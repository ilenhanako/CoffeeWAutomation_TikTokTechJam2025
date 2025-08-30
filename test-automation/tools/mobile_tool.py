from typing import Union, Tuple, List

from qwen_agent.tools.base import BaseTool, register_tool
from appium.webdriver.webdriver import WebDriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.action_chains import ActionChains
import time


@register_tool("mobile_use")
class MobileUse(BaseTool):
    def __init__(self, cfg=None, driver: WebDriver = None):
        self.display_width_px = cfg["display_width_px"]
        self.display_height_px = cfg["display_height_px"]
        self.driver = driver
        super().__init__(cfg)

    @property
    def description(self):
        return f"""
Use a touchscreen to interact with a mobile device, and take screenshots.
* This is an interface to a mobile device with touchscreen. You can perform actions like clicking, typing, swiping, etc.
* Some applications may take time to start or process actions, so you may need to wait and take successive screenshots to see the results of your actions.
* The screen's resolution is {self.display_width_px}x{self.display_height_px}.
* Make sure to click any buttons, links, icons, etc with the cursor tip in the center of the element. Don't click boxes on their edges unless asked.
""".strip()

    parameters = {
        "properties": {
            "action": {
                "description": """
The action to perform. The available actions are:
* `key`: Perform a key event on the mobile device.
    - This supports adb's `keyevent` syntax.
    - Examples: "volume_up", "volume_down", "power", "camera", "clear".
* `click`: Click the point on the screen with coordinate (x, y).
* `long_press`: Press the point on the screen with coordinate (x, y) for specified seconds.
* `swipe`: Swipe from the starting point with coordinate (x, y) to the end point with coordinates2 (x2, y2).
* `type`: Input the specified text into the activated input box.
* `system_button`: Press the system button.
* `open`: Open an app on the device.
* `wait`: Wait specified seconds for the change to happen.
* `terminate`: Terminate the current task and report its completion status.
""".strip(),
                "enum": [
                    "key",
                    "click",
                    "long_press",
                    "swipe",
                    "type",
                    "system_button",
                    "open",
                    "wait",
                    "terminate",
                ],
                "type": "string",
            },
            "coordinate": {
                "description": "(x, y): The x (pixels from the left edge) and y (pixels from the top edge) coordinates to move the mouse to. Required only by `action=click`, `action=long_press`, and `action=swipe`.",
                "type": "array",
            },
            "coordinate2": {
                "description": "(x, y): The x (pixels from the left edge) and y (pixels from the top edge) coordinates to move the mouse to. Required only by `action=swipe`.",
                "type": "array",
            },
            "text": {
                "description": "Required only by `action=key`, `action=type`, and `action=open`.",
                "type": "string",
            },
            "time": {
                "description": "The seconds to wait. Required only by `action=long_press` and `action=wait`.",
                "type": "number",
            },
            "button": {
                "description": "Back means returning to the previous interface, Home means returning to the desktop, Menu means opening the application background menu, and Enter means pressing the enter. Required only by `action=system_button`",
                "enum": [
                    "Back",
                    "Home",
                    "Menu",
                    "Enter",
                ],
                "type": "string",
            },
            "status": {
                "description": "The status of the task. Required only by `action=terminate`.",
                "type": "string",
                "enum": ["success", "failure"],
            },
        },
        "required": ["action"],
        "type": "object",
    }


    def call(self, params: Union[str, dict], **kwargs):
        params = self._verify_json_format_args(params)
        # print(f"[DEBUG] MobileUse called with: {params}")
        action = params["action"]
        if action == "key":
            return self._key(params["text"])
        elif action == "click":
            return self._click(
                coordinate=params["coordinate"]
            )
        elif action == "long_press":
            return self._long_press(
                coordinate=params["coordinate"], time=params["time"]
            )
        elif action == "swipe":
            return self._swipe(
                coordinate=params["coordinate"], coordinate2=params["coordinate2"]
            )
        elif action == "type":
            return self._type(params["text"])
        elif action == "system_button":
            return self._system_button(params["button"])
        elif action == "open":
            return self._open(params["text"])
        elif action == "wait":
            return self._wait(params["time"])
        elif action == "terminate":
            return self._terminate(params["status"])
        else:
            raise ValueError(f"Unknown action: {action}")

    def _key(self, text: str):
        """
        Performs a key event on the device.
        Example: "volume_up", "volume_down", "power".
        """
        try:
            self.driver.press_keycode(self._map_key(text))
            return {"status": "success", "key": text}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _click(self, coordinate: Tuple[int, int]):
        try:
            x, y = coordinate
            self.driver.tap([(x, y)])
            return {"status": "success", "clicked": coordinate}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _long_press(self, coordinate: Tuple[int, int], time: int):
        try:
            actions = ActionChains(self.driver)
            actions.w3c_actions.pointer_action.move_to_location(*coordinate)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.pause(time)
            actions.w3c_actions.pointer_action.release()
            actions.perform()
            return {"status": "success", "long_pressed": coordinate}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _swipe(self, coordinate: Tuple[int, int], coordinate2: Tuple[int, int]):
        try:
            self.driver.swipe(coordinate[0], coordinate[1], coordinate2[0], coordinate2[1], duration=800)
            return {"status": "success", "swipe": (coordinate, coordinate2)}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _type(self, text: str):
        try:
            # Find all EditText elements
            text_fields = self.driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.EditText")
            # print(f"[DEBUG] Found {len(text_fields)} EditText elements")
            
            if text_fields:
                field = text_fields[0]  # Use the first one
                field.click()  # Focus it
                time.sleep(1)   # Wait for focus
                field.clear()   # Clear existing text
                field.send_keys(text)

                self.driver.press_keycode(66)
                return {"status": "success", "typed": text}
            else:
                return {"status": "error", "error": "No EditText elements found"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _system_button(self, button: str):
        mapping = {
            "Back": 4,
            "Home": 3,
            "Menu": 82,
            "Enter": 66
        }
        try:
            self.driver.press_keycode(mapping[button])
            return {"status": "success", "button": button}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _open(self, text: str):
        try:
            self.driver.activate_app(text)
            return {"status": "success", "opened": text}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _wait(self, time_val: int):
        time.sleep(time_val)
        return {"status": "success", "waited": time_val}

    def _terminate(self, status: str):
        return {"status": status}


    def _map_key(self, key: str):
        mapping = {
            "volume_up": 24,
            "volume_down": 25,
            "power": 26,
            "camera": 27,
            "clear": 28
        }
        return mapping.get(key.lower(), 66)
    