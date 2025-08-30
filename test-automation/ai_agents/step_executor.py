import time
from typing import Dict, List
from PIL import Image

from models.execution_models import ExecutorStep, ProcessorConfig, ActionResult
from core.driver_manager import DriverManager
from core.screenshot_manager import ScreenshotManager
from .action_processor import ActionProcessor
from .interruption_handler import InterruptionGuard
from .evaluator import AIEvaluator
from utils.coordinates_utils import CoordinateUtils
from qwen_vl_utils import smart_resize

class StepExecutor:
    
    def __init__(self, driver_manager: DriverManager, action_processor: ActionProcessor,
                 guard: InterruptionGuard, processor_config: ProcessorConfig):
        self.driver_manager = driver_manager
        self.action_processor = action_processor
        self.guard = guard
        self.processor = processor_config
        self.evaluator = AIEvaluator()
        self.screenshot_manager = ScreenshotManager()
    
    def execute_step_with_guard(self, business_goal: str, step: ExecutorStep, 
                               screenshot_path: str, max_cycles: int = 3) -> bool:
        driver = self.driver_manager.get_driver()
        
        # Get image dimensions for coordinate normalization
        dummy_img = Image.open(screenshot_path)
        orig_w, orig_h = dummy_img.size
        
        resized_h, resized_w = smart_resize(
            dummy_img.height, dummy_img.width,
            factor=self.processor.patch_size * self.processor.merge_size,
            min_pixels=self.processor.min_pixels,
            max_pixels=self.processor.max_pixels,
        )
        
        def _evaluate_now():
            shot = self.screenshot_manager.take_screenshot(driver)
            b64 = self.screenshot_manager.encode_image(shot)
            xml_after = self.driver_manager.get_page_source()
            return shot, self.evaluator.evaluate_step_outcome(
                business_goal=business_goal,
                step_description=getattr(step, "description", ""),
                expected_state_hint=self._get_expected_hint_from_step(step),
                last_action_args={
                    "action_type": getattr(step, "action_type", None),
                    "qwen_query": getattr(step, "query_for_qwen", None)
                },
                page_source_xml=xml_after,
                screenshot_b64=b64,
            )
        
        
        for cycle in range(1, max_cycles + 1):
            print(f"Step cycle {cycle}/{max_cycles}")
            # --- PRE-CHECK: is step already satisfied? ---
            shot = self.screenshot_manager.take_screenshot(driver)
            b64 = self.screenshot_manager.encode_image(shot)
            xml = self.driver_manager.get_page_source()
            pre_eval = self.evaluator.evaluate_step_outcome(
                business_goal,
                getattr(step, "description", ""),
                self._get_expected_hint_from_step(step),
                {},
                xml,
                b64,
            )
            if pre_eval.ok:
                print("✅ Step already satisfied, skipping execution.")
                return True
            
            # 1) Execute the step
            self.action_processor.execute_enhanced_xml_first(
                screenshot_path, step.query_for_qwen
            )
            time.sleep(0.2)
            
            # 2) Evaluate outcome
            post_shot, eval_res = _evaluate_now()
            print(f"Evaluator verdict: ok={eval_res.ok} recovery={eval_res.recovery} reason={eval_res.reason}")
            
            if eval_res.suggestions:
                for s in eval_res.suggestions[:4]:
                    print(f"   Suggestion: {s}")
            
            if eval_res.ok:
                return True
            
            # 3) Handle recovery based on evaluation
            if not self._handle_recovery(eval_res, driver, step, business_goal, post_shot, 
                                       resized_w, resized_h, orig_w, orig_h):
                if cycle < max_cycles:
                    continue
                else:
                    break
        
        print("Max cycles reached without success.")
        return False
    
    def _handle_recovery(self, eval_res, driver, step, business_goal, screenshot_path,
                        resized_w, resized_h, orig_w, orig_h) -> bool:
        recovery = (eval_res.recovery or "").upper()
        
        if recovery == "GRANT_PERMISSION":
            print("Permission gate detected — attempting to grant required permission.")
            success = self._handle_permission_gate(driver, step)
            if success:
                time.sleep(0.4)
                new_shot = self.screenshot_manager.take_screenshot(driver)
                self.action_processor.process_screenshot_with_qwen(new_shot, step.query_for_qwen)
                return True
            return False
        
        elif recovery == "REDO_STEP":
            print("Re-doing the step.")
            if eval_res.suggestions:
                self._actionize_suggestions(driver, eval_res.suggestions, step.query_for_qwen)
            time.sleep(0.2)
            return True  # Continue to next cycle
        
        elif recovery == "HANDLE_INTERRUPT":
            print("Interruption suspected; attempting guard.handle and retry.")
            return self._handle_interruption(driver, business_goal, step, screenshot_path, 
                                           resized_w, resized_h, orig_w, orig_h, eval_res)
        
        elif recovery == "REQUIRE_AUTH":
            print("Authentication required.")
            success = self._handle_require_auth(driver, business_goal, step, eval_res)
            if success:
                time.sleep(0.4)
                new_shot = self.screenshot_manager.take_screenshot(driver)
                self.action_processor.process_screenshot_with_qwen(new_shot, step.query_for_qwen)
                return True
            return False
        
        elif recovery == "REPLAN":
            print("UI drift detected — quick micro-replan and retry.")
            self._quick_replan_and_retry(driver, step)
            time.sleep(0.2)
            return True
        
        elif recovery == "ABORT":
            print(f"Abort advised by evaluator. Reason: {eval_res.reason}")
            return False
        
        if eval_res.suggestions:
            self._actionize_suggestions(driver, eval_res.suggestions, step.query_for_qwen)
            time.sleep(0.2)
            return True
        
        return False
    
    def _handle_permission_gate(self, driver, step) -> bool:
        xml = self.driver_manager.get_page_source()
        mobile_use = self.action_processor.mobile_use
        
        # Common permission dialog selectors
        allow_selectors = [
            {"text": "Allow while using the app"},
            {"text": "Allow only this time"},
            {"text": "Allow once"},
            {"text": "Allow"},
            {"content_desc": "Allow"},
            {"resource_id": "android:id/button1"},
            {"resource_id": "com.android.permissioncontroller:id/permission_allow_button"},
        ]
        
        from utils.xml_parser import XMLParser
        
        for sel in allow_selectors:
            coord = XMLParser.find_by_selector(
                xml, 
                text=sel.get("text"), 
                content_desc=sel.get("content_desc"), 
                resource_id=sel.get("resource_id")
            )
            if coord:
                result = self.action_processor.execute_with_retry(
                    {"action": "click", "coordinate": coord}, 
                    mobile_use
                )
                if result.get("status") == "success":
                    time.sleep(0.3)
                    return True
        
        return False
    
    def _handle_interruption(self, driver, business_goal, step, screenshot_path,
                           resized_w, resized_h, orig_w, orig_h, eval_res) -> bool:
        size = self.driver_manager.get_screen_size()
        intr = self.guard.detect(driver, size["width"], size["height"])
        
        if intr.present:
            b64_now = self.screenshot_manager.encode_image(screenshot_path)
            decision = self.guard.decide(intr, business_goal, step.description, 
                                       self.driver_manager.get_page_source(), b64_now)
            normalized_decision = []
            if isinstance(decision, str):
                # Wrap natural-language suggestion
                normalized_decision.append({"action": "query", "query": decision})
            elif isinstance(decision, dict):
                normalized_decision.append(decision)
            elif isinstance(decision, list):
                for d in decision:
                    if isinstance(d, str):
                        normalized_decision.append({"action": "query", "query": d})
                    elif isinstance(d, dict):
                        normalized_decision.append(d)
            
            ok = self.guard.handle(driver, self.action_processor.mobile_use, intr, normalized_decision,
                                 resized_w, resized_h, orig_w, orig_h)
            if ok:
                time.sleep(0.4)
                return True
        
        # Fallback: try suggestions or corner closes
        if eval_res.suggestions:
            self._actionize_suggestions(driver, eval_res.suggestions, "close ad")
        else:
            self._try_corner_closes(driver)
        
        time.sleep(0.3)
        return True
    
    def _actionize_suggestions(self, driver, suggestions: List[str], fallback_query: str = None):
        shot = self.screenshot_manager.take_screenshot(driver)
        for suggestion in (suggestions or []):
            if isinstance(suggestion, str):
                query = suggestion.strip() or fallback_query
                if query:
                    print(f"Following suggestion: {query}")
                    # send to Qwen pipeline instead of raw to guard
                    self.action_processor.execute_enhanced_xml_first(shot, query)
                    time.sleep(0.25)
            elif isinstance(suggestion, dict):
                # Already structured
                self.action_processor.execute_with_retry(suggestion, self.action_processor.mobile_use)
        
    def _try_corner_closes(self, driver, attempts: int = 3) -> bool:
        #Try clicking common close button locations
        size = self.driver_manager.get_screen_size()
        w, h = size["width"], size["height"]
        
        candidates = [
            (int(w * 0.97), int(h * 0.03)),  # top-right
            (int(w * 0.95), int(h * 0.07)),
            (int(w * 0.05), int(h * 0.05)),  # top-left
            (int(w * 0.50), int(h * 0.92)),  # bottom-center
        ]
        
        mobile_use = self.action_processor.mobile_use
        for i, (x, y) in enumerate(candidates[:attempts]):
            result = self.action_processor.execute_with_retry(
                {"action": "click", "coordinate": [x, y]}, 
                mobile_use, retries=1, delay=0.1
            )
            if result.get("status") == "success":
                time.sleep(0.2)
                return True
        return False
    
    def _handle_require_auth(self, driver, business_goal, step, eval_res) -> bool:
        if eval_res.suggestions:
            self._actionize_suggestions(driver, eval_res.suggestions, "Sign in")
            return True
        return False
    
    def _quick_replan_and_retry(self, driver, step):
        shot = self.screenshot_manager.take_screenshot(driver)
        print("Quick replan: retrying with fresh perception...")
        self.action_processor.process_screenshot_with_qwen(shot, step.query_for_qwen)
        time.sleep(0.2)
    
    def _get_expected_hint_from_step(self, step) -> str:
        if getattr(step, "expected_state", None):
            return step.expected_state
        
        desc = (getattr(step, "description", "") or "").lower()
        if "comment" in desc:
            return "Comment UI visible (input field or comments list present)"
        if step.action_type in ("click", "tap"):
            return "Target element reflects clicked state or expected screen appears"
        if step.action_type in ("type", "input"):
            return "Text field contains newly entered text and the send/submit button is enabled"
        if step.action_type in ("swipe", "scroll"):
            return "Content position changed in scrollable region"
        
        return "Screen reflects successful completion of the described step"