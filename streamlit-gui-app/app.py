#!/usr/bin/env python3
"""
Knowledge Graph GUI Testing Tool - Streamlit Web Interface
"""

import streamlit as st
import json
import time
import sys
import os
from typing import List, Dict, Any, Optional
from streamlit_agraph import agraph, Node, Edge, Config

# Add the knowledge graph package to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'knowledge-graph'))

# Import our knowledge graph components
from src.graph.neo4j_knowledge_graph import Neo4jKnowledgeGraph
from src.graph.query_interface import GraphQueryInterface
from src.models.ontology import ScenarioPlan, ExecutorStep

# Configure Streamlit page
st.set_page_config(
    page_title="GUI Testing Tool",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for theme styling
st.markdown("""
<style>
    /* Global theme colors */
    .main {
        background-color: #000000;
        color: #FFFFFF;
    }
    
    /* Streamlit specific overrides */
    .stButton > button {
        background-color: #FE2C55;
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background-color: #25F4EE;
        color: #000000;
        border: none;
    }
    
    .stSelectbox > div > div {
        background-color: #1a1a1a;
        color: #FFFFFF;
        border: 1px solid #4A4A4A;
    }
    
    .stTextArea > div > div > textarea {
        background-color: #1a1a1a;
        color: #FFFFFF;
        border: 1px solid #4A4A4A;
    }
    
    .stTextInput > div > div > input {
        background-color: #1a1a1a;
        color: #FFFFFF;
        border: 1px solid #4A4A4A;
    }
    
    .stExpander {
        background-color: #1a1a1a;
        border: 1px solid #4A4A4A;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1a1a;
        color: #4A4A4A;
        border: 1px solid #4A4A4A;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #FE2C55 !important;
        color: #FFFFFF !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1a1a1a;
    }
    
    /* Success/Error message styling */
    .stAlert > div {
        background-color: #25F4EE;
        color: #000000;
        border: none;
    }
    
    /* Metric styling */
    .metric-container {
        background-color: #1a1a1a;
        border: 1px solid #25F4EE;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'kg' not in st.session_state:
        try:
            st.session_state.kg = Neo4jKnowledgeGraph(
                uri="bolt://localhost:7687",
                username="neo4j", 
                password="tiktoktechjam"
            )
            st.session_state.query_interface = GraphQueryInterface(st.session_state.kg)
            st.session_state.connection_status = "connected"
            
            # Check if business scenarios are already in persistent ChromaDB
            with st.spinner("🔍 Checking business scenarios in ChromaDB..."):
                try:
                    # Try to query existing scenarios to see if they're already loaded
                    similar_scenarios = st.session_state.kg.find_similar_business_scenarios("test query", top_k=1)
                    
                    if similar_scenarios:
                        st.session_state.scenarios_initialized = True
                        st.info("✅ Found existing business scenarios in persistent ChromaDB")
                    else:
                        # Initialize business scenarios if none found
                        with st.spinner("📚 Loading business scenarios into ChromaDB..."):
                            st.session_state.query_interface.add_sample_business_scenarios()
                            st.session_state.scenarios_initialized = True
                            st.success("✅ Business scenarios loaded into persistent ChromaDB")
                            
                except Exception as scenario_e:
                    st.warning(f"⚠️ Error checking scenarios: {scenario_e}")
                    # Fallback: try to initialize scenarios
                    try:
                        st.session_state.query_interface.add_sample_business_scenarios()
                        st.session_state.scenarios_initialized = True
                    except Exception as init_e:
                        st.error(f"❌ Failed to initialize scenarios: {init_e}")
                        st.session_state.scenarios_initialized = False
                    
        except Exception as e:
            st.session_state.connection_status = f"error: {str(e)}"
            st.session_state.kg = None
            st.session_state.query_interface = None
    
    if 'current_plan' not in st.session_state:
        st.session_state.current_plan = None
    
    if 'neo4j_uri' not in st.session_state:
        st.session_state.neo4j_uri = "bolt://localhost:7687"
        st.session_state.neo4j_user = "neo4j"
        st.session_state.neo4j_pass = "tiktoktechjam"

def check_connection_status():
    """Check and display Neo4j connection status with theme colors"""
    if st.session_state.connection_status == "connected":
        st.sidebar.markdown("""
        <div style='background-color: #FE2C55; color: #FFFFFF; padding: 10px; border-radius: 5px; margin: 10px 0;'>
            <strong>🟢 Neo4j Connected</strong>
        </div>
        """, unsafe_allow_html=True)
        
        # Show business scenario status
        if st.session_state.get('scenarios_initialized', False):
            st.sidebar.markdown("""
            <div style='background-color: #25F4EE; color: #000000; padding: 10px; border-radius: 5px; margin: 10px 0;'>
                <strong>📚 Business Scenarios Loaded</strong>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.sidebar.markdown("""
            <div style='background-color: #FE2C55; color: #FFFFFF; padding: 10px; border-radius: 5px; margin: 10px 0;'>
                <strong>⚠️ Business Scenarios Not Loaded</strong>
            </div>
            """, unsafe_allow_html=True)
            
    else:
        st.sidebar.markdown(f"""
        <div style='background-color: #FE2C55; color: #FFFFFF; padding: 10px; border-radius: 5px; margin: 10px 0;'>
            <strong>🔴 Neo4j Error:</strong><br>{st.session_state.connection_status}
        </div>
        """, unsafe_allow_html=True)
        return False
    return True

def format_plan_as_text(plan: ScenarioPlan) -> str:
    """Format a scenario plan as readable text"""
    text = f"Test Plan: {plan.scenario_title}\n"
    text += "=" * 50 + "\n\n"
    
    for step in plan.steps:
        text += f"Step {step.step_id}: {step.description}\n"
        text += f"  Action: {step.action_type.upper()}\n"
        text += f"  Query: {step.query_for_qwen}\n"
        if step.expected_state:
            text += f"  Expected Result: {step.expected_state}\n"
        text += "\n"
    
    return text


def get_knowledge_graph_data(kg):
    """Retrieve knowledge graph structure for visualization matching Neo4j Browser"""
    nodes = []
    edges = []
    
    try:
        with kg.get_session() as session:
            # Get all states (yellow nodes in Neo4j Browser)
            result = session.run("MATCH (s:State) RETURN s.name as name ORDER BY s.name")
            states = [record['name'] for record in result]
            
            # Create state nodes with Razzmatazz color and white text
            for state_name in states:
                nodes.append(Node(
                    id=state_name,
                    label=state_name.replace('Page', '\nPage'),  # Line break for better display
                    size=30,
                    color='#FE2C55',  # Razzmatazz color for state nodes
                    shape='dot',
                    font={'color': '#FFFFFF'}  # White text for state labels
                ))
            
            # Get all unique components (light green nodes in Neo4j Browser)
            # Use component ID to avoid duplicates since same component can exist in multiple states  
            result = session.run("MATCH (c:Component) RETURN DISTINCT c.id as id, c.name as name, c.component_type as type ORDER BY c.name")
            components = list(result)
            
            for comp_record in components:
                comp_id = comp_record['id'] 
                comp_name = comp_record['name']
                comp_type = comp_record['type']
                
                if comp_name and comp_id:  # Skip empty component names or IDs
                    nodes.append(Node(
                        id=comp_id,  # Use unique component ID instead of name
                        label=comp_name,  # Display name as label
                        size=20,
                        color='#25F4EE',  # Splash color for component nodes
                        shape='dot',
                        font={'color': '#FFFFFF'}  # White text for component labels
                    ))
            
            # Get HAS_COMPONENT relationships (state -> component connections)
            result = session.run("""
                MATCH (s:State)-[:HAS_COMPONENT]->(c:Component)
                RETURN s.name as state_name, c.id as component_id
            """)
            
            for record in result:
                state_name = record['state_name']
                component_id = record['component_id']
                
                if component_id:  # Skip empty component IDs
                    edges.append(Edge(
                        source=state_name,
                        target=component_id,  # Use component ID
                        # No label for HAS_COMPONENT relationships
                        color='#FFFFFF',  # White for HAS_COMPONENT relationships
                        width=1
                    ))
            
            # Get action relationships (component -> state transitions)
            result = session.run("""
                MATCH (c:Component)-[r]->(s:State)
                WHERE type(r) IN ['TAP', 'SWIPE', 'SCROLL', 'TYPE']
                RETURN c.id as component_id, type(r) as action_type, s.name as target_state
            """)
            
            for record in result:
                component_id = record['component_id']
                action_type = record['action_type']
                target_state = record['target_state']
                
                if component_id:  # Skip empty component IDs
                    # Use theme colors for action types
                    edge_color = {
                        'TAP': '#FE2C55',      # Razzmatazz
                        'SWIPE': '#25F4EE',    # Splash  
                        'SCROLL': '#FFFFFF',   # White
                        'TYPE': '#FE2C55'      # Razzmatazz
                    }.get(action_type, '#FFFFFF')  # Default to white
                    
                    edges.append(Edge(
                        source=component_id,  # Use component ID
                        target=target_state,
                        label=action_type,
                        color=edge_color,
                        width=2
                    ))
                    
    except Exception as e:
        st.error(f"Error retrieving graph data: {e}")
        
    return nodes, edges


# Initialize the app
def main():
    """Main Streamlit application"""
    
    # Initialize session state
    initialize_session_state()
    
    # App header with theme colors
    st.markdown("""
    <div style='text-align: center; padding: 20px 0;'>
        <h1 style='color: #FE2C55; font-size: 48px; margin-bottom: 10px;'>🤖 Bombotest GUI Test</h1>
        <p style='color: #FFFFFF; font-size: 18px; margin: 0;'>Generate automated test steps from natural language scenarios</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Connection status in sidebar with theme colors
    with st.sidebar:
        st.markdown("<h2 style='color: #FE2C55;'>System Status</h2>", unsafe_allow_html=True)
        check_connection_status()
        
        if st.button("🔄 Refresh Connection"):
            # Clear connection and reinitialize
            for key in ['kg', 'query_interface', 'connection_status']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    # Check connection before showing main interface
    if st.session_state.connection_status != "connected":
        st.error("❌ Cannot proceed without Neo4j connection. Please check your database settings.")
        st.stop()
    
    # Main tabbed interface
    tab1, tab2, tab3 = st.tabs([
        "🔍 Query & Test Generation", 
        "🕸️ Knowledge Graph Explorer", 
        "📋 Scenario Management"
    ])
    
    with tab1:
        # === QUERY & TEST GENERATION TAB ===
        st.markdown("<h3 style='color: #FE2C55;'>Generate Test Steps from Natural Language</h3>", unsafe_allow_html=True)
        
        # Query input section
        col1, col2 = st.columns([3, 1])
        
        with col1:
            query = st.text_area(
                "Describe your testing scenario:",
                placeholder="Examples:\n• Navigate from ForYou page to settings\n• Update my username from homepage\n• Like a video on STEM page",
                height=100,
                help="Use natural language to describe what the user wants to accomplish"
            )
        
        with col2:
            start_state = st.selectbox(
                "Starting State:",
                options=["HomePage", "ForYouPage", "STEMPage", "ExplorePage", 
                        "FollowingPage", "FriendsPage", "ProfilePage", "SettingsPage"],
                help="Select where the user begins their journey"
            )
            
            # Advanced options
            with st.expander("Advanced Options"):
                debug_mode = st.checkbox("Show Debug Info", False)

        # Execute button and status display
        col_btn, col_status = st.columns([1, 1])
        
        with col_btn:
            generate_clicked = st.button("🚀 Generate Test Steps", type="primary", use_container_width=True)
        
        with col_status:
            status_placeholder = st.empty()
        
        if generate_clicked:
            if query.strip():
                with st.spinner("Analyzing scenario and generating test steps..."):
                    try:
                        # Execute the query
                        scenario_plan = st.session_state.query_interface.query_business_scenario(query, start_state)
                        st.session_state.current_plan = scenario_plan
                        
                        if scenario_plan and scenario_plan.steps:
                            status_placeholder.success(f"✅ Generated {len(scenario_plan.steps)} test steps!")
                        else:
                            status_placeholder.warning("⚠️ No test steps could be generated. Try rephrasing your scenario.")
                            
                            # Show additional debug info
                            if scenario_plan:
                                st.info(f"Plan title: {scenario_plan.scenario_title}")
                                st.info("Plan object exists but has no steps")
                            else:
                                st.error("No plan object returned from query interface")
                            
                            # Test basic connectivity
                            st.info("🔧 Testing basic connectivity...")
                            try:
                                with st.session_state.kg.get_session() as session:
                                    result = session.run("MATCH (n) RETURN count(n) as total")
                                    total_nodes = result.single()['total']
                                    st.info(f"Total nodes in graph: {total_nodes}")
                                    
                                    # Test states specifically
                                    result = session.run("MATCH (s:State) RETURN s.name as state_name")
                                    states = [record['state_name'] for record in result]
                                    st.info(f"Available states: {states}")
                                    
                            except Exception as conn_e:
                                st.error(f"Database connectivity test failed: {str(conn_e)}")
                            
                    except Exception as e:
                        st.error(f"❌ Error generating test steps: {str(e)}")
                        st.exception(e)  # Always show exception details for debugging
            else:
                st.error("Please enter a test scenario description")


        # === EXECUTOR STEP VISUALIZATION ===
        if 'current_plan' in st.session_state and st.session_state.current_plan and st.session_state.current_plan.steps:
            # Test Plan header with theme colors
            st.markdown(f"""
            <div style='color: #FE2C55; font-size: 24px; font-weight: bold; margin: 20px 0;'>
                📋 Test Plan: <span style='color: #FFFFFF;'>{st.session_state.current_plan.scenario_title}</span>
            </div>
            """, unsafe_allow_html=True)
            
            
            # All steps in one combined area with theme colors
            st.markdown("""
            <div style='background-color: #1a1a1a; padding: 20px; border-radius: 10px; border: 2px solid #25F4EE; margin: 20px 0;'>
            """, unsafe_allow_html=True)
            
            for i, step in enumerate(st.session_state.current_plan.steps):
                # Action type color mapping
                action_color_mapping = {
                    'tap': '#FE2C55',    # Razzmatazz
                    'swipe': '#25F4EE',  # Splash
                    'scroll': '#FFFFFF', # White
                    'type': '#FE2C55'    # Razzmatazz
                }
                
                action_bg_color = action_color_mapping.get(step.action_type.lower(), '#FFFFFF')
                text_color = '#000000' if action_bg_color == '#FFFFFF' else '#FFFFFF'
                
                # Compact step display with all info in one line
                expected_result = step.expected_state if step.expected_state else "Stay in current state"
                
                # Alternate border colors between steps
                border_color = '#FE2C55' if i % 2 == 0 else '#25F4EE'
                
                step_content = f"""
                <div style='margin: 15px 0; padding: 15px; background-color: #2a2a2a; border-radius: 8px; border-left: 4px solid {border_color};'>
                    <div style='display: flex; align-items: center; flex-wrap: wrap; gap: 15px;'>
                        <div style='color: #FFFFFF; font-weight: bold; font-size: 16px;'>
                            Step {step.step_id}: {step.description}
                        </div>
                        <div style='background-color: {action_bg_color}; color: {text_color}; padding: 6px 12px; border-radius: 15px; font-size: 12px; font-weight: bold;'>
                            {step.action_type.upper()}
                        </div>
                    </div>
                    <div style='margin-top: 10px; color: #FFFFFF; font-style: italic;'>
                        {step.query_for_qwen}
                    </div>
                    <div style='margin-top: 10px; color: {border_color}; font-size: 14px;'>
                        <strong>Expected:</strong> <span style='color: #FFFFFF;'>{expected_result}</span>
                    </div>
                </div>
                """
                
                st.markdown(step_content, unsafe_allow_html=True)
                
                # Add flow arrow except for last step
                if i < len(st.session_state.current_plan.steps) - 1:
                    st.markdown("<div style='text-align: center; color: #FE2C55; font-size: 20px; margin: 10px 0;'>⬇️</div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            

    with tab2:
        # === KNOWLEDGE GRAPH EXPLORER TAB ===
        st.markdown("<h3 style='color: #FE2C55;'>Interactive Knowledge Graph</h3>", unsafe_allow_html=True)
        
        # Graph visualization controls
        col1, col2 = st.columns([3, 1])
        
        with col2:
            st.markdown("<h4 style='color: #4A4A4A;'>🎛️ Visualization Controls</h4>", unsafe_allow_html=True)
            
            # Add refresh button
            if st.button("🔄 Refresh Graph", help="Reload graph data from Neo4j"):
                # Clear any cached graph data
                if 'graph_data_cache' in st.session_state:
                    del st.session_state.graph_data_cache
                st.rerun()
            
            show_components = st.checkbox("Show Components", value=True, 
                                        help="Display UI components connected to states")
            
            show_state_transitions = st.checkbox("Show State Transitions", value=True,
                                                help="Display action relationships between states")
            
            layout_type = st.selectbox("Layout Algorithm", 
                                     options=["force-directed", "hierarchical", "circular"],
                                     index=0,
                                     help="Choose how nodes are positioned")
            
            node_physics = st.checkbox("Enable Physics", value=True,
                                     help="Allow nodes to move and stabilize automatically")
        
        with col1:
            if st.session_state.connection_status == "connected":
                with st.spinner("🔍 Loading knowledge graph..."):
                    try:
                        # Always fetch fresh data to ensure accuracy
                        nodes, edges = get_knowledge_graph_data(st.session_state.kg)
                        
                        if not show_components:
                            # Filter out component nodes and their edges
                            # State nodes have 'Page' in their name, components don't
                            state_nodes = [n for n in nodes if 'Page' in n.id]
                            # Keep only edges between states
                            state_edges = [e for e in edges if 'Page' in e.source and 'Page' in e.target]
                            nodes, edges = state_nodes, state_edges
                        
                        if not show_state_transitions:
                            # Filter out action transition edges (TAP, SWIPE, etc.)
                            # Keep only HAS_COMPONENT relationships (edges without labels or with width=1)
                            edges = [e for e in edges if not hasattr(e, 'label') or e.label == '' or e.width == 1]
                        
                        # Configure the graph appearance with better spacing
                        if node_physics:
                            config = Config(
                                width=1000, 
                                height=700, 
                                directed=True,
                                hierarchical=layout_type == "hierarchical",
                                nodeHighlightBehavior=True,
                                highlightColor="#25F4EE",  # Splash color for highlights
                                collapsible=False,
                                backgroundColor="#000000",  # Black background
                                # Enhanced physics for better spacing
                                physics={
                                    "enabled": True,
                                    "forceAtlas2Based": {
                                        "gravitationalConstant": -26,
                                        "centralGravity": 0.005,
                                        "springLength": 230,
                                        "springConstant": 0.18,
                                        "damping": 0.15,
                                        "avoidOverlap": 1.5
                                    },
                                    "maxVelocity": 146,
                                    "solver": "forceAtlas2Based",
                                    "timestep": 0.35,
                                    "stabilization": {"iterations": 150}
                                }
                            )
                        else:
                            config = Config(
                                width=1000, 
                                height=700, 
                                directed=True,
                                physics=False,
                                hierarchical=layout_type == "hierarchical",
                                nodeHighlightBehavior=True,
                                highlightColor="#25F4EE",  # Splash color for highlights
                                collapsible=False,
                                backgroundColor="#000000"  # Black background
                            )
                        
                        if nodes and edges:
                            # Display the interactive graph
                            selected_node = agraph(nodes=nodes, edges=edges, config=config)
                            
                            # Show graph statistics
                            st.markdown("---")
                            col_stats1, col_stats2, col_stats3 = st.columns(3)
                            
                            with col_stats1:
                                states_count = len([n for n in nodes if 'Page' in n.id])
                                st.metric("States", states_count)
                            
                            with col_stats2:
                                components_count = len([n for n in nodes if 'Page' not in n.id])
                                st.metric("Components", components_count)
                            
                            with col_stats3:
                                st.metric("Relationships", len(edges))
                            
                            # Show selected node info
                            if selected_node:
                                st.subheader(f"Selected: {selected_node}")
                                
                                # Get details about the selected node
                                if 'Page' in selected_node:
                                    # This is a state
                                    st.info(f"🏠 State: **{selected_node}**")
                                    
                                    # Show components connected to this state
                                    with st.session_state.kg.get_session() as session:
                                        result = session.run("""
                                            MATCH (s:State {name: $state_name})-[:HAS_COMPONENT]->(c:Component)
                                            RETURN c.name as component_name, c.component_type as component_type
                                        """, {"state_name": selected_node})
                                        
                                        components = list(result)
                                        if components:
                                            st.markdown("**Available Components:**")
                                            for comp in components:
                                                comp_type_icon = {
                                                    'button': '🔴', 'input': '🔵', 
                                                    'navigation': '🟣', 'display': '🟢'
                                                }.get(comp['component_type'], '⚪')
                                                st.markdown(f"- {comp_type_icon} **{comp['component_name']}** ({comp['component_type']})")
                                else:
                                    # This is a component (selected_node is component ID)
                                    # Get component details
                                    with st.session_state.kg.get_session() as session:
                                        result = session.run("""
                                            MATCH (c:Component {id: $component_id})
                                            RETURN c.name as component_name, c.component_type as component_type
                                        """, {"component_id": selected_node})
                                        
                                        comp_info = result.single()
                                        if comp_info:
                                            comp_name = comp_info['component_name']
                                            comp_type = comp_info['component_type']
                                            st.info(f"🔧 Component: **{comp_name}** ({comp_type})")
                                            
                                            # Show which states contain this component
                                            result = session.run("""
                                                MATCH (s:State)-[:HAS_COMPONENT]->(c:Component {id: $component_id})
                                                RETURN s.name as state_name
                                            """, {"component_id": selected_node})
                                            
                                            states = [record['state_name'] for record in result]
                                            if states:
                                                st.markdown("**Found in States:**")
                                                for state in states:
                                                    st.markdown(f"- 🏠 {state}")
                                            
                                            # Show actions available on this component
                                            result = session.run("""
                                                MATCH (c:Component {id: $component_id})-[r]->(target:State)
                                                RETURN type(r) as action_type, target.name as target_state,
                                                       r.query_for_qwen as query_description
                                            """, {"component_id": selected_node})
                                            
                                            actions = list(result)
                                            if actions:
                                                st.markdown("**Available Actions:**")
                                                for action in actions:
                                                    action_type = action['action_type']
                                                    target_state = action['target_state']
                                                    query_desc = action.get('query_for_qwen', 'No description')
                                                    
                                                    action_color = {
                                                        'TAP': '🔴', 'SWIPE': '🔵', 
                                                        'SCROLL': '🟠', 'TYPE': '🟣'
                                                    }.get(action_type, '⚪')
                                                    
                                                    st.markdown(f"- {action_color} **{action_type}** → {target_state}")
                                                    if query_desc and query_desc != 'No description':
                                                        st.markdown(f"  _{query_desc}_")
                                        else:
                                            st.info(f"🔧 Component: **{selected_node}** (details not found)")
                        else:
                            st.warning("No graph data available to visualize")
                            
                    except Exception as e:
                        st.error(f"Error loading knowledge graph: {e}")
                        st.exception(e)
            else:
                st.error("❌ Cannot visualize graph without Neo4j connection")
        
        # Advanced query interface
        st.markdown("---")
        st.markdown("<h4 style='color: #FFFFFF;'>🔍 Cypher Query</h4>", unsafe_allow_html=True)
        
        col_query1, col_query2 = st.columns([3, 1])
        
        with col_query1:
            cypher_query = st.text_area(
                "Enter Cypher Query:",
                value="MATCH (s:State)-[:HAS_COMPONENT]->(c:Component) RETURN s.name, c.name, c.component_type LIMIT 10",
                height=100
            )
        
        with col_query2:
            st.markdown("**Quick Queries:**")
            if st.button("All States"):
                st.session_state.quick_query = "MATCH (s:State) RETURN s.name ORDER BY s.name"
            if st.button("All Components"):
                st.session_state.quick_query = "MATCH (c:Component) RETURN c.name, c.component_type"
            if st.button("Action Paths"):
                st.session_state.quick_query = "MATCH (c:Component)-[r]->(s:State) RETURN c.name, type(r), s.name LIMIT 20"
        
        # Use quick query if selected
        if 'quick_query' in st.session_state:
            cypher_query = st.session_state.quick_query
            del st.session_state.quick_query
        
        if st.button("Execute Query"):
            with st.spinner("Querying Neo4j..."):
                try:
                    with st.session_state.kg.get_session() as session:
                        result = session.run(cypher_query)
                        data = [dict(record) for record in result]
                        
                        if data:
                            st.dataframe(data, use_container_width=True)
                        else:
                            st.info("Query returned no results")
                            
                except Exception as e:
                    st.error(f"Query error: {str(e)}")

    with tab3:
        # === SCENARIO MANAGEMENT TAB ===
        st.markdown("<h3 style='color: #FE2C55;'>Business Scenario Library</h3>", unsafe_allow_html=True)
        
        # Tab sub-navigation for scenario management
        scenario_tab1, scenario_tab2, scenario_tab3 = st.tabs([
            "📚 Browse Scenarios",
            "➕ Add New Scenario", 
            "📤 Import/Export"
        ])
        
        with scenario_tab1:
            # === BROWSE SCENARIOS ===
            st.markdown("<h4 style='color: #4A4A4A;'>📚 Browse Existing Scenarios</h4>", unsafe_allow_html=True)
            
            if st.session_state.connection_status == "connected":
                try:
                    # Import the business scenarios
                    import sys
                    import os
                    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'knowledge-graph'))
                    from src.scenarios.business_scenarios import get_all_business_scenarios
                    from src.models.scenario import ScenarioType
                    
                    # Get all scenarios
                    all_scenarios = get_all_business_scenarios()
                    
                    # Filters
                    col_filter1, col_filter2, col_filter3 = st.columns(3)
                    
                    with col_filter1:
                        # Feature filter
                        features = list(set([s.feature for s in all_scenarios]))
                        selected_feature = st.selectbox("Filter by Feature:", ["All"] + sorted(features))
                    
                    with col_filter2:
                        # Scenario type filter
                        scenario_types = [t.value for t in ScenarioType]
                        selected_type = st.selectbox("Filter by Type:", ["All"] + scenario_types)
                    
                    with col_filter3:
                        # Tag filter
                        all_tags = set()
                        for s in all_scenarios:
                            all_tags.update(s.tags)
                        selected_tag = st.selectbox("Filter by Tag:", ["All"] + sorted(list(all_tags)))
                    
                    # Apply filters
                    filtered_scenarios = all_scenarios
                    if selected_feature != "All":
                        filtered_scenarios = [s for s in filtered_scenarios if s.feature == selected_feature]
                    if selected_type != "All":
                        filtered_scenarios = [s for s in filtered_scenarios if s.scenario_type == selected_type]
                    if selected_tag != "All":
                        filtered_scenarios = [s for s in filtered_scenarios if selected_tag in s.tags]
                    
                    # Search functionality
                    search_query = st.text_input("🔍 Search scenarios:", placeholder="Search by title, feature, or goal...")
                    if search_query:
                        filtered_scenarios = [s for s in filtered_scenarios if 
                                            search_query.lower() in s.title.lower() or 
                                            search_query.lower() in s.feature.lower() or
                                            search_query.lower() in s.goal.lower()]
                    
                    st.markdown(f"**Found {len(filtered_scenarios)} scenarios**")
                    
                    # Display scenarios
                    if filtered_scenarios:
                        for i, scenario in enumerate(filtered_scenarios):
                            # Alternate colors for scenario cards
                            border_color = '#FE2C55' if i % 2 == 0 else '#25F4EE'
                            
                            with st.expander(f"#{scenario.id} - {scenario.title}"):
                                st.markdown(f"""
                                <div style='padding: 15px; background-color: #2a2a2a; border-radius: 8px; border-left: 4px solid {border_color};'>
                                    <div style='color: #FE2C55; font-weight: bold; margin-bottom: 10px;'>
                                        📋 {scenario.feature}
                                    </div>
                                    <div style='color: #FFFFFF; margin-bottom: 10px;'>
                                        <strong>Goal:</strong> {scenario.goal}
                                    </div>
                                    <div style='color: #25F4EE; margin-bottom: 10px;'>
                                        <strong>Type:</strong> {scenario.scenario_type}
                                    </div>
                                    <div style='color: #FFFFFF; margin-bottom: 10px;'>
                                        <strong>Given:</strong> {', '.join(scenario.given_conditions)}
                                    </div>
                                    <div style='color: #FFFFFF; margin-bottom: 10px;'>
                                        <strong>When:</strong> {', '.join(scenario.when_actions)}
                                    </div>
                                    <div style='color: #FFFFFF; margin-bottom: 10px;'>
                                        <strong>Then:</strong> {', '.join(scenario.then_expectations)}
                                    </div>
                                    <div style='color: #FFFFFF;'>
                                        <strong>Tags:</strong> {', '.join(scenario.tags)}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info("No scenarios found matching your filters.")
                        
                except Exception as e:
                    st.error(f"Error loading scenarios: {str(e)}")
            else:
                st.error("❌ Cannot load scenarios without Neo4j connection")
        
        with scenario_tab2:
            # === ADD NEW SCENARIO ===
            st.markdown("<h4 style='color: #4A4A4A;'>➕ Add New Business Scenario</h4>", unsafe_allow_html=True)
            
            with st.form("new_scenario_form"):
                col_basic1, col_basic2 = st.columns(2)
                
                with col_basic1:
                    new_title = st.text_input("Scenario Title *", placeholder="e.g., Navigate to user profile")
                    new_feature = st.text_input("Feature *", placeholder="e.g., Profile Page Navigation")
                    new_goal = st.text_input("Goal *", placeholder="e.g., Access user profile information")
                
                with col_basic2:
                    new_type = st.selectbox("Scenario Type", ["feature", "regression", "edge_case", "performance"])
                    new_tags = st.text_input("Tags (comma-separated)", placeholder="e.g., profile, navigation, user")
                
                # Scenario steps
                st.markdown("**Scenario Steps:**")
                new_given = st.text_area("Given Conditions", placeholder="e.g., I am logged in, I am on main page")
                new_when = st.text_area("When Actions", placeholder="e.g., I tap Profile tab, I navigate to user profile")
                new_then = st.text_area("Then Expectations", placeholder="e.g., Profile page loads, User info is displayed")
                
                # Submit button
                col_submit, col_reset = st.columns(2)
                with col_submit:
                    submitted = st.form_submit_button("💾 Save Scenario", type="primary", use_container_width=True)
                with col_reset:
                    st.form_submit_button("🔄 Clear Form", use_container_width=True)
                
                if submitted:
                    if new_title and new_feature and new_goal:
                        # Create new scenario object
                        try:
                            from src.models.scenario import BusinessScenario, ScenarioType
                            
                            new_scenario = BusinessScenario(
                                title=new_title,
                                feature=new_feature,
                                goal=new_goal,
                                scenario_type=ScenarioType(new_type),
                                given_conditions=[g.strip() for g in new_given.split(',') if g.strip()],
                                when_actions=[w.strip() for w in new_when.split(',') if w.strip()],
                                then_expectations=[t.strip() for t in new_then.split(',') if t.strip()],
                                tags=[tag.strip() for tag in new_tags.split(',') if tag.strip()]
                            )
                            
                            st.success("✅ Scenario saved successfully!")
                            st.json(new_scenario.model_dump())
                            st.info("💡 Note: This is a demo. In production, scenarios would be saved to the database.")
                            
                        except Exception as e:
                            st.error(f"Error creating scenario: {str(e)}")
                    else:
                        st.error("Please fill in all required fields (marked with *)")
        
        with scenario_tab3:
            # === IMPORT/EXPORT ===
            st.markdown("<h4 style='color: #4A4A4A;'>📤 Import/Export Scenarios</h4>", unsafe_allow_html=True)
            
            # Export section
            st.markdown("**📤 Export Scenarios**")
            col_export1, col_export2 = st.columns(2)
            
            with col_export1:
                if st.button("📄 Export All Scenarios (JSON)", use_container_width=True):
                    try:
                        from src.scenarios.business_scenarios import get_all_business_scenarios
                        all_scenarios = get_all_business_scenarios()
                        scenarios_data = [s.model_dump() for s in all_scenarios]
                        
                        import json
                        json_data = json.dumps(scenarios_data, indent=2)
                        
                        st.download_button(
                            "💾 Download JSON File",
                            json_data,
                            "business_scenarios.json",
                            "application/json",
                            use_container_width=True
                        )
                        
                        st.success(f"✅ Ready to download {len(all_scenarios)} scenarios")
                    except Exception as e:
                        st.error(f"Export error: {str(e)}")
            
            with col_export2:
                if st.button("📊 Export Summary (CSV)", use_container_width=True):
                    try:
                        from src.scenarios.business_scenarios import get_all_business_scenarios
                        import pandas as pd
                        
                        all_scenarios = get_all_business_scenarios()
                        
                        # Create summary data
                        summary_data = []
                        for s in all_scenarios:
                            summary_data.append({
                                'ID': s.id,
                                'Title': s.title,
                                'Feature': s.feature,
                                'Goal': s.goal,
                                'Type': s.scenario_type,
                                'Tags': ', '.join(s.tags),
                                'Steps Count': len(s.given_conditions) + len(s.when_actions) + len(s.then_expectations)
                            })
                        
                        df = pd.DataFrame(summary_data)
                        csv_data = df.to_csv(index=False)
                        
                        st.download_button(
                            "💾 Download CSV File",
                            csv_data,
                            "scenarios_summary.csv",
                            "text/csv",
                            use_container_width=True
                        )
                        
                        st.success(f"✅ Ready to download summary for {len(all_scenarios)} scenarios")
                    except Exception as e:
                        st.error(f"Export error: {str(e)}")
            
            st.divider()
            
            # Import section
            st.markdown("**📥 Import Scenarios**")
            uploaded_file = st.file_uploader("Choose a JSON file", type="json")
            
            if uploaded_file is not None:
                try:
                    import json
                    file_content = uploaded_file.read()
                    scenarios_data = json.loads(file_content)
                    
                    if isinstance(scenarios_data, list):
                        st.success(f"✅ Found {len(scenarios_data)} scenarios in file")
                        
                        # Preview first few scenarios
                        with st.expander("🔍 Preview Import Data"):
                            for i, scenario_data in enumerate(scenarios_data[:3]):  # Show first 3
                                st.json(scenario_data)
                                if i >= 2:
                                    st.info(f"... and {len(scenarios_data) - 3} more scenarios")
                                    break
                        
                        if st.button("📥 Import Scenarios", type="primary"):
                            st.info("💡 Note: This is a demo. In production, scenarios would be imported to the database.")
                            st.success("✅ Import completed successfully!")
                    else:
                        st.error("❌ Invalid JSON format. Expected a list of scenarios.")
                        
                except Exception as e:
                    st.error(f"Import error: {str(e)}")
            
            # Statistics
            st.divider()
            st.markdown("**📊 Scenario Statistics**")
            
            try:
                from src.scenarios.business_scenarios import get_all_business_scenarios
                all_scenarios = get_all_business_scenarios()
                
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                
                with col_stat1:
                    st.markdown(f"""
                    <div style='background-color: #FE2C55; color: #FFFFFF; padding: 15px; border-radius: 8px; text-align: center;'>
                        <div style='font-size: 24px; font-weight: bold;'>{len(all_scenarios)}</div>
                        <div style='font-size: 14px; margin-top: 5px;'>Total Scenarios</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_stat2:
                    features = set([s.feature for s in all_scenarios])
                    st.markdown(f"""
                    <div style='background-color: #25F4EE; color: #000000; padding: 15px; border-radius: 8px; text-align: center;'>
                        <div style='font-size: 24px; font-weight: bold;'>{len(features)}</div>
                        <div style='font-size: 14px; margin-top: 5px;'>Features Covered</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_stat3:
                    all_tags = set()
                    for s in all_scenarios:
                        all_tags.update(s.tags)
                    st.markdown(f"""
                    <div style='background-color: #FE2C55; color: #FFFFFF; padding: 15px; border-radius: 8px; text-align: center;'>
                        <div style='font-size: 24px; font-weight: bold;'>{len(all_tags)}</div>
                        <div style='font-size: 14px; margin-top: 5px;'>Unique Tags</div>
                    </div>
                    """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error loading statistics: {str(e)}")
        

if __name__ == "__main__":
    main()