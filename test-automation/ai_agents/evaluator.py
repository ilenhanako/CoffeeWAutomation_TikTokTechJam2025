import base64
from io import BytesIO
import json
from PIL import Image
from typing import List
from models.execution_models import EvaluationResult
from ai_agents.qwen_agent import QwenClient
from utils.statis_ui_knowledge import STATIC_UI_KB
from utils.knowledge_block import detect_app
"""- business_goal (what the user ultimately wants)"""
"""- page_source_xml (current view hierarchy)"""
class AIEvaluator:
    
    EVAL_SYSTEM_PROMPT = """You are a mobile UI outcome evaluator.

You get:
- business_goal (what the user ultimately wants)
- step_description (what this micro-step tries to do)
- expected_state_hint (what success looks like)
- last_action_args (optional, what we last tried)
- screenshot_b64 (current screenshot)

Your job:
1) Decide if THIS step_description is DONE (ok=true). 
   - Only consider the CURRENT step, not future ones.
2) If not done, propose exactly 1 minimal, actionable suggestion 
   that would help complete THIS step in the presence of the current UI.

Use business_goal ONLY to interpret blockers, Otherwise, recovery suggestions should focus on completing the current micro-step only.

NEVER suggest skipping ahead to future steps just because they are implied by the business goal.

- When deciding ok=true, point to evidence in the current UI:
  - For "open comments" success: a comment panel/sheet or input field is visible (e.g., EditText, hint "Add a comment", icons like send/submit).
  - For "typed comment": input field MUST contain non-empty user text (ignore placeholders such as "Add a comment", "Write a comment...", "Say something...") AND a send/submit button is visible. 
  - For "share": a share sheet/recipient list is visible.
  - For "liked": the like button is in the "on" state.
- If evidence is ambiguous or missing, set ok=false.
- Use the screenshot, ui_xml_excerpt, AND static_ui_hints (if present) for verification.
- static_ui_hints may include typical absolute locations of common controls for the current app/screen size.

Critically distinguish:
- REQUIRED GATES (e.g., Login, Account creation, OS permission dialogs like Camera/Microphone/Photos): these must be satisfied to progress if they are relevant to the task. Do NOT dismiss them. Return recovery "REQUIRE_AUTH" or "GRANT_PERMISSION" with concrete suggestions (e.g., "Tap 'Log in'", "Tap 'Allow while using the app'").
- DISTRACTIONS (ads/interstitials/upsells/unrelated modals): return "HANDLE_INTERRUPT" with suggestions to close or skip.
- If recovery="HANDLE_INTERRUPT" (ads/upsell/modals), prioritize 1–2 suggestions that directly DISMISS/CLOSE the obstruction (e.g., "Tap ×", "Tap Close", "Tap Skip"). Do not mix navigation actions (scroll/swipe) unless you also provide a direct close action first.

Infer required capability from the goal/step: 
- commenting/posting/liking/sharing/following → likely requires auth
- recording/taking photo/scanning → likely needs camera/mic permission
- uploading/picking photo → likely needs gallery/photos permission

"Suggestions MUST be concrete tappable/typable actions, not advice. Prefer imperative forms that the agent can execute directly, e.g.: "
"- \"Type 'Great picture!'\" (not \"ensure you typed\") "
"- \"Tap 'Send'\" "
"If the goal implies a text field (comment/post/search) and no text is present, include a 'Type ...' suggestion with a short default."

Output strictly in JSON with fields:
{
  "ok": boolean,
  "recovery": one of ["NONE","REDO_STEP","HANDLE_INTERRUPT","REQUIRE_AUTH","GRANT_PERMISSION","REPLAN","ABORT"],
  "reason": string,
  "suggestions": [string, ...],
  "gate_type": one of ["NONE","AUTH","PERMISSION","AD_OR_OTHER"],
  "confidence": number
}
If ok=true, set recovery="NONE" and suggestions=[].
"""
    
    def __init__(self):
        self.client = QwenClient()
    
    def evaluate_step_outcome(self, business_goal: str, step_description: str,
                             expected_state_hint: str, last_action_args: dict,
                             page_source_xml: str, screenshot_b64: str) -> EvaluationResult:
        static_hints = self._build_static_hints_for_eval("tiktok", screenshot_b64, business_goal, step_description)
        
        user_payload = {
            "business_goal": business_goal,
            "step_description": step_description,
            "expected_state_hint": expected_state_hint,
            "last_action_args": last_action_args,
            # "ui_xml_excerpt": page_source_xml[:120000], 
            "static_ui_hints": static_hints
        }
        
        messages = [
            {"role": "system", "content": [{"type": "text", "text": self.EVAL_SYSTEM_PROMPT}]},
            {"role": "user", "content": [
                {"type": "text", "text": json.dumps(user_payload, ensure_ascii=False)},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_b64}"}}
            ]}
        ]
        
        try:
            raw = self.client.chat_completion(messages, temperature=0.1)
            
            
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.strip().startswith("json"):
                    raw = raw.split("\n", 1)[1]
            
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
               
                import re
                match = re.search(r"\{[\s\S]*\}", raw)
                if match:
                    data = json.loads(match.group(0))
                else:
                    data = {
                        "ok": False,
                        "reason": "parse_error",
                        "recovery": "REDO_STEP",
                        "suggestions": []
                    }
            
            return EvaluationResult(
                ok=bool(data.get("ok", False)),
                reason=str(data.get("reason", "")),
                recovery=str(data.get("recovery", "REDO_STEP")),
                suggestions=list(data.get("suggestions", [])),
                gate_type=data.get("gate_type", "NONE"),
                confidence=float(data.get("confidence", 0.0)),
            )
            
        except Exception as e:
            return EvaluationResult(
                ok=False,
                reason=f"Evaluation error: {str(e)}",
                recovery="REDO_STEP",
                suggestions=[],
                gate_type="NONE",
                confidence=0.0
            )
        
    # def _build_static_hints_for_eval(self, app: str, screenshot_b64: str, goal: str, step_desc: str) -> str:
    #     # get W,H from b64 to make absolute coordinates
    #     try:
    #         img = Image.open(BytesIO(base64.b64decode(screenshot_b64.split(",")[-1]))).convert("RGB")
    #         W, H = img.size
    #     except Exception:
    #         W, H = 1080, 1920

    #     app_key = detect_app(app or "", "", "")  # e.g., "tiktok"
    #     kb = STATIC_UI_KB.get(app_key, {})
    #     # lightweight intent guess
    #     uq = f"{goal} {step_desc}".lower()
    #     intents = []
    #     for k in ("comment","comments","like","share","profile","mute","close","reply"):
    #         if k in uq:
    #             intents.append("comment" if k=="comments" else k)
    #     if not intents:
    #         intents = ["comment","like","share","close"]

    #     lines = [f"STATIC_UI_HINTS app={app_key} size={W}x{H}"]
    #     for key in intents:
    #         node = kb.get(key)
    #         if not node: 
    #             continue
    #         abs_pts = [f"({int(x*W)},{int(y*H)})" for (x,y) in node.get("pos", [])]
    #         lines.append(f"- {key}: {node.get('desc','')} | typical {', '.join(abs_pts)}")
    #     # A tiny policy: presence of right-rail speech bubble means "comment button is available" (not same as "comments open")
    #     lines.append("Heuristic: On short-video feeds, a speech-bubble at right-rail typical coords implies the comment BUTTON is present,")
    #     lines.append("but SUCCESS for 'open comments' requires the comment PANEL or input field to be visible.")
    #     return "\n".join(lines)

    def _build_static_hints_for_eval(self, app: str, screenshot_b64: str, goal: str, step_desc: str) -> str:
        try:
            img = Image.open(BytesIO(base64.b64decode(screenshot_b64.split(",")[-1]))).convert("RGB")
            W, H = img.size
        except Exception:
            W, H = 1080, 1920

        app_key = detect_app(app or "", "", "")  # e.g., "tiktok"
        kb = STATIC_UI_KB.get(app_key, {})

        # only use step_description for intent guessing
        uq = step_desc.lower()
        intents = []
        for k in ("comment","comments","like","share","profile","mute","close","reply"):
            if k in uq:
                intents.append("comment" if k=="comments" else k)

       
        # if not intents:
        #     intents = ["like","share","close"]

        lines = [f"STATIC_UI_HINTS app={app_key} size={W}x{H}"]
        for key in intents:
            node = kb.get(key)
            if not node: 
                continue
            abs_pts = [f"({int(x*W)},{int(y*H)})" for (x,y) in node.get("pos", [])]
            lines.append(f"- {key}: {node.get('desc','')} | typical {', '.join(abs_pts)}")

        # heuristic about comment button vs panel — only add if step is about comments
        if "comment" in intents:
            lines.append("Heuristic: On short-video feeds, a speech-bubble at right-rail typical coords implies the comment BUTTON is present,")
            lines.append("but SUCCESS for 'open comments' requires the comment PANEL or input field to be visible.")

        return "\n".join(lines)
