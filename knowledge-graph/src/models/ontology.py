from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum


class ComponentType(str, Enum):
    BUTTON = "button"
    INPUT = "input"
    NAVIGATION = "navigation"
    DISPLAY = "display"


class UIComponent(BaseModel):
    name: str
    component_type: ComponentType
    properties: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True


class State(BaseModel):
    name: str
    components: List[UIComponent] = Field(default_factory=list)
    parent_state: Optional[str] = None
    child_states: List[str] = Field(default_factory=list)
    
    def add_component(self, component: UIComponent):
        self.components.append(component)


class HomePage(State):
    name: str = "HomePage"
    
    def __init__(self, **data):
        super().__init__(**data)
        # Add default components from ontology
        default_components = [
            UIComponent(name="LikeButton", component_type=ComponentType.BUTTON),
            UIComponent(name="ProfileNavBar", component_type=ComponentType.NAVIGATION),
            UIComponent(name="UserButton", component_type=ComponentType.BUTTON),
            UIComponent(name="CommentButton", component_type=ComponentType.BUTTON),
            UIComponent(name="ShareButton", component_type=ComponentType.BUTTON),
            UIComponent(name="SearchButton", component_type=ComponentType.BUTTON),
            UIComponent(name="LIVE", component_type=ComponentType.NAVIGATION),
            UIComponent(name="STEM", component_type=ComponentType.NAVIGATION),
            UIComponent(name="Explore", component_type=ComponentType.NAVIGATION),
            UIComponent(name="Following", component_type=ComponentType.NAVIGATION),
            UIComponent(name="Friends", component_type=ComponentType.NAVIGATION),
            UIComponent(name="ForYou", component_type=ComponentType.NAVIGATION),
            UIComponent(name="Search", component_type=ComponentType.INPUT),
        ]
        self.components.extend(default_components)


class ProfilePage(State):
    name: str = "ProfilePage"
    
    def __init__(self, **data):
        super().__init__(**data)
        default_components = [
            UIComponent(name="SettingsButton", component_type=ComponentType.BUTTON),
            UIComponent(name="Following", component_type=ComponentType.DISPLAY),
            UIComponent(name="Followers", component_type=ComponentType.DISPLAY),
            UIComponent(name="Likes", component_type=ComponentType.DISPLAY),
            UIComponent(name="FollowButton", component_type=ComponentType.BUTTON),
            UIComponent(name="MessageButton", component_type=ComponentType.BUTTON),
        ]
        self.components.extend(default_components)


class SettingsPage(State):
    name: str = "SettingsPage"
    
    def __init__(self, **data):
        super().__init__(**data)
        default_components = [
            UIComponent(name="NameInput", component_type=ComponentType.INPUT),
            UIComponent(name="UserNameInput", component_type=ComponentType.INPUT),
            UIComponent(name="BioInput", component_type=ComponentType.INPUT),
            UIComponent(name="LinksInput", component_type=ComponentType.INPUT),
        ]
        self.components.extend(default_components)


class ActionType(str, Enum):
    TAP = "tap"
    SWIPE = "swipe"
    SCROLL = "scroll"
    TYPE = "type"
    WAIT = "wait"


class Action(BaseModel):
    action_type: ActionType
    target_component: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    description: str = ""
    
    class Config:
        use_enum_values = True


class Transition(BaseModel):
    from_state: str
    to_state: str
    trigger_action: Action
    conditions: List[str] = Field(default_factory=list)


class ExecutorStep(BaseModel):
    step_id: int
    description: str
    action_type: str
    query_for_qwen: str
    alternative_actions: List[str] = Field(default_factory=list)
    expected_state: Optional[str] = None


class ScenarioPlan(BaseModel):
    scenario_id: int
    scenario_title: str
    steps: List[ExecutorStep]
    preconditions: List[str] = Field(default_factory=list)
    postconditions: List[str] = Field(default_factory=list)
    environment_toggles: Dict[str, Any] = Field(default_factory=dict)