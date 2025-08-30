"""
Reusable UI components for the Streamlit app
"""

import streamlit as st
import json
from typing import List, Dict, Any, Optional
from config.settings import settings
from utils.logging_config import logger

class UIComponents:
    """Collection of reusable UI components"""
    
    @staticmethod
    def render_header():
        """Render the main application header"""
        st.markdown(f"""
        <div style='text-align: center; padding: 20px 0;'>
            <h1 style='color: {settings.ui.primary_color}; font-size: 48px; margin-bottom: 10px;'>
                {settings.app.app_title}
            </h1>
            <p style='color: {settings.ui.text_color}; font-size: 18px; margin: 0;'>
                {settings.app.app_description}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_connection_status(connection_status: str, scenarios_initialized: bool):
        """Render connection status in sidebar"""
        st.sidebar.markdown(f"<h2 style='color: {settings.ui.primary_color};'>System Status</h2>", 
                          unsafe_allow_html=True)
        
        if connection_status == "connected":
            st.sidebar.markdown(f"""
            <div style='background-color: {settings.ui.primary_color}; color: {settings.ui.text_color}; 
                        padding: 10px; border-radius: 5px; margin: 10px 0;'>
                <strong>🟢 Neo4j Connected</strong>
            </div>
            """, unsafe_allow_html=True)
            
            # Show business scenario status
            if scenarios_initialized:
                st.sidebar.markdown(f"""
                <div style='background-color: {settings.ui.secondary_color}; color: {settings.ui.background_color}; 
                            padding: 10px; border-radius: 5px; margin: 10px 0;'>
                    <strong>📚 Business Scenarios Loaded</strong>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.sidebar.markdown(f"""
                <div style='background-color: {settings.ui.primary_color}; color: {settings.ui.text_color}; 
                            padding: 10px; border-radius: 5px; margin: 10px 0;'>
                    <strong>⚠️ Business Scenarios Not Loaded</strong>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.sidebar.markdown(f"""
            <div style='background-color: {settings.ui.primary_color}; color: {settings.ui.text_color}; 
                        padding: 10px; border-radius: 5px; margin: 10px 0;'>
                <strong>🔴 Neo4j Error:</strong><br>{connection_status}
            </div>
            """, unsafe_allow_html=True)
    
    @staticmethod
    def render_metric_card(value: Any, label: str, color: str = None) -> None:
        """Render a metric card with theme colors"""
        bg_color = color or (settings.ui.primary_color if label == "Total Steps" or "Action" in label 
                           else settings.ui.secondary_color)
        text_color = settings.ui.text_color if bg_color == settings.ui.primary_color else settings.ui.background_color
        
        st.markdown(f"""
        <div style='background-color: {bg_color}; color: {text_color}; 
                    padding: 15px; border-radius: 8px; text-align: center; margin: 10px 0;'>
            <div style='font-size: 24px; font-weight: bold;'>{value}</div>
            <div style='font-size: 14px; margin-top: 5px;'>{label}</div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_step_card(step, step_index: int) -> None:
        """Render an ExecutorStep as a styled card"""
        # Action type color mapping
        action_color_mapping = {
            'tap': settings.ui.primary_color,
            'swipe': settings.ui.secondary_color,
            'scroll': settings.ui.text_color,
            'type': settings.ui.primary_color
        }
        
        action_bg_color = action_color_mapping.get(step.action_type.lower(), settings.ui.text_color)
        text_color = settings.ui.background_color if action_bg_color == settings.ui.text_color else settings.ui.text_color
        
        # Alternate border colors between steps
        border_color = settings.ui.primary_color if step_index % 2 == 0 else settings.ui.secondary_color
        
        expected_result = step.expected_state if step.expected_state else "Stay in current state"
        
        
        step_content = f"""
        <div style='margin: 15px 0; padding: 15px; background-color: {settings.ui.card_background}; 
                    border-radius: 8px; border-left: 4px solid {border_color};'>
            <div style='display: flex; align-items: center; flex-wrap: wrap; gap: 15px;'>
                <div style='color: {settings.ui.text_color}; font-weight: bold; font-size: 16px;'>
                    Step {step.step_id}: {step.description}
                </div>
                <div style='background-color: {action_bg_color}; color: {text_color}; 
                            padding: 6px 12px; border-radius: 15px; font-size: 12px; font-weight: bold;'>
                    {step.action_type.upper()}
                </div>
            </div>
            <div style='margin-top: 10px; color: {settings.ui.text_color}; font-style: italic;'>
                {step.query_for_qwen}
            </div>
            <div style='margin-top: 10px; color: {border_color}; font-size: 14px;'>
                <strong>Expected:</strong> <span style='color: {settings.ui.text_color};'>{expected_result}</span>
            </div>
        </div>
        """
        
        st.markdown(step_content, unsafe_allow_html=True)
    
    @staticmethod
    def render_scenario_card(scenario, index: int) -> None:
        """Render a business scenario card"""
        border_color = settings.ui.primary_color if index % 2 == 0 else settings.ui.secondary_color
        
        st.markdown(f"""
        <div style='padding: 15px; background-color: {settings.ui.card_background}; 
                    border-radius: 8px; border-left: 4px solid {border_color};'>
            <div style='color: {settings.ui.primary_color}; font-weight: bold; margin-bottom: 10px;'>
                📋 {scenario.feature}
            </div>
            <div style='color: {settings.ui.text_color}; margin-bottom: 10px;'>
                <strong>Goal:</strong> {scenario.goal}
            </div>
            <div style='color: {settings.ui.secondary_color}; margin-bottom: 10px;'>
                <strong>Type:</strong> {scenario.scenario_type}
            </div>
            <div style='color: {settings.ui.text_color}; margin-bottom: 10px;'>
                <strong>Given:</strong> {', '.join(scenario.given_conditions)}
            </div>
            <div style='color: {settings.ui.text_color}; margin-bottom: 10px;'>
                <strong>When:</strong> {', '.join(scenario.when_actions)}
            </div>
            <div style='color: {settings.ui.text_color}; margin-bottom: 10px;'>
                <strong>Then:</strong> {', '.join(scenario.then_expectations)}
            </div>
            <div style='color: {settings.ui.text_color};'>
                <strong>Tags:</strong> {', '.join(scenario.tags)}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_error_message(message: str, details: Optional[str] = None):
        """Render a styled error message"""
        st.error(f"❌ {message}")
        
        if details and settings.app.debug:
            with st.expander("🔍 Error Details"):
                st.code(details)
    
    @staticmethod
    def render_success_message(message: str, details: Optional[Dict[str, Any]] = None):
        """Render a styled success message"""
        st.success(f"✅ {message}")
        
        if details:
            with st.expander("📊 Details"):
                st.json(details)
    
    @staticmethod
    def render_loading_spinner(text: str = "Processing..."):
        """Render a loading spinner with custom text"""
        return st.spinner(text)
    
    @staticmethod
    def render_section_header(title: str, color: str = None):
        """Render a section header with theme styling"""
        header_color = color or settings.ui.primary_color
        st.markdown(f"<h3 style='color: {header_color};'>{title}</h3>", unsafe_allow_html=True)
    
    @staticmethod
    def render_subsection_header(title: str, color: str = None):
        """Render a subsection header"""
        header_color = color or settings.ui.grey_color
        st.markdown(f"<h4 style='color: {header_color};'>{title}</h4>", unsafe_allow_html=True)
    
    @staticmethod
    def render_json_download_button(data: Dict[str, Any], filename: str, button_text: str = "📥 Download JSON"):
        """Render a download button for JSON data"""
        json_data = json.dumps(data, indent=2)
        return st.download_button(
            button_text,
            json_data,
            filename,
            "application/json",
            use_container_width=True
        )
    
    @staticmethod
    def render_filter_controls():
        """Render common filter controls for scenarios"""
        col1, col2, col3 = st.columns(3)
        
        filters = {}
        
        with col1:
            filters['feature'] = st.selectbox("Filter by Feature:", ["All"], key="feature_filter")
        
        with col2:
            filters['type'] = st.selectbox("Filter by Type:", ["All"], key="type_filter")
        
        with col3:
            filters['tag'] = st.selectbox("Filter by Tag:", ["All"], key="tag_filter")
        
        filters['search'] = st.text_input("🔍 Search scenarios:", 
                                        placeholder="Search by title, feature, or goal...",
                                        key="search_filter")
        
        return filters