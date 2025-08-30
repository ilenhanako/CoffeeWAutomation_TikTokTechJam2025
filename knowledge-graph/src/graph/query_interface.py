from typing import List, Dict, Any, Optional
from .neo4j_knowledge_graph import Neo4jKnowledgeGraph
from ..models.ontology import ScenarioPlan


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
        
        # Step 3: Extract keywords from query to find relevant paths
        query_keywords = self._extract_keywords(query)
        print(f"🎯 Extracted keywords: {query_keywords}")
        
        # Step 4: Find paths that reach the target (state or component)
        target_info = self._determine_target_state_or_component(query_keywords, query)
        print(f"🎯 Target: {target_info}")
        
        if target_info['type'] == 'component':
            # Target is a component within a state - need multi-step path
            target_state = target_info['parent_state']
            target_component = target_info['component']
            
            # Find path to the state containing the component
            if target_state != start_state:
                state_paths = self.kg.find_action_paths(start_state, target_state, max_depth=4)
                if state_paths:
                    print(f"🛤️  Found path to {target_state}, will add component access")
                    scenario_plan = self._generate_multi_step_plan_with_component(state_paths[0], target_component, goal)
                else:
                    print(f"⚠️  No path found to {target_state} for component {target_component}")
                    return ScenarioPlan(scenario_id=1, scenario_title=goal, steps=[])
            else:
                # Component is in current state
                print(f"🛤️  Target component {target_component} is in current state {start_state}")
                scenario_plan = self._generate_single_component_step(start_state, target_component, goal)
                
        elif target_info['type'] == 'state':
            # Target is a state - need path to that state
            target_state = target_info['state']
            if target_state != start_state:
                state_paths = self.kg.find_action_paths(start_state, target_state, max_depth=4)
                if state_paths:
                    print(f"🛤️  Found {len(state_paths)} paths to {target_state}")
                    scenario_plan = self._generate_multi_step_plan_from_path(state_paths[0], goal)
                else:
                    print(f"⚠️  No path found to {target_state}")
                    return ScenarioPlan(scenario_id=1, scenario_title=goal, steps=[])
            else:
                print(f"🛤️  Already at target state {target_state}")
                return ScenarioPlan(scenario_id=1, scenario_title=goal, steps=[])
        else:
            # Fallback to keyword-based search
            relevant_paths = self.find_paths_to_goal(start_state, query_keywords)
            if not relevant_paths:
                print(f"⚠️  No relevant paths found for keywords: {query_keywords}")
                return ScenarioPlan(scenario_id=1, scenario_title=goal, steps=[])
            
            print(f"🛤️  Found {len(relevant_paths)} relevant action paths")
            scenario_plan = self.kg.generate_executor_steps_from_paths([relevant_paths[0]], goal)
        
        print(f"✅ Generated plan with {len(scenario_plan.steps)} steps")
        return scenario_plan
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from query text"""
        text = text.lower()
        keywords = []
        
        # Define keyword mappings
        keyword_mappings = {
            'settings': ['settings', 'preferences', 'config', 'options', 'update', 'modify', 'change', 'edit', 'username', 'name', 'bio', 'links'],
            'profile': ['profile', 'account', 'personal'],
            'like': ['like', 'heart', 'favorite'],
            'comment': ['comment', 'reply', 'respond'],
            'share': ['share', 'send', 'forward'],
            'follow': ['follow', 'subscribe', 'connect'],
            'navigate': ['navigate', 'go', 'move', 'switch'],
            'home': ['home', 'homepage', 'main'],
            'stem': ['stem', 'education'],
            'explore': ['explore', 'discover', 'trending'],
            'following': ['following', 'feed'],
            'friends': ['friends', 'social']
        }
        
        # Extract keywords
        for keyword, synonyms in keyword_mappings.items():
            if any(synonym in text for synonym in synonyms):
                keywords.append(keyword)
        
        return keywords if keywords else ['navigate']  # Default fallback
    
    def _determine_target_state_or_component(self, keywords: List[str], query: str) -> Dict[str, Any]:
        """Determine if target is a state or component within a state"""
        query_lower = query.lower()
        
        # Check for specific components first
        component_mappings = {
            'followerslist': {'type': 'component', 'component': 'FollowersList', 'parent_state': 'ProfilePage'},
            'followinglist': {'type': 'component', 'component': 'FollowingList', 'parent_state': 'ProfilePage'},
            'followers': {'type': 'component', 'component': 'FollowersList', 'parent_state': 'ProfilePage'},
            'following': {'type': 'component', 'component': 'FollowingList', 'parent_state': 'ProfilePage'},
            'username': {'type': 'component', 'component': 'UserNameInput', 'parent_state': 'SettingsPage'},
            'name': {'type': 'component', 'component': 'NameInput', 'parent_state': 'SettingsPage'},
            'bio': {'type': 'component', 'component': 'BioInput', 'parent_state': 'SettingsPage'},
            'links': {'type': 'component', 'component': 'LinksInput', 'parent_state': 'SettingsPage'},
            'likebutton': {'type': 'component', 'component': 'LikeButton', 'parent_state': 'HomePage'},
            'commentbutton': {'type': 'component', 'component': 'CommentButton', 'parent_state': 'HomePage'},
            'sharebutton': {'type': 'component', 'component': 'ShareButton', 'parent_state': 'HomePage'},
        }
        
        # Check if query mentions specific components
        for component_key, info in component_mappings.items():
            if component_key in query_lower:
                return info
        
        # Check for state-level targets
        state_mappings = {
            'settings': {'type': 'state', 'state': 'SettingsPage'},
            'profile': {'type': 'state', 'state': 'ProfilePage'},
            'home': {'type': 'state', 'state': 'HomePage'},
        }
        
        for keyword in keywords:
            if keyword in state_mappings:
                return state_mappings[keyword]
        
        # Default fallback
        return {'type': 'unknown'}
    
    def _generate_multi_step_plan_from_path(self, path: Dict[str, Any], goal: str) -> ScenarioPlan:
        """Generate multi-step ExecutorSteps from a Neo4j path"""
        from ..models.ontology import ExecutorStep
        
        nodes = path.get('nodes', [])
        actions = path.get('actions', [])
        
        # Debug logging
        print(f"🔍 Path structure debug:")
        print(f"  Nodes: {[node.get('name', node.get('id', 'unknown')) for node in nodes]}")
        print(f"  Actions: {actions}")
        print(f"  Node details: {[(i, node.keys()) for i, node in enumerate(nodes)]}")
        
        if len(nodes) < 3:  # Need at least start -> component -> end
            return self.kg.generate_executor_steps_from_paths([path], goal)
        
        steps = []
        step_id = 1
        
        # Process path: identify components and their actions
        # Path structure: [StartState, Component1, MiddleState, Component2, EndState]
        # Actions structure: ['HAS_COMPONENT', 'TAP', 'HAS_COMPONENT', 'SWIPE']
        
        # Find actual action relationships and their corresponding components
        for i in range(len(actions)):
            if actions[i] in ['TAP', 'SWIPE', 'SCROLL', 'TYPE']:
                # The component is the node before this action
                # Find the component node that corresponds to this action
                
                # In a typical path: State -> (HAS_COMPONENT) -> Component -> (ACTION) -> State
                # The component should be at index i (same as action index for component actions)
                if i < len(nodes):
                    component = nodes[i]
                    action_type = actions[i]
                    
                    # Find the target state (next state node after this action)
                    end_state = None
                    for j in range(i + 1, len(nodes)):
                        if nodes[j].get('name') and not nodes[j].get('id'):  # State nodes don't have 'id', components do
                            end_state = nodes[j]
                            break
                    
                    # Only process if we have a component (should have 'id' field)
                    if component.get('id') or 'Button' in component.get('name', '') or 'Input' in component.get('name', '') or 'NavBar' in component.get('name', ''):
                        component_name = component.get('name', 'component')
                        description = f"{action_type.capitalize()} {component_name}"
                        
                        step = ExecutorStep(
                            step_id=step_id,
                            description=description,
                            action_type=action_type.lower(),
                            query_for_qwen=f"{action_type.capitalize()} on the {component_name.lower()}",
                            alternative_actions=[f"Long press {component_name.lower()}", f"Alternative {action_type.lower()} action"],
                            expected_state=end_state.get('name') if end_state else None
                        )
                        steps.append(step)
                        step_id += 1
        
        return ScenarioPlan(scenario_id=1, scenario_title=goal, steps=steps)
    
    def _generate_multi_step_plan_with_component(self, state_path: Dict[str, Any], target_component: str, goal: str) -> ScenarioPlan:
        """Generate multi-step plan: navigate to state + access component"""
        from ..models.ontology import ExecutorStep
        
        # First get steps to reach the state
        state_plan = self._generate_multi_step_plan_from_path(state_path, goal)
        
        # Then add step to access the target component
        final_step = ExecutorStep(
            step_id=len(state_plan.steps) + 1,
            description=f"Tap {target_component}",
            action_type='tap',
            query_for_qwen=f"Tap on the {target_component.lower()} to access it",
            alternative_actions=[f"Long press {target_component.lower()}", f"Swipe to access {target_component.lower()}"],
            expected_state=None  # Component access doesn't change state
        )
        
        state_plan.steps.append(final_step)
        return state_plan
    
    def _generate_single_component_step(self, current_state: str, target_component: str, goal: str) -> ScenarioPlan:
        """Generate single step to access component in current state"""
        from ..models.ontology import ExecutorStep
        
        step = ExecutorStep(
            step_id=1,
            description=f"Tap {target_component}",
            action_type='tap',
            query_for_qwen=f"Tap on the {target_component.lower()}",
            alternative_actions=[f"Long press {target_component.lower()}", f"Swipe to access {target_component.lower()}"],
            expected_state=current_state  # Stay in same state
        )
        
        return ScenarioPlan(scenario_id=1, scenario_title=goal, steps=[step])
    
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
        """Add all business scenarios from scenarios file to vector store"""
        from ..scenarios.business_scenarios import get_all_business_scenarios
        
        scenarios = get_all_business_scenarios()
        
        print(f"📚 Adding {len(scenarios)} business scenarios to vector store...")
        for scenario in scenarios:
            self.kg.add_business_scenario_to_vector_store(scenario)
        
        print(f"✅ Added {len(scenarios)} business scenarios covering:")
        features = list(set(s.feature for s in scenarios))
        for feature in sorted(features):
            count = len([s for s in scenarios if s.feature == feature])
            print(f"   - {feature}: {count} scenarios")
        
        print(f"📋 Total scenario types: {len(set(s.scenario_type for s in scenarios))}")
        print(f"🏷️  Total unique tags: {len(set(tag for s in scenarios for tag in s.tags))}")


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