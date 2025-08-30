"""
Scenario Management page module
"""

import streamlit as st
import json
from typing import List, Dict, Any
from utils.ui_components import UIComponents
from utils.session_manager import SessionManager
from services.scenario_service import ScenarioService
from utils.caching import PerformanceMonitor, get_scenarios_with_cache
from utils.logging_config import logger

class ScenarioManagementPage:
    """Handles the Scenario Management tab functionality"""
    
    @staticmethod
    @PerformanceMonitor.time_function("render_scenario_page")
    def render():
        """Render the complete scenario management page"""
        UIComponents.render_section_header("Business Scenario Library")
        
        # Sub-tab navigation
        scenario_tab1, scenario_tab2, scenario_tab3 = st.tabs([
            "📚 Browse Scenarios",
            "➕ Add New Scenario", 
            "📤 Import/Export"
        ])
        
        with scenario_tab1:
            ScenarioManagementPage._render_browse_scenarios()
        
        with scenario_tab2:
            ScenarioManagementPage._render_add_scenario()
        
        with scenario_tab3:
            ScenarioManagementPage._render_import_export()
    
    @staticmethod
    def _render_browse_scenarios():
        """Render the browse scenarios tab"""
        UIComponents.render_subsection_header("📚 Browse Existing Scenarios")
        
        if not SessionManager.is_connected():
            UIComponents.render_error_message("Cannot load scenarios without Neo4j connection")
            return
        
        try:
            # Get filter options
            filter_options = get_scenarios_with_cache()
            
            # Render filter controls
            filters = ScenarioManagementPage._render_scenario_filters(filter_options)
            
            # Search and filter scenarios
            scenarios = ScenarioService.search_scenarios(
                feature_filter=filters['feature'],
                type_filter=filters['type'],
                tag_filter=filters['tag'],
                search_query=filters['search']
            )
            
            st.markdown(f"**Found {len(scenarios)} scenarios**")
            
            # Display scenarios
            if scenarios:
                ScenarioManagementPage._render_scenario_list(scenarios)
            else:
                st.info("No scenarios found matching your filters.")
                
        except Exception as e:
            logger.error(f"Error loading scenarios: {e}")
            UIComponents.render_error_message("Error loading scenarios", str(e))
    
    @staticmethod
    def _render_scenario_filters(filter_options: Dict[str, List[str]]) -> Dict[str, str]:
        """Render scenario filter controls"""
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            selected_feature = st.selectbox(
                "Filter by Feature:", 
                ["All"] + filter_options.get("features", []),
                key="scenario_feature_filter"
            )
        
        with col_filter2:
            selected_type = st.selectbox(
                "Filter by Type:", 
                ["All"] + filter_options.get("types", []),
                key="scenario_type_filter"
            )
        
        with col_filter3:
            selected_tag = st.selectbox(
                "Filter by Tag:", 
                ["All"] + filter_options.get("tags", []),
                key="scenario_tag_filter"
            )
        
        search_query = st.text_input(
            "🔍 Search scenarios:", 
            placeholder="Search by title, feature, or goal...",
            key="scenario_search"
        )
        
        return {
            'feature': selected_feature,
            'type': selected_type,
            'tag': selected_tag,
            'search': search_query
        }
    
    @staticmethod
    def _render_scenario_list(scenarios: List[Any]):
        """Render the list of scenarios"""
        for i, scenario in enumerate(scenarios):
            with st.expander(f"#{scenario.id} - {scenario.title}"):
                UIComponents.render_scenario_card(scenario, i)
    
    @staticmethod
    def _render_add_scenario():
        """Render the add new scenario tab"""
        UIComponents.render_subsection_header("➕ Add New Business Scenario")
        
        with st.form("new_scenario_form"):
            # Basic information
            col_basic1, col_basic2 = st.columns(2)
            
            with col_basic1:
                new_title = st.text_input(
                    "Scenario Title *", 
                    placeholder="e.g., Navigate to user profile",
                    key="new_title"
                )
                new_feature = st.text_input(
                    "Feature *", 
                    placeholder="e.g., Profile Page Navigation",
                    key="new_feature"
                )
                new_goal = st.text_input(
                    "Goal *", 
                    placeholder="e.g., Access user profile information",
                    key="new_goal"
                )
            
            with col_basic2:
                new_type = st.selectbox(
                    "Scenario Type", 
                    ["feature", "regression", "edge_case", "performance"],
                    key="new_type"
                )
                new_tags = st.text_input(
                    "Tags (comma-separated)", 
                    placeholder="e.g., profile, navigation, user",
                    key="new_tags"
                )
            
            # Scenario steps
            st.markdown("**Scenario Steps:**")
            new_given = st.text_area(
                "Given Conditions", 
                placeholder="e.g., I am logged in, I am on main page",
                key="new_given"
            )
            new_when = st.text_area(
                "When Actions", 
                placeholder="e.g., I tap Profile tab, I navigate to user profile",
                key="new_when"
            )
            new_then = st.text_area(
                "Then Expectations", 
                placeholder="e.g., Profile page loads, User info is displayed",
                key="new_then"
            )
            
            # Submit buttons
            col_submit, col_reset = st.columns(2)
            with col_submit:
                submitted = st.form_submit_button(
                    "💾 Save Scenario", 
                    type="primary", 
                    use_container_width=True
                )
            with col_reset:
                st.form_submit_button("🔄 Clear Form", use_container_width=True)
            
            if submitted:
                ScenarioManagementPage._handle_scenario_creation({
                    'title': new_title,
                    'feature': new_feature,
                    'goal': new_goal,
                    'type': new_type,
                    'tags': new_tags,
                    'given': new_given,
                    'when': new_when,
                    'then': new_then
                })
    
    @staticmethod
    def _handle_scenario_creation(scenario_data: Dict[str, str]):
        """Handle the creation of a new scenario"""
        # Validate required fields
        if not all([scenario_data['title'], scenario_data['feature'], scenario_data['goal']]):
            UIComponents.render_error_message("Please fill in all required fields (marked with *)")
            return
        
        try:
            # Process the scenario data
            processed_data = {
                'title': scenario_data['title'],
                'feature': scenario_data['feature'],
                'goal': scenario_data['goal'],
                'scenario_type': scenario_data['type'],
                'given_conditions': [g.strip() for g in scenario_data['given'].split(',') if g.strip()],
                'when_actions': [w.strip() for w in scenario_data['when'].split(',') if w.strip()],
                'then_expectations': [t.strip() for t in scenario_data['then'].split(',') if t.strip()],
                'tags': [tag.strip() for tag in scenario_data['tags'].split(',') if tag.strip()]
            }
            
            success, message = ScenarioService.create_scenario(processed_data)
            
            if success:
                UIComponents.render_success_message(message, processed_data)
            else:
                UIComponents.render_error_message(message)
                
        except Exception as e:
            logger.error(f"Error creating scenario: {e}")
            UIComponents.render_error_message("Error creating scenario", str(e))
    
    @staticmethod
    def _render_import_export():
        """Render the import/export tab"""
        UIComponents.render_subsection_header("📤 Import/Export Scenarios")
        
        # Export section
        st.markdown("**📤 Export Scenarios**")
        col_export1, col_export2 = st.columns(2)
        
        with col_export1:
            if st.button("📄 Export All Scenarios (JSON)", use_container_width=True, key="export_json"):
                ScenarioManagementPage._handle_export("json")
        
        with col_export2:
            if st.button("📊 Export Summary (CSV)", use_container_width=True, key="export_csv"):
                ScenarioManagementPage._handle_export("csv")
        
        st.divider()
        
        # Import section
        st.markdown("**📥 Import Scenarios**")
        uploaded_file = st.file_uploader("Choose a JSON file", type="json", key="import_file")
        
        if uploaded_file is not None:
            ScenarioManagementPage._handle_import(uploaded_file)
        
        # Statistics
        st.divider()
        ScenarioManagementPage._render_statistics()
    
    @staticmethod
    def _handle_export(format_type: str):
        """Handle scenario export"""
        with UIComponents.render_loading_spinner(f"Exporting scenarios as {format_type.upper()}..."):
            success, data, message = ScenarioService.export_scenarios(format_type)
            
            if success:
                filename = f"business_scenarios.{format_type}"
                mime_type = "application/json" if format_type == "json" else "text/csv"
                
                st.download_button(
                    f"💾 Download {format_type.upper()} File",
                    data,
                    filename,
                    mime_type,
                    use_container_width=True,
                    key=f"download_{format_type}"
                )
                
                UIComponents.render_success_message(message)
            else:
                UIComponents.render_error_message(f"Export failed: {message}")
    
    @staticmethod
    def _handle_import(uploaded_file):
        """Handle scenario import"""
        try:
            file_content = uploaded_file.read()
            scenarios_data = json.loads(file_content)
            
            if isinstance(scenarios_data, list):
                UIComponents.render_success_message(f"Found {len(scenarios_data)} scenarios in file")
                
                # Preview first few scenarios
                with st.expander("🔍 Preview Import Data"):
                    for i, scenario_data in enumerate(scenarios_data[:3]):
                        st.json(scenario_data)
                        if i >= 2 and len(scenarios_data) > 3:
                            st.info(f"... and {len(scenarios_data) - 3} more scenarios")
                            break
                
                if st.button("📥 Import Scenarios", type="primary", key="import_confirm"):
                    st.info("💡 Note: This is a demo. In production, scenarios would be imported to the database.")
                    UIComponents.render_success_message("Import completed successfully!")
            else:
                UIComponents.render_error_message("Invalid JSON format. Expected a list of scenarios.")
                
        except json.JSONDecodeError as e:
            UIComponents.render_error_message("Invalid JSON file", str(e))
        except Exception as e:
            logger.error(f"Import error: {e}")
            UIComponents.render_error_message("Import failed", str(e))
    
    @staticmethod
    def _render_statistics():
        """Render scenario statistics"""
        st.markdown("**📊 Scenario Statistics**")
        
        try:
            stats = ScenarioService.get_scenario_statistics()
            
            if stats:
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                
                with col_stat1:
                    UIComponents.render_metric_card(
                        stats.get('total_scenarios', 0), 
                        "Total Scenarios"
                    )
                
                with col_stat2:
                    UIComponents.render_metric_card(
                        stats.get('features_covered', 0), 
                        "Features Covered",
                        color="#25F4EE"
                    )
                
                with col_stat3:
                    UIComponents.render_metric_card(
                        stats.get('unique_tags', 0), 
                        "Unique Tags"
                    )
            else:
                st.info("No statistics available")
                
        except Exception as e:
            logger.error(f"Error loading statistics: {e}")
            UIComponents.render_error_message("Error loading statistics", str(e))