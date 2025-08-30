import networkx as nx
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
import chromadb
import numpy as np
import uuid

from ..models.scenario import BusinessScenario, ScenarioChunk, Intent, Constraint
from ..models.ontology import State, Action, Transition


class KnowledgeGraph:
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        self.graph = nx.DiGraph()
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Initialize ChromaDB for vector storage
        self.chroma_client = chromadb.Client()
        self.scenario_collection = self.chroma_client.create_collection(
            name="scenarios",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Maps for quick lookups
        self.scenario_index: Dict[int, BusinessScenario] = {}
        self.state_index: Dict[str, State] = {}
        
    def add_scenario(self, scenario: BusinessScenario) -> None:
        scenario_id = scenario.id or len(self.scenario_index)
        scenario.id = scenario_id
        
        # Store scenario
        self.scenario_index[scenario_id] = scenario
        
        # Add scenario node to graph
        self.graph.add_node(
            f"scenario_{scenario_id}",
            type="scenario",
            title=scenario.title,
            feature=scenario.feature,
            goal=scenario.goal,
            scenario_type=scenario.scenario_type
        )
        
        # Add intent nodes and connections
        for intent in scenario.intents:
            intent_id = f"intent_{scenario_id}_{intent.name}"
            self.graph.add_node(
                intent_id,
                type="intent",
                name=intent.name,
                description=intent.description
            )
            self.graph.add_edge(f"scenario_{scenario_id}", intent_id, relation="has_intent")
        
        # Add constraint nodes and connections
        for constraint in scenario.constraints:
            constraint_id = f"constraint_{scenario_id}_{constraint.name}"
            self.graph.add_node(
                constraint_id,
                type="constraint",
                name=constraint.name,
                constraint_type=constraint.type,
                condition=constraint.condition
            )
            self.graph.add_edge(f"scenario_{scenario_id}", constraint_id, relation="has_constraint")
        
        # Add entity nodes
        for entity in scenario.entities:
            entity_id = f"entity_{entity}"
            if not self.graph.has_node(entity_id):
                self.graph.add_node(entity_id, type="entity", name=entity)
            self.graph.add_edge(f"scenario_{scenario_id}", entity_id, relation="involves_entity")
        
        # Create scenario chunks and embed them
        chunks = self._create_scenario_chunks(scenario)
        self._embed_and_store_chunks(chunks)
        
        # Create relationships between scenarios based on shared entities/intents
        self._create_scenario_relationships(scenario_id)
    
    def add_state(self, state: State) -> None:
        self.state_index[state.name] = state
        
        # Add state node
        self.graph.add_node(
            f"state_{state.name}",
            type="state",
            name=state.name
        )
        
        # Add component nodes
        for component in state.components:
            component_id = f"component_{state.name}_{component.name}"
            self.graph.add_node(
                component_id,
                type="component",
                name=component.name,
                component_type=component.component_type
            )
            self.graph.add_edge(f"state_{state.name}", component_id, relation="has_component")
    
    def add_transition(self, transition: Transition) -> None:
        transition_id = f"transition_{transition.from_state}_to_{transition.to_state}"
        
        self.graph.add_node(
            transition_id,
            type="transition",
            from_state=transition.from_state,
            to_state=transition.to_state,
            action_type=transition.trigger_action.action_type
        )
        
        # Connect states through transition
        if self.graph.has_node(f"state_{transition.from_state}"):
            self.graph.add_edge(f"state_{transition.from_state}", transition_id, relation="from_state")
        if self.graph.has_node(f"state_{transition.to_state}"):
            self.graph.add_edge(transition_id, f"state_{transition.to_state}", relation="to_state")
    
    def _create_scenario_chunks(self, scenario: BusinessScenario) -> List[ScenarioChunk]:
        chunks = []
        scenario_id = scenario.id
        
        # Chunk given conditions
        for i, condition in enumerate(scenario.given_conditions):
            chunk = ScenarioChunk(
                chunk_id=f"{scenario_id}_given_{i}",
                scenario_id=scenario_id,
                content=condition,
                chunk_type="given"
            )
            chunks.append(chunk)
        
        # Chunk when actions
        for i, action in enumerate(scenario.when_actions):
            chunk = ScenarioChunk(
                chunk_id=f"{scenario_id}_when_{i}",
                scenario_id=scenario_id,
                content=action,
                chunk_type="when"
            )
            chunks.append(chunk)
        
        # Chunk then expectations
        for i, expectation in enumerate(scenario.then_expectations):
            chunk = ScenarioChunk(
                chunk_id=f"{scenario_id}_then_{i}",
                scenario_id=scenario_id,
                content=expectation,
                chunk_type="then"
            )
            chunks.append(chunk)
        
        return chunks
    
    def _embed_and_store_chunks(self, chunks: List[ScenarioChunk]) -> None:
        if not chunks:
            return
            
        texts = [chunk.content for chunk in chunks]
        embeddings = self.embedding_model.encode(texts)
        
        # Store in ChromaDB
        self.scenario_collection.add(
            documents=texts,
            embeddings=embeddings.tolist(),
            metadatas=[{
                "chunk_id": chunk.chunk_id,
                "scenario_id": chunk.scenario_id,
                "chunk_type": chunk.chunk_type
            } for chunk in chunks],
            ids=[chunk.chunk_id for chunk in chunks]
        )
        
        # Update chunks with embeddings
        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding.tolist()
    
    def _create_scenario_relationships(self, scenario_id: int) -> None:
        current_scenario = self.scenario_index[scenario_id]
        
        # Find scenarios with shared entities or intents
        for other_id, other_scenario in self.scenario_index.items():
            if other_id == scenario_id:
                continue
                
            # Check for shared entities
            shared_entities = set(current_scenario.entities) & set(other_scenario.entities)
            if shared_entities:
                weight = len(shared_entities) / max(len(current_scenario.entities), len(other_scenario.entities))
                self.graph.add_edge(
                    f"scenario_{scenario_id}",
                    f"scenario_{other_id}",
                    relation="shares_entities",
                    weight=weight,
                    shared_entities=list(shared_entities)
                )
            
            # Check for shared intents
            current_intent_names = {intent.name for intent in current_scenario.intents}
            other_intent_names = {intent.name for intent in other_scenario.intents}
            shared_intents = current_intent_names & other_intent_names
            if shared_intents:
                weight = len(shared_intents) / max(len(current_intent_names), len(other_intent_names))
                self.graph.add_edge(
                    f"scenario_{scenario_id}",
                    f"scenario_{other_id}",
                    relation="shares_intents",
                    weight=weight,
                    shared_intents=list(shared_intents)
                )
    
    def find_similar_scenarios(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        query_embedding = self.embedding_model.encode([query])
        
        results = self.scenario_collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=top_k
        )
        
        scenario_scores = {}
        for metadata, distance in zip(results['metadatas'][0], results['distances'][0]):
            scenario_id = metadata['scenario_id']
            similarity = 1 - distance  # Convert distance to similarity
            if scenario_id not in scenario_scores:
                scenario_scores[scenario_id] = similarity
            else:
                scenario_scores[scenario_id] = max(scenario_scores[scenario_id], similarity)
        
        return sorted(scenario_scores.items(), key=lambda x: x[1], reverse=True)
    
    def get_related_scenarios(self, scenario_id: int, max_depth: int = 2) -> List[int]:
        scenario_node = f"scenario_{scenario_id}"
        if not self.graph.has_node(scenario_node):
            return []
        
        related = set()
        current_level = {scenario_node}
        
        for _ in range(max_depth):
            next_level = set()
            for node in current_level:
                # Get neighbors (both directions)
                neighbors = set(self.graph.predecessors(node)) | set(self.graph.successors(node))
                scenario_neighbors = {n for n in neighbors if n.startswith("scenario_")}
                next_level.update(scenario_neighbors)
                related.update(scenario_neighbors)
            current_level = next_level - related
            if not current_level:
                break
        
        # Remove the original scenario and convert to IDs
        related.discard(scenario_node)
        return [int(node.split("_")[1]) for node in related]
    
    def get_scenario_constraints(self, scenario_id: int) -> List[Constraint]:
        scenario = self.scenario_index.get(scenario_id)
        return scenario.constraints if scenario else []
    
    def export_graph_data(self) -> Dict[str, Any]:
        return {
            "nodes": [
                {"id": node, **data} 
                for node, data in self.graph.nodes(data=True)
            ],
            "edges": [
                {"source": u, "target": v, **data} 
                for u, v, data in self.graph.edges(data=True)
            ],
            "scenarios": {
                scenario_id: scenario.dict() 
                for scenario_id, scenario in self.scenario_index.items()
            }
        }