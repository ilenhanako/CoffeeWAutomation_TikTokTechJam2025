from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum


class ScenarioType(str, Enum):
    FEATURE = "feature"
    REGRESSION = "regression"
    EDGE_CASE = "edge_case"
    PERFORMANCE = "performance"


class Intent(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class Constraint(BaseModel):
    name: str
    type: str  # invariant, precondition, postcondition
    condition: str
    description: str = ""


class BusinessScenario(BaseModel):
    id: Optional[int] = None
    title: str
    feature: str
    goal: str
    scenario_type: ScenarioType = ScenarioType.FEATURE
    given_conditions: List[str] = Field(default_factory=list)
    when_actions: List[str] = Field(default_factory=list)
    then_expectations: List[str] = Field(default_factory=list)
    constraints: List[Constraint] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    
    # Extracted semantic information
    intents: List[Intent] = Field(default_factory=list)
    entities: List[str] = Field(default_factory=list)
    relationships: Dict[str, List[str]] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True


class ScenarioChunk(BaseModel):
    chunk_id: str
    scenario_id: int
    content: str
    chunk_type: str  # given, when, then, constraint
    embedding: Optional[List[float]] = None
    semantic_tags: List[str] = Field(default_factory=list)