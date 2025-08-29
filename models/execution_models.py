from dataclasses import dataclass
from typing import List, Dict, Optional, Any

@dataclass
class ExecutorStep:
    # a step
    step_id: int
    description: str
    action_type: str  # click, swipe, type, wait, verify
    query_for_qwen: str
    alternative_actions: List[str]

    expected_state: Optional[str] = None

@dataclass
class ScenarioPlan:
    # a test scenario
    scenario_id: int
    scenario_title: str
    steps: List[ExecutorStep]
    success_criteria: str
    failure_scenarios: List[str]

@dataclass
class ActionResult:
    status: str
    action: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ProcessorConfig:
    def __init__(self):
        self.image_processor = self
        self.patch_size = 14
        self.merge_size = 2
        self.min_pixels = 256 * 28 * 28
        self.max_pixels = 1280 * 28 * 28

@dataclass
class Interruption:
    present: bool
    kind: str = ""
    coverage: float = 0.0
    nodes: List[dict] = None
    screenshot_path: Optional[str] = None

@dataclass
class EvaluationResult:
    ok: bool
    reason: str
    recovery: str
    suggestions: List[str]
    gate_type: str = "NONE"
    confidence: float = 0.0