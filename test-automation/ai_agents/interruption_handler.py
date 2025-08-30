
import json
import re
import time
from typing import Callable, List, Optional, Tuple
from models.execution_models import Interruption


class InterruptionGuard:
    # Heuristics / cues
    DIALOG_CLASSES = {
        "android.app.Dialog",
        "androidx.appcompat.app.AlertDialog",
        "android.widget.PopupWindow$PopupDecorView",
        "com.google.android.material.bottomsheet.BottomSheetDialog"
    }
    CLOSE_TEXTS = {"close", "skip", "not now", "no thanks", "cancel", "dismiss", "x"}
    AD_HINTS = {"ad", "advert", "sponsored", "promo", "offer", "upgrade", "try premium"}
    LOGIN_HINTS = {"sign in", "log in", "continue with", "google", "facebook", "apple"}
    PERMISSION_HINTS = {"allow", "deny", "while using the app", "only this time"}

    def __init__(
        self,
        llm_client_factory: Callable[[], object],
        execute_with_retry: Callable[[dict, object, int, float], dict],
        normalize_mobile_action: Callable[[str], str],
        allowlist_steps: Optional[List[str]] = None,
        blocklist_ids: Optional[List[str]] = None,
    ):

        self._client_factory = llm_client_factory
        self._execute_with_retry = execute_with_retry
        self._normalize_mobile_action = normalize_mobile_action
        self.allowlist_steps = set([s.lower() for s in (allowlist_steps or [])])
        self.blocklist_ids = set([s.lower() for s in (blocklist_ids or [])])

    # ---------- utils ----------
    @staticmethod
    def _parse_bounds(b: str) -> Tuple[int,int,int,int]:
        m = re.findall(r"\[(\d+),(\d+)\]", b or "")
        if len(m) == 2:
            (x1,y1),(x2,y2) = m
            return int(x1),int(y1),int(x2),int(y2)
        return (0,0,0,0)

    @staticmethod
    def _node_text(n: dict) -> str:
        return " ".join([
            (n.get("text") or ""), 
            (n.get("content-desc") or ""), 
            (n.get("resource-id") or "")
        ]).lower()

    def _classify_text(self, s: str) -> str:
        t = (s or "").lower()
        if any(w in t for w in self.PERMISSION_HINTS): return "permission"
        if any(w in t for w in self.LOGIN_HINTS): return "login"
        if any(w in t for w in self.AD_HINTS): return "ad"
        return "unknown"

    # ---------- detection ----------
    def detect(self, driver, screen_w: int, screen_h: int) -> Interruption:
        xml = driver.page_source
        nodes = re.findall(
            r'class="([^"]+)"[^>]*?bounds="([^"]+)"[^>]*?(?:text="([^"]*)")?[^>]*?(?:content-desc="([^"]*)")?[^>]*?(?:resource-id="([^"]*)")?',
            xml
        )
        candidates = []
        max_cover = 0.0

        # classes that are common layout containers; ignore unless strong cues
        LAYOUT_CLASSES = {
            "android.view.ViewGroup", "android.widget.FrameLayout",
            "android.widget.LinearLayout", "android.widget.RelativeLayout",
            "androidx.recyclerview.widget.RecyclerView", "androidx.viewpager.widget.ViewPager",
            "androidx.viewpager2.widget.ViewPager2"
        }

        # a “central area” rectangle; if an overlay doesn't intersect this, it's less likely to block
        cx1 = int(screen_w * 0.2); cy1 = int(screen_h * 0.15)
        cx2 = int(screen_w * 0.8); cy2 = int(screen_h * 0.85)

        for cls, bounds, text, desc, resid in nodes:
            x1,y1,x2,y2 = self._parse_bounds(bounds)
            area = max(1,(x2-x1)) * max(1,(y2-y1))
            cover = area / max(1, (screen_w*screen_h))
            label = " ".join([(text or ""), (desc or ""), (resid or "")]).lower()

            # probe nearby attributes for clickability/focusability/scrollable flags
            around_start = max(0, xml.find(bounds) - 200)
            around_end   = xml.find(bounds) + 200
            window = xml[around_start:around_end]
            clickable  = 'clickable="true"'  in window
            focusable  = 'focusable="true"'  in window
            scrollable = 'scrollable="true"' in window

        
            intersects_center = not (x2 < cx1 or x1 > cx2 or y2 < cy1 or y1 > cy2)

            # Strong cues
            has_cue = any(k in label for k in (self.AD_HINTS | self.LOGIN_HINTS | self.PERMISSION_HINTS)) \
                    or any((resid or "").lower().find(b) >= 0 for b in self.blocklist_ids)

           
            likely_modal = (cls in self.DIALOG_CLASSES) or (cover > 0.60)

            big_interactive_overlay = (cover > 0.33 and (clickable or focusable) and (not scrollable) and intersects_center)

            # Filter out generic layout containers unless they have strong cues or are huge
            is_generic_layout = cls in LAYOUT_CLASSES
            allow_generic = (has_cue or likely_modal)

            if likely_modal or has_cue or (big_interactive_overlay and (not is_generic_layout or allow_generic)):
                candidates.append({
                    "class": cls,
                    "bounds": (x1,y1,x2,y2),
                    "text": text or "",
                    "content-desc": desc or "",
                    "resource-id": resid or "",
                    "coverage": cover
                })
                max_cover = max(max_cover, cover)

        if not candidates:
            # System alert (permissions, etc.)
            try:
                alert = driver.switch_to.alert
                _ = alert.text
                return Interruption(True, kind="permission", coverage=0.6, nodes=[], screenshot_path=None)
            except Exception:
                return Interruption(False)

        # classify kind for the best set
        kind_votes = [self._classify_text(self._node_text(n)) for n in candidates]
        kind = max(kind_votes, key=kind_votes.count) if kind_votes else "unknown"
        return Interruption(True, kind=kind, coverage=max_cover, nodes=candidates)

    def decide(self, interruption: Interruption, business_goal: str, current_step: str, xml: str, screenshot_b64: str) -> dict:
        if not interruption.present:
            return {"decision":"PASS_THROUGH","rationale":"No interruption","actions":[]}

        step_l = (current_step or "").lower()
        if any(w in step_l for w in self.allowlist_steps) and interruption.kind in {"permission","login"}:
            return {"decision":"HANDLE", "rationale":"Allowlisted step requires it", "actions":[]}

        client = self._client_factory()

        prompt = f"""
You are assisting a mobile UI test. Business goal: "{business_goal}".
Current step: "{current_step}"

We detected a possible popup/overlay. Decide:
- PASS_THROUGH if it doesn't block or matter.
- DISMISS if it blocks but is irrelevant (ads, upsells, rate apps).
- HANDLE if it's relevant/required to proceed (permissions needed for this step, required login wall if this step needs logged-in features).

Return STRICT JSON with fields:
- decision: PASS_THROUGH | DISMISS | HANDLE
- rationale: short sentence
- actions: list of tool calls using only: click, long_press, swipe, type, key, wait.
  Prefer safe selectors (text/content-desc/resource-id). Use coordinates ONLY if needed.

Be conservative and avoid risky clicks.
"""
        messages = [
            {"role":"system","content":[{"type":"text","text":"You are a careful mobile test interruption triager."}]},
            {"role":"user","content":[
                {"type":"image_url","image_url":{"url": f"data:image/png;base64,{screenshot_b64}"}},
                {"type":"text","text": "UI XML:\n"+ xml[:120000]},
                {"type":"text","text": prompt}
            ]}
        ]
        out = client.chat.completions.create(
            model="qwen2.5-vl-7b-instruct",
            messages=messages,
            temperature=0.2,
            max_tokens=700
        ).choices[0].message.content

        try:
            j = json.loads(out[out.find("{"):out.rfind("}")+1])
            if j.get("decision") not in {"PASS_THROUGH","DISMISS","HANDLE"}:
                j["decision"] = "PASS_THROUGH"
            j["actions"] = j.get("actions", [])
            return j
        except Exception:
            return {"decision":"PASS_THROUGH","rationale":"Parse error, default to pass-through","actions":[]}


    def _normalize_and_call(self, act: dict, mobile_use, resized_w: int, resized_h: int, orig_w: int, orig_h: int):
        if isinstance(act, str):
            act = {"action": act}
        elif not isinstance(act, dict):
      
            act = {"action": "click"}
    
        args = {"action": self._normalize_mobile_action(act.get("action","click"))}
        if "text" in act: args["text"] = act["text"]
        if "content_desc" in act: args["content-desc"] = act["content_desc"]
        if "resource_id" in act: args["resource-id"] = act["resource_id"]
        if "coordinate" in act:
            x,y = act["coordinate"]
            args["coordinate"] = [
                int((x / max(1,resized_w)) * orig_w),
                int((y / max(1,resized_h)) * orig_h)
            ]
        return self._execute_with_retry(args, mobile_use, retries=2, delay=1.0)

    def handle(self, driver, mobile_use, interruption: Interruption, decision: dict,
               resized_w: int, resized_h: int, orig_w: int, orig_h: int) -> bool:
        # quick deterministic dismiss if blocklisted id present
        for n in (interruption.nodes or []):
            rid = (n.get("resource-id") or "").lower()
            if any(b in rid for b in self.blocklist_ids):
                x1,y1,x2,y2 = n["bounds"]
                cx = int(x2 - (x2-x1)*0.05)
                cy = int(y1 + (y2-y1)*0.08)
                _ = self._execute_with_retry({"action":"click","coordinate":[cx,cy]}, mobile_use, retries=2, delay=0.8)

        attempts = 0
        for a in decision.get("actions", []):
            attempts += 1
            if attempts > 3:
                break
            self._normalize_and_call(a, mobile_use, resized_w, resized_h, orig_w, orig_h)
            time.sleep(0.8)

        size = driver.get_window_size()
        again = self.detect(driver, size["width"], size["height"])
        return not again.present
