
from typing import TypedDict, Dict, Any, List, Optional

class UIState(TypedDict, total=False):
    # inputs
    business_goal: str
    user_query: str
    step_description: str
    expected_state_hint: str

    screenshot_path: str
    page_source_xml: str
    screenshot_b64: str

    exec_action: Dict[str, Any]
    exec_result: Dict[str, Any]
    eval_result: Dict[str, Any]

    # control
    cycle: int
    done: bool
    notes: List[str]
