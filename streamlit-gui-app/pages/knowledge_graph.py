"""
Knowledge Graph Explorer page module
"""

import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
from typing import List, Tuple
from utils.ui_components import UIComponents
from utils.session_manager import SessionManager
from utils.caching import cached_function, PerformanceMonitor
from utils.logging_config import logger
from config.settings import settings

class KnowledgeGraphPage:
    """Handles the Knowledge Graph Explorer tab functionality"""
    
    @staticmethod
    @PerformanceMonitor.time_function("render_kg_page")
    def render():
        """Render the complete knowledge graph page"""
        UIComponents.render_section_header("Interactive Knowledge Graph")
        
        if SessionManager.is_connected():
            KnowledgeGraphPage._render_graph_interface()
        else:
            UIComponents.render_error_message("Cannot visualize graph without Neo4j connection")
        
        KnowledgeGraphPage._render_cypher_query_interface()
    
    @staticmethod
    def _render_graph_interface():
        """Render the graph visualization interface"""
        col1, col2 = st.columns([3, 1])
        
        with col2:
            controls = KnowledgeGraphPage._render_visualization_controls()
        
        with col1:
            KnowledgeGraphPage._render_graph_visualization(controls)
    
    @staticmethod
    def _render_visualization_controls() -> dict:
        """Render visualization controls and return settings"""
        UIComponents.render_subsection_header("🎛️ Visualization Controls")
        
        # Refresh button
        if st.button("🔄 Refresh Graph", help="Reload graph data from Neo4j", key="refresh_graph"):
            KnowledgeGraphPage._clear_graph_cache()
            st.rerun()
        
        # Control options
        controls = {
            'show_components': st.checkbox("Show Components", value=True, 
                                         help="Display UI components connected to states",
                                         key="show_components"),
            'show_state_transitions': st.checkbox("Show State Transitions", value=True,
                                                help="Display action relationships between states",
                                                key="show_transitions"),
            'layout_type': st.selectbox("Layout Algorithm", 
                                      options=["force-directed", "hierarchical", "circular"],
                                      index=0,
                                      help="Choose how nodes are positioned",
                                      key="layout_type"),
            'node_physics': st.checkbox("Enable Physics", value=True,
                                      help="Allow nodes to move and stabilize automatically",
                                      key="node_physics")
        }
        
        return controls
    
    @staticmethod
    @cached_function(ttl=300)  # Cache for 5 minutes
    def _get_knowledge_graph_data() -> Tuple[List[Node], List[Edge]]:
        """Get knowledge graph data with caching"""
        return KnowledgeGraphPage._fetch_graph_data()
    
    @staticmethod
    def _fetch_graph_data() -> Tuple[List[Node], List[Edge]]:
        """Fetch graph data from Neo4j"""
        nodes = []
        edges = []
        
        kg = SessionManager.get('kg')
        if not kg:
            return nodes, edges
        
        try:
            with kg.get_session() as session:
                # Get all states (Razzmatazz colored nodes)
                result = session.run("MATCH (s:State) RETURN s.name as name ORDER BY s.name")
                states = [record['name'] for record in result]
                
                # Create state nodes
                for state_name in states:
                    nodes.append(Node(
                        id=state_name,
                        label=state_name.replace('Page', '\nPage'),
                        size=30,
                        color=settings.ui.primary_color,
                        shape='dot',
                        font={'color': settings.ui.text_color}
                    ))
                
                # Get all unique components (Splash colored nodes)
                result = session.run("""
                    MATCH (c:Component) 
                    RETURN DISTINCT c.id as id, c.name as name, c.component_type as type 
                    ORDER BY c.name
                """)
                components = list(result)
                
                for comp_record in components:
                    comp_id = comp_record['id'] 
                    comp_name = comp_record['name']
                    
                    if comp_name and comp_id:
                        nodes.append(Node(
                            id=comp_id,
                            label=comp_name,
                            size=20,
                            color=settings.ui.secondary_color,
                            shape='dot',
                            font={'color': settings.ui.text_color}
                        ))
                
                # Get HAS_COMPONENT relationships
                result = session.run("""
                    MATCH (s:State)-[:HAS_COMPONENT]->(c:Component)
                    RETURN s.name as state_name, c.id as component_id
                """)
                
                for record in result:
                    state_name = record['state_name']
                    component_id = record['component_id']
                    
                    if component_id:
                        edges.append(Edge(
                            source=state_name,
                            target=component_id,
                            color=settings.ui.text_color,
                            width=1
                        ))
                
                # Get action relationships
                result = session.run("""
                    MATCH (c:Component)-[r]->(s:State)
                    WHERE type(r) IN ['TAP', 'SWIPE', 'SCROLL', 'TYPE']
                    RETURN c.id as component_id, type(r) as action_type, s.name as target_state
                """)
                
                for record in result:
                    component_id = record['component_id']
                    action_type = record['action_type']
                    target_state = record['target_state']
                    
                    if component_id:
                        edge_color = {
                            'TAP': settings.ui.primary_color,
                            'SWIPE': settings.ui.secondary_color,
                            'SCROLL': settings.ui.text_color,
                            'TYPE': settings.ui.primary_color
                        }.get(action_type, settings.ui.text_color)
                        
                        edges.append(Edge(
                            source=component_id,
                            target=target_state,
                            label=action_type,
                            color=edge_color,
                            width=2
                        ))
                        
        except Exception as e:
            logger.error(f"Error retrieving graph data: {e}")
            UIComponents.render_error_message("Error loading graph data", str(e))
        
        return nodes, edges
    
    @staticmethod
    def _render_graph_visualization(controls: dict):
        """Render the interactive graph visualization"""
        with UIComponents.render_loading_spinner("Loading knowledge graph..."):
            nodes, edges = KnowledgeGraphPage._get_knowledge_graph_data()
            
            if not nodes:
                st.warning("No graph data available to visualize")
                return
            
            # Apply filters
            if not controls['show_components']:
                state_nodes = [n for n in nodes if 'Page' in n.id]
                state_edges = [e for e in edges if 'Page' in e.source and 'Page' in e.target]
                nodes, edges = state_nodes, state_edges
            
            if not controls['show_state_transitions']:
                edges = [e for e in edges if not hasattr(e, 'label') or e.label == '' or e.width == 1]
            
            # Configure graph
            config = KnowledgeGraphPage._get_graph_config(controls)
            
            # Display graph
            selected_node = agraph(nodes=nodes, edges=edges, config=config)
            
            # Show statistics
            KnowledgeGraphPage._render_graph_statistics(nodes, edges)
            
            # Show selected node info
            if selected_node:
                KnowledgeGraphPage._render_node_details(selected_node)
    
    @staticmethod
    def _get_graph_config(controls: dict) -> Config:
        """Get graph configuration based on controls"""
        base_config = {
            "width": 1000,
            "height": 700,
            "directed": True,
            "hierarchical": controls['layout_type'] == "hierarchical",
            "nodeHighlightBehavior": True,
            "highlightColor": settings.ui.secondary_color,
            "collapsible": False,
            "backgroundColor": settings.ui.background_color
        }
        
        if controls['node_physics']:
            base_config.update({
                "physics": {
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
            })
        else:
            base_config["physics"] = False
        
        return Config(**base_config)
    
    @staticmethod
    def _render_graph_statistics(nodes: List[Node], edges: List[Edge]):
        """Render graph statistics"""
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
    
    @staticmethod
    def _render_node_details(selected_node: str):
        """Render details for selected node"""
        st.subheader(f"Selected: {selected_node}")
        
        kg = SessionManager.get('kg')
        if not kg:
            return
        
        try:
            with kg.get_session() as session:
                if 'Page' in selected_node:
                    # This is a state
                    KnowledgeGraphPage._render_state_details(session, selected_node)
                else:
                    # This is a component
                    KnowledgeGraphPage._render_component_details(session, selected_node)
                    
        except Exception as e:
            logger.error(f"Error getting node details: {e}")
            UIComponents.render_error_message("Error loading node details", str(e))
    
    @staticmethod
    def _render_state_details(session, state_name: str):
        """Render state details"""
        st.info(f"🏠 State: **{state_name}**")
        
        result = session.run("""
            MATCH (s:State {name: $state_name})-[:HAS_COMPONENT]->(c:Component)
            RETURN c.name as component_name, c.component_type as component_type
        """, {"state_name": state_name})
        
        components = list(result)
        if components:
            st.markdown("**Available Components:**")
            for comp in components:
                comp_type_icon = {
                    'button': '🔴', 'input': '🔵', 
                    'navigation': '🟣', 'display': '🟢'
                }.get(comp['component_type'], '⚪')
                st.markdown(f"- {comp_type_icon} **{comp['component_name']}** ({comp['component_type']})")
    
    @staticmethod
    def _render_component_details(session, component_id: str):
        """Render component details"""
        result = session.run("""
            MATCH (c:Component {id: $component_id})
            RETURN c.name as component_name, c.component_type as component_type
        """, {"component_id": component_id})
        
        comp_info = result.single()
        if comp_info:
            comp_name = comp_info['component_name']
            comp_type = comp_info['component_type']
            st.info(f"🔧 Component: **{comp_name}** ({comp_type})")
            
            # Show states containing this component
            result = session.run("""
                MATCH (s:State)-[:HAS_COMPONENT]->(c:Component {id: $component_id})
                RETURN s.name as state_name
            """, {"component_id": component_id})
            
            states = [record['state_name'] for record in result]
            if states:
                st.markdown("**Found in States:**")
                for state in states:
                    st.markdown(f"- 🏠 {state}")
    
    @staticmethod
    def _render_cypher_query_interface():
        """Render the Cypher query interface"""
        st.markdown("---")
        UIComponents.render_subsection_header("🔍 Cypher Query", settings.ui.text_color)
        
        col_query1, col_query2 = st.columns([3, 1])
        
        with col_query1:
            cypher_query = st.text_area(
                "Enter Cypher Query:",
                value="MATCH (s:State)-[:HAS_COMPONENT]->(c:Component) RETURN s.name, c.name, c.component_type LIMIT 10",
                height=100,
                key="cypher_query"
            )
        
        with col_query2:
            st.markdown("**Quick Queries:**")
            if st.button("All States", key="query_states"):
                st.session_state.cypher_query = "MATCH (s:State) RETURN s.name ORDER BY s.name"
                st.rerun()
            if st.button("All Components", key="query_components"):
                st.session_state.cypher_query = "MATCH (c:Component) RETURN c.name, c.component_type"
                st.rerun()
            if st.button("Action Paths", key="query_actions"):
                st.session_state.cypher_query = "MATCH (c:Component)-[r]->(s:State) RETURN c.name, type(r), s.name LIMIT 20"
                st.rerun()
        
        if st.button("Execute Query", key="execute_query"):
            KnowledgeGraphPage._execute_cypher_query(cypher_query)
    
    @staticmethod
    def _execute_cypher_query(query: str):
        """Execute a Cypher query and display results"""
        kg = SessionManager.get('kg')
        if not kg:
            UIComponents.render_error_message("No database connection available")
            return
        
        with UIComponents.render_loading_spinner("Querying Neo4j..."):
            try:
                with kg.get_session() as session:
                    result = session.run(query)
                    data = [dict(record) for record in result]
                    
                    if data:
                        st.dataframe(data, use_container_width=True)
                    else:
                        st.info("Query returned no results")
                        
            except Exception as e:
                UIComponents.render_error_message("Query error", str(e))
    
    @staticmethod
    def _clear_graph_cache():
        """Clear graph data cache"""
        # Clear the cached function results
        if hasattr(st.session_state, 'cache_get_knowledge_graph_data'):
            delattr(st.session_state, 'cache_get_knowledge_graph_data')
        logger.info("Cleared graph data cache")