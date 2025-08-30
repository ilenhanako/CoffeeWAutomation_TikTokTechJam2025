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
        # Set child states (substates of HomePage)
        self.child_states = ["STEMPage", "ExplorePage", "FollowingPage", "FriendsPage", "ForYouPage"]
        
        # Add base HomePage components
        self._add_base_components()
    
    def _add_base_components(self):
        """Add the base components that all HomePage substates inherit"""
        base_components = [
            UIComponent(name="LikeButton", component_type=ComponentType.BUTTON),
            UIComponent(name="ProfileNavBar", component_type=ComponentType.NAVIGATION),
            UIComponent(name="UserButton", component_type=ComponentType.BUTTON),
            UIComponent(name="CommentButton", component_type=ComponentType.BUTTON),
            UIComponent(name="ShareButton", component_type=ComponentType.BUTTON),
            UIComponent(name="SearchButton", component_type=ComponentType.BUTTON),
            UIComponent(name="Search", component_type=ComponentType.INPUT),
            # Tab navigation components
            UIComponent(name="LIVE", component_type=ComponentType.NAVIGATION),
            UIComponent(name="STEM", component_type=ComponentType.NAVIGATION), 
            UIComponent(name="Explore", component_type=ComponentType.NAVIGATION),
            UIComponent(name="Following", component_type=ComponentType.NAVIGATION),
            UIComponent(name="Friends", component_type=ComponentType.NAVIGATION),
            UIComponent(name="ForYou", component_type=ComponentType.NAVIGATION),
        ]
        self.components.extend(base_components)


# HomePage substates - inherit components from HomePage
class STEMPage(HomePage):
    name: str = "STEMPage"
    
    def __init__(self, **data):
        super().__init__(**data)  # This calls HomePage.__init__ which adds base components
        self.parent_state = "HomePage"


class ExplorePage(HomePage):
    name: str = "ExplorePage"
    
    def __init__(self, **data):
        super().__init__(**data)  # Inherits all HomePage components
        self.parent_state = "HomePage"


class FollowingPage(HomePage):
    name: str = "FollowingPage"
    
    def __init__(self, **data):
        super().__init__(**data)  # Inherits all HomePage components
        self.parent_state = "HomePage"


class FriendsPage(HomePage):
    name: str = "FriendsPage"
    
    def __init__(self, **data):
        super().__init__(**data)  # Inherits all HomePage components
        self.parent_state = "HomePage"


class ForYouPage(HomePage):
    name: str = "ForYouPage"
    
    def __init__(self, **data):
        super().__init__(**data)  # Inherits all HomePage components
        self.parent_state = "HomePage"


class ProfilePage(State):
    name: str = "ProfilePage"
    
    def __init__(self, **data):
        super().__init__(**data)
        # ProfilePage-specific components (doesn't inherit from HomePage since it's a different context)
        default_components = [
            UIComponent(name="SettingsButton", component_type=ComponentType.BUTTON),
            UIComponent(name="FollowingList", component_type=ComponentType.DISPLAY),
            UIComponent(name="FollowersList", component_type=ComponentType.DISPLAY),
            UIComponent(name="Likes", component_type=ComponentType.DISPLAY),
            UIComponent(name="FollowButton", component_type=ComponentType.BUTTON),
            UIComponent(name="MessageButton", component_type=ComponentType.BUTTON),
            # Add common navigation components
            UIComponent(name="ProfileNavBar", component_type=ComponentType.NAVIGATION),
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