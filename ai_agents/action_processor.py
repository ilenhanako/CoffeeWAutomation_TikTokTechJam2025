import json
import random
import time
import difflib
from typing import Dict, List, Any, Optional
from PIL import Image
from qwen_agent.llm.fncall_prompts.nous_fncall_prompt import NousFnCallPrompt, Message, ContentItem
from IPython.display import display

from core.driver_manager import DriverManager
from core.screenshot_manager import ScreenshotManager
from ai_agents.qwen_agent import QwenClient
from utils.xml_parser import XMLParser
from utils.coordinates_utils import CoordinateUtils
from models.execution_models import ActionResult
from config.settings import config
from qwen_vl_utils import smart_resize
from tools.mobile_tool import MobileUse
from models.execution_models import ProcessorConfig
from utils.knowledge_block import build_static_knowledge_block, detect_app
class ActionProcessor:
    
    VALID_MOBILE_ACTIONS = {
        'key', 'click', 'long_press', 'swipe', 'type', 
        'system_button', 'open', 'wait', 'terminate'
    }
    
    ACTION_MAPPINGS = {
        'left_click': 'click', 'right_click': 'click', 'tap': 'click',
        'touch': 'click', 'press': 'click', 'single_click': 'click',
        'double_click': 'click', 'double_tap': 'click',
        'long_click': 'long_press', 'hold': 'long_press',
        'press_and_hold': 'long_press', 'long_tap': 'long_press',
        'scroll': 'swipe', 'drag': 'swipe', 'slide': 'swipe', 'flick': 'swipe',
        'input': 'type', 'enter': 'type', 'write': 'type', 'text': 'type',
        'keypress': 'key', 'key_press': 'key', 'button': 'key',
        'launch': 'open', 'start': 'open', 'run': 'open',
        'sleep': 'wait', 'pause': 'wait', 'delay': 'wait',
        'stop': 'terminate', 'end': 'terminate', 'finish': 'terminate',
    }
    
    COORD_ACTIONS = {"click", "long_press", "swipe"}
    
    def __init__(self, driver_manager: DriverManager, mobile_use: MobileUse, qwen_client: QwenClient, demo_coordinator=None):
        self.driver_manager = driver_manager
        self.mobile_use = mobile_use
        self.qwen_client = qwen_client
        self.screenshot_manager = ScreenshotManager()
        self.processor_config = ProcessorConfig()
        self.coord= CoordinateUtils()
        self.demo_coordinator = demo_coordinator
    
    def execute_enhanced_xml_first(self, screenshot_path: str, user_query: str) -> ActionResult:
        driver = self.driver_manager.get_driver()
        page_source = self.driver_manager.get_page_source()
        
        # xml element
        relevant_elements = self._find_relevant_elements(page_source, user_query)
        
        
        # mobile_use = MobileUse(
        #     cfg={
        #         "display_width_px": 1080, 
        #         "display_height_px": 1920
        #     }, 
        #     driver=driver
        # )
        mobile_use= self.mobile_use
        
        if len(relevant_elements) == 1:
            print("XML-first: Found single matching element.")
            action = self._create_action_from_element(relevant_elements[0])
            result = self.execute_with_retry(action["arguments"], mobile_use, retries=3, delay=1.5)
            return ActionResult(status=result.get("status", "unknown"), metadata=result)
        
        if len(relevant_elements) > 1:
            print(f"XML-first: {len(relevant_elements)} candidates found, invoking vision disambiguation...")
            action = self._vision_model_disambiguate(screenshot_path, relevant_elements, user_query)
            if action:
                result = self.execute_with_retry(action["arguments"], mobile_use, retries=3, delay=1.5)
                return ActionResult(status=result.get("status", "unknown"), metadata=result)
        
        # Fallback to full Qwen pipeline
        print("XML-first: No match found, falling back to Qwen pipeline.")
        return self.process_screenshot_with_qwen(screenshot_path, user_query)
    
    def process_screenshot_with_qwen(self, screenshot_path: str, user_query: str) -> ActionResult:
        if self.demo_coordinator and self.demo_coordinator.should_use_demo_mode(user_query):
            demo_result = self.demo_coordinator.execute_demo_action(user_query)
            if demo_result:
                return demo_result
        
        driver = self.driver_manager.get_driver()
        page_source = self.driver_manager.get_page_source()
        
        MAX_XML = 120_000
        page_source_trimmed = page_source[:MAX_XML]
    
        processor = self.processor_config
        
        dummy_image = Image.open(screenshot_path)
        original_width, original_height = dummy_image.size
        
        resized_height, resized_width = smart_resize(
            dummy_image.height,
            dummy_image.width,
            factor=processor.patch_size * processor.merge_size,
            min_pixels=processor.min_pixels,
            max_pixels=processor.max_pixels,
        )
        
        mobile_use = MobileUse(cfg={"display_width_px": resized_width, "display_height_px": resized_height}, driver=driver)
        

        strict_rule = (
            "You MUST call the tool with ONE function call only, using exactly one of: "
            "click, long_press, swipe, type, key, system_button, open, wait, terminate. "
            "Do NOT output any thoughts, analysis, or plain text. Do NOT prefix with 'Thought:'. "
            "Wrap the function call inside <tool_call>{...}</tool_call> or output pure JSON only. "
            "For 'type' actions you MUST include a 'text' string to input."
            "For 'type' actions, you must first click on the field before suggesting the step to type. "
            "If the step or business goal implies commenting/posting/searching, ALWAYS produce a 'type' action with a text string."
            " e.g., 'Great picture!' when commenting, if no explicit text was given."
            "If needed, assume the text field is already focused. Do NOT stop at just a click."
        )
        
        tools = [{"type": "function", "function": mobile_use.function}]
        tool_choice = {"type": "function", "function": {"name": mobile_use.function["name"]}}
        
        ncp = NousFnCallPrompt()
        system_message = ncp.preprocess_fncall_messages(
            messages=[Message(role="system", content=[
                ContentItem(text="You are a mobile UI automation assistant."),
                ContentItem(text=strict_rule),
            ])],
            functions=[mobile_use.function],
            tool_choice=tool_choice,
            tools=tools,
            lang=None
        )[0].model_dump()
        
        static_block = build_static_knowledge_block(app=detect_app("tiktok"),
                                                 screenshot_path=screenshot_path,
                                                 user_query=user_query)

        base64_image = self.screenshot_manager.encode_image(screenshot_path)
        messages = [
            {"role": "system", "content": [{"type": "text", "text": msg["text"]} for msg in system_message["content"]]},
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}},
                {"type": "text", "text": "UI Hierarchy:\n" + page_source_trimmed},
                {"type": "text", "text": static_block},  # <= injected knowledge
                {"type": "text", "text": user_query}
            ]},
        ]
        
        output_text = self.qwen_client.chat_completion(messages, temperature=0.3)
        print("Model output:", output_text)
        
        try:
            if "<tool_call>" in output_text:
                action_json = output_text.split("<tool_call>\n")[1].split("\n</tool_call>")[0]
            else:
                action_json = output_text
            action = json.loads(action_json)
            print("Parsed action:", action)
            
            action = self._fix_mobile_action(action)
            print("Final normalized action:", action)
            
        except Exception as e:
            print(f"Error parsing action: {e}\nOutput was:\n{output_text}")
            return ActionResult(status="error", error=str(e))
        
        args = action.get("arguments", {})
        act = (args.get("action") or "").lower().strip()
        

        action_for_original = action.copy()
        if act in self.COORD_ACTIONS and "coordinate" in args:
            action_for_original = self.coord.normalize_action_coordinates(
                action.copy(),
                original_width, original_height,
                resized_width, resized_height
            )
        
        if act in self.COORD_ACTIONS and "coordinate" in action["arguments"]:
            box_size = int(original_width * 0.15)
            box_display = self._draw_click_box(dummy_image, action_for_original["arguments"]["coordinate"], box_size)
            display(box_display)
            
            if "arguments" in action_for_original and "coordinate" in action_for_original["arguments"]:
                original_display = self.screenshot_manager.draw_point(dummy_image, action_for_original["arguments"]["coordinate"], color="blue")
                display(original_display)
        

        if act in self.COORD_ACTIONS:
            sel_text = args.get("text")
            sel_desc = args.get("content-desc") or args.get("content_desc")
            sel_res = args.get("resource-id") or args.get("resource_id")
            
            if "coordinate" not in action_for_original["arguments"]:
                mapped = XMLParser.find_by_selector(page_source, text=sel_text, content_desc=sel_desc, resource_id=sel_res)
                if mapped:
                    action_for_original["arguments"]["coordinate"] = mapped
                    print(f"Selector mapped to coord: {mapped}")
        
        if act == "click" and "coordinate" in action_for_original["arguments"]:
            px, py = action_for_original["arguments"]["coordinate"]
            size = self.driver_manager.get_screen_size()
            snapped = self.coord.snap_to_nearest_tappable(
                px, py, page_source,
                screen_w=size["width"], screen_h=size["height"],
                max_dist_px=160,
                prefer_right_rail=True,
                right_rail_ratio=0.28,
                prefer_keywords=("comment", "comments", "like", "share", "send", "reply")
            )
            if snapped != [px, py]:
                print(f"Snapped click {(px,py)} -> {snapped}")
                action_for_original["arguments"]["coordinate"] = snapped
            
            try:
                snapped_vis = self.screenshot_manager.draw_point(dummy_image, snapped, color="yellow")
                display(snapped_vis)
            except Exception:
                pass
        

        if act == "click" and "coordinate" in action_for_original.get("arguments", {}):
            result = self._adaptive_fuzzy_click(
                self.driver_manager,
                action_for_original["arguments"],
                mobile_use,
                page_source,
                retries_each=1,
                delay_each=0.2,
            )
            return ActionResult(
                status=result.get("status", "unknown"),
                action=action_for_original,
                metadata={"action_executed": result, "action": action_for_original}
            )
        else:
            print(f"Executing action: {action_for_original}")
            result = self.execute_with_retry(
                action_for_original["arguments"],
                mobile_use,
                retries=3,
                delay=1.5
            )
            print("Final Appium result:", result)
            time.sleep(3)
            return ActionResult(
                status=result.get("status", "unknown"),
                action=action_for_original,
                metadata={"action_executed": result, "action": action_for_original}
            )
    
    def execute_with_retry(self, action_args: Dict, mobile_use, retries: int = 3, delay: float = 1.5) -> Dict:
        if isinstance(action_args, dict) and action_args.get("action") == "wait":
            sec = (action_args.get("time")
                   or action_args.get("seconds")
                   or action_args.get("duration")
                   or 0.2)
            try:
                sec = float(sec)
            except Exception:
                sec = 0.2
            print(f"Waiting for {sec} seconds (local wait).")
            time.sleep(sec)
            return {"status": "success", "waited": sec}
        
        for attempt in range(1, retries + 1):
            try:
                result = mobile_use.call(action_args)
                
                if isinstance(result, dict) and result.get("status") == "success":
                    print(f"Action succeeded on attempt {attempt}: {result}")
                    return result
                
                print(f"Attempt {attempt} failed: {result}")
            except Exception as e:
                print(f"Attempt {attempt} raised an exception: {e}")
            
            if attempt < retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
        
        print(f"Action failed after {retries} retries: {action_args}")
        return {"status": "failure", "action": action_args}
    
    
    def _adaptive_fuzzy_click(self, driver_manager, action_args, mobile_use, xml, retries_each=1, delay_each=0.25):
        if "coordinate" not in action_args:
            return self.execute_with_retry(action_args, mobile_use, retries=retries_each, delay=delay_each)

        x, y = action_args["coordinate"]
        x1, y1, x2, y2 = self.coord.build_click_box(driver_manager, xml, x, y)

        candidates = [
            [random.randint(x1, x2), random.randint(y1, y2)]
            for _ in range(8)
        ]

        print(f"Clicking inside box ({x1},{y1}) -> ({x2},{y2}) with {len(candidates)} candidates")

        last_result = {"status": "failure"}
        for coord in candidates:
            args = dict(action_args)
            args["coordinate"] = coord
            print(f"Trying click at {coord} ...")
            res = self.execute_with_retry(args, mobile_use, retries=retries_each, delay=delay_each)
            last_result = res
            if isinstance(res, dict) and res.get("status") == "success":
                print(f"Success at {coord}")
                return res

        print("All random attempts failed, falling back to original coordinate.")
        return self.execute_with_retry(action_args, mobile_use, retries=2, delay=delay_each)
    
    
    def _find_relevant_elements(self, xml: str, user_query: str):
       
        user_query_lower = user_query.lower()
        candidates = []

        for node in XMLParser.parse_nodes(xml):
            label = " ".join([node["text"], node["content_desc"], node["resource_id"]]).lower()
            if user_query_lower in label:
                candidates.append(node)

        return candidates
    
    def _create_action_from_element(self, element):
        
        center = XMLParser.get_center_point(element["bounds"])
        return {
            "arguments": {
                "action": "click",
                "coordinate": center
            }
        }
    
    def _vision_model_disambiguate(self, screenshot_path, relevant_elements, user_query):
        try:
            base64_image = self.screenshot_manager.encode_image(screenshot_path)
            
            prompt = (
                "You are a mobile UI assistant.\n"
                "There are multiple possible elements matching the user query.\n"
                "Your job: choose the BEST one.\n\n"
                "User Query: " + user_query + "\n\n"
                "Candidates:\n"
            )

            # Show candidates with bounds + text + desc
            for i, node in enumerate(relevant_elements):
                prompt += f"{i+1}. Bounds={node['bounds']} | Text='{node['text']}' | Desc='{node['content_desc']}' | ResID='{node['resource_id']}'\n"
            prompt += "\nRespond ONLY with a single integer ID (1..N) indicating the correct candidate.\n"

           
            output = self.qwen_client.vision_analysis(base64_image, prompt)
            print(f"Qwen chose candidate: {output}")

            # Parse index safely
            try:
                index = int(output.strip())
                if 1 <= index <= len(relevant_elements):
                    chosen = relevant_elements[index - 1]
                    center = XMLParser.get_center_point(chosen["bounds"])
                    print(f"Using element #{index} at {center}")
                    return {
                        "arguments": {
                            "action": "click",
                            "coordinate": center
                        }
                    }
                else:
                    print("Invalid index from Qwen, falling back to first candidate.")
                    chosen = relevant_elements[0]
                    center = XMLParser.get_center_point(chosen["bounds"])
                    return {
                        "arguments": {
                            "action": "click",
                            "coordinate": center
                        }
                    }
            except ValueError:
                print("Qwen returned unexpected output, falling back to first candidate.")
                chosen = relevant_elements[0]
                center = XMLParser.get_center_point(chosen["bounds"])
                return {
                    "arguments": {
                        "action": "click",
                        "coordinate": center
                    }
                }

        except Exception as e:
            print(f"Vision disambiguation failed: {e}")
            return None
    
    def normalize_mobile_action(self, action_name: str) -> str:
        if not action_name:
            return 'click'
        
        cleaned_action = action_name.lower().strip().replace(' ', '_')
        
        if cleaned_action in self.VALID_MOBILE_ACTIONS:
            return cleaned_action
        
        if cleaned_action in self.ACTION_MAPPINGS:
            return self.ACTION_MAPPINGS[cleaned_action]
        
        matches = difflib.get_close_matches(cleaned_action, list(self.ACTION_MAPPINGS.keys()), n=1, cutoff=0.6)
        if matches:
            return self.ACTION_MAPPINGS[matches[0]]
        
        valid_matches = difflib.get_close_matches(cleaned_action, list(self.VALID_MOBILE_ACTIONS), n=1, cutoff=0.6)
        if valid_matches:
            return valid_matches[0]
        
        if any(keyword in cleaned_action for keyword in ['click', 'tap', 'touch', 'press']):
            return 'click'
        elif any(keyword in cleaned_action for keyword in ['long', 'hold']):
            return 'long_press'
        elif any(keyword in cleaned_action for keyword in ['swipe', 'scroll', 'drag']):
            return 'swipe'
        elif any(keyword in cleaned_action for keyword in ['type', 'input', 'text']):
            return 'type'
        elif any(keyword in cleaned_action for keyword in ['key', 'button']):
            return 'key'
        
        print(f"Unknown action '{action_name}' mapped to 'click' as fallback")
        return 'click'
    
    def _fix_mobile_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(action, dict) or 'arguments' not in action:
            return action
        
        args = action['arguments']
        if 'action' not in args:
            return action
        
        original_action = args['action']
        normalized_action = self.normalize_mobile_action(original_action)
        if original_action != normalized_action:
            print(f"Action normalized: '{original_action}' -> '{normalized_action}'")
            action['arguments']['action'] = normalized_action

        if self._is_blocked_action(action):
            print("Blocked action (back/terminate). Replacing with wait.")
            action['arguments'] = {"action": "wait", "time": 0.2}
        
        return action
    
    def _is_blocked_action(self, action: dict) -> bool:

        try:
            args = action.get("arguments", {})
            a = (args.get("action") or "").lower().strip()
            if a == "terminate":
                return True
            if a == "system_button":
                btn = str(args.get("button", "")).lower()
                if btn in ("back", "home", "recent", "recents", "overview"):
                    return True
            return False
        except Exception:
            return False
    
    def _draw_click_box(self, image: Image.Image, bottom_right: list, box_size: int, color="orange"):

        from PIL import ImageDraw, ImageColor
        
        overlay = Image.new("RGBA", image.size, (255,255,255,0))
        draw = ImageDraw.Draw(overlay)

        x2, y2 = bottom_right
        x1 = max(1, x2 - box_size)
        y1 = max(1, y2 - box_size)

        try:
            box_color = ImageColor.getrgb(color) + (120,)
        except:
            box_color = (255, 165, 0, 120) 

        draw.rectangle([(x1, y1), (x2, y2)], fill=box_color, outline="red", width=3)
        return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")