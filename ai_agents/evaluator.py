import json
from typing import List
from models.execution_models import EvaluationResult
from ai_agents.qwen_agent import QwenClient

class AIEvaluator:
    
    EVAL_SYSTEM_PROMPT = """You are a mobile UI outcome evaluator.

You get:
- business_goal (what the user ultimately wants)
- step_description (what this micro-step tries to do)
- expected_state_hint (what success looks like)
- last_action_args (optional, what we last tried)
- page_source_xml (current view hierarchy)
- screenshot_b64 (current screenshot)

Your job:
1) Decide if the step is DONE (ok=true).
2) If not done, pick the best recovery and propose 1–3 minimal, actionable suggestions.

- When deciding ok=true, point to evidence in the current UI:
  - For "open comments" success: a comment panel/sheet or input field is visible (e.g., EditText, hint "Add a comment", icons like send/submit).
  - For "typed comment": input field contains text and send/submit is available.
  - For "share": a share sheet/recipient list is visible.
  - For "liked": the like button is in the "on" state.
- If evidence is ambiguous or missing, set ok=false.
- Use both screenshot+bounds hints AND ui_xml_excerpt for verification.

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
        
        user_payload = {
            "business_goal": business_goal,
            "step_description": step_description,
            "expected_state_hint": expected_state_hint,
            "last_action_args": last_action_args,
            "ui_xml_excerpt": page_source_xml[:120000],  # Cap to keep requests reasonable
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
            print(f"Error in step evaluation: {e}")
            return EvaluationResult(
                ok=False,
                reason=f"Evaluation error: {str(e)}",
                recovery="REDO_STEP",
                suggestions=[],
                gate_type="NONE",
                confidence=0.0
            )