
import time
from typing import Optional, List
from models.execution_models import ActionResult

class DemoCoordinator:
    
    DEMO_COORDINATES = {
        "like_button": [1009, 932],
        "comment_button": [1009, 1154],
        "share_button": [1009, 1354],
        "mute_button": [1009, 1576],
        "close_button": [1042, 133],
        "home_button": [108, 2020],
        "search_button": [324, 2020],
        "upload_button": [540, 2020],
        "inbox_button": [756, 2020],
        "profile_button": [972, 2020],
        "send": [982, 2064],
        "submit": [982, 2064],
        "text_field": [540, 2042],
        "comment_text_field": [540, 2042],
        "send_button": [982, 2064],
        "video_play_area": [540, 1110],
    }
    
    def __init__(self, mobile_use, execute_with_retry_func):
        self.mobile_use = mobile_use
        self.execute_with_retry = execute_with_retry_func
    
    def should_use_demo_mode(self, step_description: str) -> bool:

        intent = self._extract_intent_from_step(step_description)
        return intent is not None
    
    def execute_demo_action(self, step_description: str) -> Optional[ActionResult]:
     
        
        intent = self._extract_intent_from_step(step_description)
        if not intent:
            return None
        
        print(f"[DEMO MODE] Detected intent: {intent}")
        
        action_map = {
            "comment": "comment_button",
            "like": "like_button", 
            "share": "share_button",
            # "close": "close_button",
            "video_tap": "video_play_area",
            "type_comment": "comment_text_field"
        }
        
       
        if intent in ["scroll_up", "scroll_down"]:
            return self._execute_hardcoded_scroll(intent)
        
        #
        coord_key = action_map.get(intent)
        if coord_key and coord_key in self.DEMO_COORDINATES:
            coordinate = self.DEMO_COORDINATES[coord_key]
            
            if intent == "type_comment":
        
                return self._execute_hardcoded_text_input(coordinate)
            else:
              
                return self._execute_hardcoded_click(coordinate, intent)
        
        return None
    
    def _extract_intent_from_step(self, step_description: str) -> Optional[str]:
       
        step_lower = step_description.lower()
        
     
        intent_patterns = {
            "type_comment": ["type", "write comment", "enter text", "text field", "input field", "comment field"],
            "comment": ["comment button", "speech bubble", "comment", "bubble icon"],
            "like": ["like", "heart", "like button"],
            "share": ["share", "share button", "arrow"],
            # "close": ["close", "dismiss", "x button", "cancel"],
            "video_tap": ["tap on it to play", "video", "play"],
            "scroll_up": ["scroll up", "swipe up"],
            "scroll_down": ["scroll down", "swipe down"],
        }
        
        for intent, patterns in intent_patterns.items():
            if any(pattern in step_lower for pattern in patterns):
                return intent
        
        return None
    
    def _execute_hardcoded_scroll(self, direction: str) -> ActionResult:

        # Screen center for scroll
        center_x = 540  # Middle of 1080px screen
        
        if direction == "scroll_up":
            start_y = 1400
            end_y = 800
        else:  # scroll_down
            start_y = 800  
            end_y = 1400
            
        action_args = {
            "action": "swipe",
            "coordinate": [center_x, start_y],
            "coordinate2": [center_x, end_y]
        }
        
        print(f"[DEMO MODE] Executing hardcoded {direction}")
        result = self.execute_with_retry(action_args, self.mobile_use, retries=2, delay=0.5)
        
        return ActionResult(
            status=result.get("status", "unknown"),
            metadata={"demo_mode": True, "action": direction}
        )
    
    def _execute_hardcoded_text_input(self, coordinate: List[int]) -> ActionResult:
     
        click_result = self._execute_hardcoded_click(coordinate, "text_field")
        
        if click_result.status == "success":
            # Wait a moment, then type
            time.sleep(0.5)
            
            demo_text = "Great video! 🔥" 
            type_result = self.mobile_use.call({
                "action": "type", 
                "text": demo_text
            })
            
            return ActionResult(
                status=type_result.get("status", "unknown"),
                metadata={
                    "demo_mode": True, 
                    "text_typed": demo_text,
                    "coordinate_used": coordinate
                }
            )
        
        return click_result
    
    def _execute_hardcoded_click(self, coordinate: List[int], intent: str) -> ActionResult:
    
        action_args = {
            "action": "click",
            "coordinate": coordinate
        }
        
        print(f"[DEMO MODE] Clicking {intent} at hardcoded coordinate: {coordinate}")
        result = self.execute_with_retry(action_args, self.mobile_use, retries=2, delay=0.5)
        
        if result.get("status") == "success":
            print(f"[DEMO MODE] Successfully clicked {intent}")
        else:
            print(f"[DEMO MODE] Failed to click {intent}")
        
        return ActionResult(
            status=result.get("status", "unknown"),
            metadata={
                "demo_mode": True, 
                "intent": intent,
                "coordinate_used": coordinate
            }
        )