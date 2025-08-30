from typing import List, Dict, Any, Optional
from .neo4j_knowledge_graph import Neo4jKnowledgeGraph
from ..models.scenario import BusinessScenario
from ..models.ontology import ScenarioPlan, ExecutorStep


class GraphQueryInterface:
    """High-level interface for querying the knowledge graph"""
    
    def __init__(self, kg: Neo4jKnowledgeGraph):
        self.kg = kg
    
    def query_business_scenario(self, query: str, start_state: str = "HomePage") -> ScenarioPlan:
        """
        Main entry point: query with business scenario and get executable plan
        
        Flow:
        1. Find similar business scenarios in vector store
        2. Extract goal/intent from similar scenarios
        3. Find action paths in knowledge graph
        4. Generate ExecutorSteps
        """
        print(f"🔍 Querying business scenario: {query}")
        
        # Step 1: Find similar business scenarios
        similar_scenarios = self.kg.find_similar_business_scenarios(query, top_k=3)
        
        if not similar_scenarios:
            print("⚠️  No similar business scenarios found")
            return ScenarioPlan(scenario_id=0, scenario_title=query, steps=[])
        
        print(f"📋 Found {len(similar_scenarios)} similar scenarios")
        for i, scenario in enumerate(similar_scenarios):
            print(f"  {i+1}. {scenario['metadata'].get('goal', 'Unknown goal')} "
                  f"(similarity: {scenario['similarity']:.2f})")
        
        # Step 2: Extract goal from best matching scenario
        best_scenario = similar_scenarios[0]
        goal = best_scenario['metadata'].get('goal', query)
        
        # Step 3: Find action paths in knowledge graph
        # For now, find paths from start_state to any reachable state
        paths = self.kg.find_action_paths(start_state, max_depth=3)
        
        if not paths:
            print(f"⚠️  No action paths found from {start_state}")
            return ScenarioPlan(scenario_id=1, scenario_title=goal, steps=[])
        
        print(f"🛤️  Found {len(paths)} possible action paths")
        
        # Step 4: Generate ExecutorSteps from paths
        scenario_plan = self.kg.generate_executor_steps_from_paths(paths, goal)
        
        print(f"✅ Generated plan with {len(scenario_plan.steps)} steps")
        return scenario_plan
    
    def find_paths_to_goal(self, start_state: str, goal_keywords: List[str]) -> List[Dict[str, Any]]:
        """Find paths from start state that might achieve the goal"""
        # Get all possible paths from start state
        all_paths = self.kg.find_action_paths(start_state, max_depth=4)
        
        # Filter paths that might be relevant to the goal
        relevant_paths = []
        for path in all_paths:
            path_text = " ".join([
                node.get("name", "") for node in path["nodes"]
            ]).lower()
            
            # Check if any goal keywords appear in the path
            if any(keyword.lower() in path_text for keyword in goal_keywords):
                relevant_paths.append(path)
        
        return relevant_paths or all_paths[:5]  # Fallback to first 5 paths
    
    def explore_state(self, state_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific state"""
        components = self.kg.find_components_in_state_hierarchy(state_name)
        
        state_info = {
            "state_name": state_name,
            "components": components,
            "possible_actions": {}
        }
        
        # Get possible actions for each component
        for component in components:
            component_id = component.get("id", "")
            actions = self.kg.get_possible_actions_from_component(component_id)
            if actions:
                state_info["possible_actions"][component_id] = actions
        
        return state_info
    
    def get_navigation_graph(self) -> Dict[str, Any]:
        """Get overview of how states connect to each other"""
        with self.kg.get_session() as session:
            # Get all states and their connections
            result = session.run("""
                MATCH (s1:State)-[:HAS_COMPONENT]->(c:Component)-[action]->(s2:State)
                WHERE type(action) IN ['TAP', 'SWIPE', 'SCROLL', 'TYPE']
                RETURN s1.name as from_state, 
                       c.name as via_component,
                       type(action) as action_type,
                       s2.name as to_state
                ORDER BY from_state, via_component
            """)
            
            navigation_map = {}
            for record in result:
                from_state = record["from_state"]
                if from_state not in navigation_map:
                    navigation_map[from_state] = []
                
                navigation_map[from_state].append({
                    "component": record["via_component"],
                    "action": record["action_type"], 
                    "destination": record["to_state"]
                })
            
            return navigation_map
    
    def add_sample_business_scenarios(self):
        """Add sample business scenarios to vector store for testing"""
        sample_scenarios = [
            BusinessScenario(
                id=1,
                title="User can log in",
                feature="Authentication",
                goal="Reach Dashboard",
                given_conditions=["app.launched()"],
                when_actions=["I choose to log in with a valid account"],
                then_expectations=[
                    "I should eventually be on Dashboard",
                    "property analytics.event_fired('login_success')",
                    "invariant no_blocking_spinners"
                ]
            ),
            BusinessScenario(
                id=2, 
                title="Comment on a video",
                feature="Social interaction",
                goal="Post comment on video",
                given_conditions=["I am on HomePage", "I see a video post"],
                when_actions=["I tap the comment button", "I type a comment", "I submit"],
                then_expectations=["Comment appears in comment list", "Comment count increases"]
            ),
            BusinessScenario(
                id=3,
                title="Update profile information", 
                feature="Profile management",
                goal="Update user profile",
                given_conditions=["I am logged in", "I am on ProfilePage"],
                when_actions=["I tap settings", "I update my bio", "I save changes"],
                then_expectations=["Bio is updated", "Changes are saved", "I return to ProfilePage"]
            ),
            BusinessScenario(
                id=4,
                title="Like a video post",
                feature="Social interaction", 
                goal="Like video content",
                given_conditions=["I am on HomePage", "I see a video I want to like"],
                when_actions=["I tap the like button"],
                then_expectations=["Like button changes state", "Like count increases"]
            )
        ]
        
        print("📚 Adding sample business scenarios to vector store...")
        for scenario in sample_scenarios:
            self.kg.add_business_scenario_to_vector_store(scenario)
        
        print(f"✅ Added {len(sample_scenarios)} sample business scenarios")


def demo_query_interface():
    """Demonstrate the query interface functionality"""
    kg = Neo4jKnowledgeGraph()
    query_interface = GraphQueryInterface(kg)
    
    try:
        # Add sample scenarios
        query_interface.add_sample_business_scenarios()
        
        # Demo queries
        test_queries = [
            "User wants to log in to the app",
            "I want to comment on a video", 
            "Update my profile bio",
            "Like a video post I enjoy"
        ]
        
        print("\n🎯 Demo: Querying business scenarios")
        print("=" * 50)
        
        for query in test_queries:
            print(f"\n📝 Query: {query}")
            print("-" * 30)
            
            plan = query_interface.query_business_scenario(query)
            
            print(f"📋 Generated Plan: {plan.scenario_title}")
            for step in plan.steps:
                print(f"  {step.step_id}. {step.description} [{step.action_type}]")
                print(f"     Query: {step.query_for_qwen}")
            
            print()
        
        # Explore state structure
        print("\n🗺️  Navigation Overview")
        print("=" * 50)
        nav_map = query_interface.get_navigation_graph()
        for state, connections in nav_map.items():
            print(f"\n{state}:")
            for conn in connections[:3]:  # Show first 3 connections
                print(f"  → {conn['action']} {conn['component']} → {conn['destination']}")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
    finally:
        kg.close()


if __name__ == "__main__":
    demo_query_interface()