"""
Query and Test Generation page module
"""

import streamlit as st
from utils.ui_components import UIComponents
from utils.session_manager import SessionManager
from services.scenario_service import ScenarioService
from services.automation_service import AutomationService
from utils.status_monitor import StreamlitStatusMonitor
from utils.caching import PerformanceMonitor
from utils.logging_config import logger

class QueryGenerationPage:
    """Handles the Query & Test Generation tab functionality"""
    
    @staticmethod
    @PerformanceMonitor.time_function("render_query_page")
    def render():
        """Render the complete query generation page"""
        UIComponents.render_section_header("Generate Test Steps from Natural Language")
        
        # Query input section
        QueryGenerationPage._render_query_input()
        
        # Results section
        if SessionManager.has_current_plan():
            QueryGenerationPage._render_results()
    
    @staticmethod
    def _render_query_input():
        """Render the query input section"""
        col1, col2 = st.columns([3, 1])
        
        with col1:
            query = st.text_area(
                "Describe your testing scenario:",
                placeholder="Examples:\n• Navigate from ForYou page to settings\n• Update my username from homepage\n• Like a video on STEM page",
                height=100,
                help="Use natural language to describe what the user wants to accomplish",
                key="query_input"
            )
        
        with col2:
            start_state = st.selectbox(
                "Starting State:",
                options=["HomePage", "ForYouPage", "STEMPage", "ExplorePage", 
                        "FollowingPage", "FriendsPage", "ProfilePage", "SettingsPage"],
                help="Select where the user begins their journey",
                key="start_state_input"
            )
            
            # Advanced options
            with st.expander("Advanced Options"):
                st.checkbox("Show Debug Info", False, key="debug_mode")
        
        # Execute button and status
        QueryGenerationPage._render_query_execution_controls(query, start_state)
    
    @staticmethod
    def _render_query_execution_controls(query: str, start_state: str):
        """Render execution controls and handle query processing"""
        col_btn, col_status = st.columns([1, 1])
        
        with col_btn:
            generate_clicked = st.button(
                "🚀 Generate Test Steps", 
                type="primary", 
                use_container_width=True,
                key="generate_button"
            )
        
        with col_status:
            status_placeholder = st.empty()
        
        if generate_clicked:
            QueryGenerationPage._process_query(query, start_state, status_placeholder)
    
    @staticmethod
    @PerformanceMonitor.time_function("process_query")
    def _process_query(query: str, start_state: str, status_placeholder):
        """Process the query and generate test steps"""
        with UIComponents.render_loading_spinner("Analyzing scenario and generating test steps..."):
            success, scenario_plan, message = ScenarioService.generate_test_steps(query, start_state)
            
            if success:
                status_placeholder.success(f"✅ {message}")
                logger.info(f"Successfully generated test plan: {scenario_plan.scenario_title}")
                
                # Show debug info if enabled
                if st.session_state.get('debug_mode', False):
                    QueryGenerationPage._show_debug_info(query, start_state, scenario_plan)
            
            else:
                status_placeholder.error(f"❌ {message}")
                
                # Show connectivity test if no steps generated
                if scenario_plan is None:
                    QueryGenerationPage._show_connectivity_test()
    
    @staticmethod
    def _show_debug_info(query: str, start_state: str, scenario_plan):
        """Show debug information"""
        with st.expander("🔍 Processing Details"):
            st.json({
                "query": query,
                "start_state": start_state,
                "plan_generated": scenario_plan is not None,
                "steps_count": len(scenario_plan.steps) if scenario_plan else 0,
                "plan_title": scenario_plan.scenario_title if scenario_plan else None
            })
    
    @staticmethod
    def _show_connectivity_test():
        """Show connectivity test information"""
        st.info("🔧 Testing basic connectivity...")
        
        kg = SessionManager.get('kg')
        if kg:
            try:
                with kg.get_session() as session:
                    result = session.run("MATCH (n) RETURN count(n) as total")
                    total_nodes = result.single()['total']
                    st.info(f"Total nodes in graph: {total_nodes}")
                    
                    # Test states specifically
                    result = session.run("MATCH (s:State) RETURN s.name as state_name")
                    states = [record['state_name'] for record in result]
                    st.info(f"Available states: {states}")
                    
            except Exception as conn_e:
                UIComponents.render_error_message("Database connectivity test failed", str(conn_e))
    
    @staticmethod
    def _render_results():
        """Render the test generation results"""
        current_plan = SessionManager.get('current_plan')
        if not current_plan or not current_plan.steps:
            return
        
        # Test Plan header
        st.markdown(f"""
        <div style='color: #FE2C55; font-size: 24px; font-weight: bold; margin: 20px 0;'>
            📋 Test Plan: <span style='color: #FFFFFF;'>{current_plan.scenario_title}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Steps container
        st.markdown("""
        <div style='background-color: #1a1a1a; padding: 20px; border-radius: 10px; border: 2px solid #25F4EE; margin: 20px 0;'>
        """, unsafe_allow_html=True)
        
        # Render each step
        for i, step in enumerate(current_plan.steps):
            UIComponents.render_step_card(step, i)
            
            # Add flow arrow except for last step
            if i < len(current_plan.steps) - 1:
                st.markdown(
                    "<div style='text-align: center; color: #FE2C55; font-size: 20px; margin: 10px 0;'>⬇️</div>", 
                    unsafe_allow_html=True
                )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Add execution controls
        QueryGenerationPage._render_execution_controls(current_plan)
    
    @staticmethod
    def _render_execution_controls(current_plan):
        """Render automation execution controls and monitoring UI"""
        st.markdown("---")
        
        # Execution section header
        st.markdown("""
        <div style='color: #25F4EE; font-size: 20px; font-weight: bold; margin: 20px 0;'>
            🚀 Execute Automation Testing
        </div>
        """, unsafe_allow_html=True)
        
        # Check automation service health
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("🔍 Check Service Health", use_container_width=True):
                with st.spinner("Checking automation service..."):
                    is_healthy, status_message = AutomationService.check_automation_service_health()
                    if is_healthy:
                        st.success(status_message)
                    else:
                        st.error(status_message)
        
        with col2:
            start_state = st.selectbox(
                "Starting State:",
                options=["HomePage", "ForYouPage", "STEMPage", "ExplorePage", 
                        "FollowingPage", "FriendsPage", "ProfilePage", "SettingsPage"],
                key="execution_start_state"
            )
        
        with col3:
            show_monitoring = st.checkbox(
                "Show Status Monitoring", 
                value=True,
                help="Display execution status after starting automation"
            )
        
        # Execute button
        col_execute, col_status = st.columns([1, 2])
        
        with col_execute:
            execute_clicked = st.button(
                "Execute Automation",
                type="primary",
                use_container_width=True,
                key="execute_automation"
            )
        
        with col_status:
            status_placeholder = st.empty()
        
        # Handle execution
        if execute_clicked:
            QueryGenerationPage._handle_automation_execution(
                current_plan, 
                start_state, 
                show_monitoring, 
                status_placeholder
            )
        
        # Show monitoring UI if monitoring is enabled and execution is active
        current_execution_id = SessionManager.get('current_execution_id')
        if show_monitoring and current_execution_id:
            StreamlitStatusMonitor.render_execution_status(current_execution_id)
    
    @staticmethod
    def _handle_automation_execution(current_plan, start_state: str, show_monitoring: bool, status_placeholder):
        """Handle automation execution"""
        with st.spinner("Starting automation execution..."):
            # Execute the scenario
            success, message, response_data = AutomationService.execute_scenario(current_plan, start_state)
            
            if success:
                status_placeholder.success(message)
                execution_id = response_data.get('execution_id')
                SessionManager.set('current_execution_id', execution_id)
                
                # Refresh to show monitoring UI if enabled
                if show_monitoring:
                    st.rerun()
                    
            else:
                status_placeholder.error(message)
                
                # Show troubleshooting info
                with st.expander("🔧 Troubleshooting"):
                    st.markdown("""
                    **Common Issues:**
                    
                    1. **Service Not Running**: Start the FastAPI automation service:
                       ```bash
                       cd test-automation
                       python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
                       ```
                    
                    2. **Port Conflicts**: Ensure port 8000 is available
                    
                    3. **Configuration**: Check automation service URL in settings
                    
                    4. **Dependencies**: Ensure all automation dependencies are installed
                    """)
    
