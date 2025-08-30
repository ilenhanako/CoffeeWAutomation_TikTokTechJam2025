from neo4j import GraphDatabase
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
import chromadb
import logging
from contextlib import contextmanager

from ..models.scenario import BusinessScenario, ScenarioChunk
from ..models.ontology import State, UIComponent, Action, ExecutorStep, ScenarioPlan


class Neo4jKnowledgeGraph:
    def __init__(self, uri: str = "bolt://localhost:7687", 
                 username: str = "neo4j", 
                 password: str = "password",
                 embedding_model: str = "all-MiniLM-L6-v2"):
        
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Initialize logger first
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize ChromaDB for business scenario vector storage
        self.chroma_client = chromadb.Client()
        try:
            # Force delete and recreate collection to clear cache
            self.chroma_client.delete_collection("business_scenarios")
        except Exception:
            pass  # Collection might not exist
        
        self.scenario_collection = self.chroma_client.create_collection(
            name="business_scenarios",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize Neo4j schema
        self._create_constraints_and_indexes()
    
    @contextmanager
    def get_session(self):
        session = self.driver.session()
        try:
            yield session
        finally:
            session.close()
    
    def _create_constraints_and_indexes(self):
        """Create Neo4j constraints and indexes for optimal performance"""
        constraints_and_indexes = [
            "CREATE CONSTRAINT state_name_unique IF NOT EXISTS FOR (s:State) REQUIRE s.name IS UNIQUE",
            "CREATE CONSTRAINT component_id_unique IF NOT EXISTS FOR (c:Component) REQUIRE c.id IS UNIQUE",
            "CREATE INDEX state_name_idx IF NOT EXISTS FOR (s:State) ON (s.name)",
            "CREATE INDEX component_name_idx IF NOT EXISTS FOR (c:Component) ON (c.name)",
            "CREATE INDEX component_type_idx IF NOT EXISTS FOR (c:Component) ON (c.component_type)"
        ]
        
        with self.get_session() as session:
            for query in constraints_and_indexes:
                try:
                    session.run(query)
                except Exception as e:
                    self.logger.warning(f"Could not create constraint/index: {e}")
    
    def add_state(self, state: State) -> None:
        """Add a state node to the knowledge graph"""
        with self.get_session() as session:
            # Create state node
            # Convert child_states list to string for Neo4j storage
            child_states_str = ",".join(state.child_states) if state.child_states else ""
            
            session.run("""
                MERGE (s:State {name: $name})
                SET s.parent_state = $parent_state,
                    s.child_states = $child_states
            """, {
                "name": state.name,
                "parent_state": state.parent_state,
                "child_states": child_states_str
            })
            
            # Add components and relationships
            for component in state.components:
                component_id = f"{state.name}_{component.name}"
                
                # Create component node
                # Convert properties to string if not empty, otherwise store empty dict
                props_str = str(component.properties) if component.properties else "{}"
                
                session.run("""
                    MERGE (c:Component {id: $id})
                    SET c.name = $name,
                        c.component_type = $component_type,
                        c.properties_json = $properties_json
                """, {
                    "id": component_id,
                    "name": component.name,
                    "component_type": str(component.component_type),
                    "properties_json": props_str
                })
                
                # Create HAS_COMPONENT relationship
                session.run("""
                    MATCH (s:State {name: $state_name})
                    MATCH (c:Component {id: $component_id})
                    MERGE (s)-[:HAS_COMPONENT]->(c)
                """, {
                    "state_name": state.name,
                    "component_id": component_id
                })
            
            # Add hierarchical relationships for child states
            if state.parent_state:
                session.run("""
                    MATCH (parent:State {name: $parent_name})
                    MATCH (child:State {name: $child_name})
                    MERGE (parent)-[:CONTAINS]->(child)
                    MERGE (child)-[:CHILD_OF]->(parent)
                """, {
                    "parent_name": state.parent_state,
                    "child_name": state.name
                })
    
    def add_action_relationship(self, component_id: str, action_type: str, 
                               target_state: str, properties: Dict[str, Any] = None) -> None:
        """Add an action relationship between component and target state"""
        with self.get_session() as session:
            properties = properties or {}
            
            session.run(f"""
                MATCH (c:Component {{id: $component_id}})
                MATCH (s:State {{name: $target_state}})
                MERGE (c)-[r:{action_type.upper()}]->(s)
                SET r += $properties
            """, {
                "component_id": component_id,
                "target_state": target_state,
                "properties": properties
            })
    
    def find_action_paths(self, start_state: str, end_state: str = None, 
                          max_depth: int = 5) -> List[Dict[str, Any]]:
        """Find all possible action paths from start state to end state"""
        with self.get_session() as session:
            if end_state:
                # Try direct path first
                query = """
                    MATCH path = (start:State {name: $start_state})-[:HAS_COMPONENT]->(c:Component)
                             -[action:TAP|SWIPE|SCROLL|TYPE]->(end:State {name: $end_state})
                    RETURN path, 
                           [rel in relationships(path) | type(rel)] as actions,
                           [node in nodes(path) | node] as nodes
                    UNION
                    MATCH path = (start:State {name: $start_state})-[:HAS_COMPONENT]->(c1:Component)
                             -[a1:TAP|SWIPE|SCROLL|TYPE]->(mid:State)
                             -[:HAS_COMPONENT]->(c2:Component)
                             -[a2:TAP|SWIPE|SCROLL|TYPE]->(end:State {name: $end_state})
                    WHERE start.name <> end.name
                    RETURN path,
                           [rel in relationships(path) | type(rel)] as actions,
                           [node in nodes(path) | node] as nodes
                    LIMIT 20
                """
                
                result = session.run(query, {
                    "start_state": start_state,
                    "end_state": end_state
                })
            else:
                query = """
                    MATCH path = (start:State {name: $start_state})-[:HAS_COMPONENT]->(c:Component)
                             -[action:TAP|SWIPE|SCROLL|TYPE]->(end:State)
                    RETURN path,
                           [rel in relationships(path) | type(rel)] as actions,
                           [node in nodes(path) | node] as nodes
                    LIMIT 20
                """
                
                result = session.run(query, {"start_state": start_state})
            
            paths = []
            for record in result:
                paths.append({
                    "actions": record["actions"],
                    "nodes": [dict(node) for node in record["nodes"]],
                    "path_length": len(record["actions"])
                })
            
            return paths
    
    def find_components_in_state_hierarchy(self, state_name: str) -> List[Dict[str, Any]]:
        """Find all components in a state and its sub-states"""
        with self.get_session() as session:
            result = session.run("""
                MATCH (state:State {name: $state_name})-[:CONTAINS*0..]->(substate:State)
                      -[:HAS_COMPONENT]->(c:Component)
                RETURN DISTINCT c, substate.name as containing_state
                ORDER BY containing_state, c.name
            """, {"state_name": state_name})
            
            components = []
            for record in result:
                component_data = dict(record["c"])
                component_data["containing_state"] = record["containing_state"]
                components.append(component_data)
            
            return components
    
    def get_possible_actions_from_component(self, component_id: str) -> List[Dict[str, Any]]:
        """Get all possible actions from a specific component"""
        with self.get_session() as session:
            result = session.run("""
                MATCH (c:Component {id: $component_id})-[action]->(target:State)
                WHERE type(action) IN ['TAP', 'SWIPE', 'SCROLL', 'TYPE']
                RETURN type(action) as action_type, 
                       target.name as target_state,
                       properties(action) as action_properties
            """, {"component_id": component_id})
            
            actions = []
            for record in result:
                actions.append({
                    "action_type": record["action_type"],
                    "target_state": record["target_state"],
                    "properties": dict(record["action_properties"])
                })
            
            return actions
    
    def add_business_scenario_to_vector_store(self, scenario: BusinessScenario) -> None:
        """Add business scenario to ChromaDB for semantic search"""
        # Create text representation of the scenario
        scenario_text = f"""
        Feature: {scenario.feature}
        Goal: {scenario.goal}
        Given: {' '.join(scenario.given_conditions)}
        When: {' '.join(scenario.when_actions)}
        Then: {' '.join(scenario.then_expectations)}
        """.strip()
        
        # Generate embedding
        embedding = self.embedding_model.encode([scenario_text])[0]
        
        # Store in ChromaDB
        self.scenario_collection.add(
            documents=[scenario_text],
            embeddings=[embedding.tolist()],
            metadatas=[{
                "scenario_id": scenario.id or 0,
                "feature": scenario.feature,
                "goal": scenario.goal,
                "scenario_type": str(scenario.scenario_type)
            }],
            ids=[f"scenario_{scenario.id or 0}"]
        )
    
    def find_similar_business_scenarios(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find business scenarios similar to the query"""
        query_embedding = self.embedding_model.encode([query])[0]
        
        results = self.scenario_collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )
        
        scenarios = []
        if results['documents']:
            for doc, metadata, distance in zip(
                results['documents'][0], 
                results['metadatas'][0], 
                results['distances'][0]
            ):
                scenarios.append({
                    "document": doc,
                    "metadata": metadata,
                    "similarity": 1 - distance
                })
        
        return scenarios
    
    def generate_executor_steps_from_paths(self, paths: List[Dict[str, Any]], 
                                          scenario_goal: str) -> ScenarioPlan:
        """Convert graph paths to ExecutorSteps"""
        if not paths:
            return ScenarioPlan(scenario_id=0, scenario_title=scenario_goal, steps=[])
        
        # Use the first path for now (could be enhanced to merge multiple paths)
        selected_path = paths[0]
        steps = []
        
        step_id = 1
        nodes = selected_path["nodes"]
        actions = selected_path["actions"]
        
        # Debug path structure
        self.logger.info(f"Path structure - Nodes: {len(nodes)}, Actions: {len(actions)}")
        self.logger.info(f"Actions: {actions}")
        self.logger.info(f"Node types: {[node.get('name', 'unknown') for node in nodes]}")
        
        # Path structure: State -> Component -> State
        # Actions: ["HAS_COMPONENT", "TAP/SWIPE/SCROLL/TYPE"]
        if len(nodes) >= 3 and len(actions) >= 2:
            start_state = nodes[0]
            component = nodes[1] 
            end_state = nodes[2]
            action_type = actions[1].lower()  # Skip "HAS_COMPONENT", get actual action
            
            # Get action properties if available
            component_id = component.get("id", "")
            action_details = self.get_possible_actions_from_component(component_id)
            
            query_for_qwen = f"{action_type.capitalize()} on {component.get('name', 'component')}"
            alternatives = [f"Long press on {component.get('name', 'component')}"]
            
            # Enhance with stored action properties
            for action_detail in action_details:
                if action_detail["action_type"].lower() == action_type:
                    props = action_detail.get("properties", {})
                    if "query_for_qwen" in props:
                        query_for_qwen = props["query_for_qwen"]
                    if "alternative_actions" in props:
                        alternatives = props["alternative_actions"]
                    break
            
            step = ExecutorStep(
                step_id=step_id,
                description=f"{action_type.capitalize()} {component.get('name', 'component')}",
                action_type=action_type,
                query_for_qwen=query_for_qwen,
                alternative_actions=alternatives,
                expected_state=end_state.get("name") if end_state else None
            )
            
            steps.append(step)
            self.logger.info(f"Generated step: {step.description}")
        else:
            self.logger.warning(f"Unexpected path structure: {len(nodes)} nodes, {len(actions)} actions")
        
        return ScenarioPlan(
            scenario_id=1,
            scenario_title=scenario_goal,
            steps=steps
        )
    
    def close(self):
        """Close the Neo4j driver connection"""
        if self.driver:
            self.driver.close()