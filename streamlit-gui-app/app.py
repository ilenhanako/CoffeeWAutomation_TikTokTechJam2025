#!/usr/bin/env python3
"""
Production-Ready Knowledge Graph GUI Testing Tool - Streamlit Web Interface

This is a refactored, production-ready version of the GUI testing tool with:
- Modular architecture
- Comprehensive error handling
- Performance optimizations
- Configuration management
- Logging system
- Caching mechanisms
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

# Import configuration and core modules
from config.settings import settings
from utils.logging_config import setup_logging, logger
from utils.session_manager import SessionManager
from utils.ui_components import UIComponents
from utils.caching import PerformanceMonitor
from services.database_manager import DatabaseManager

# Import page modules
from pages.query_generation import QueryGenerationPage
from pages.knowledge_graph import KnowledgeGraphPage
from pages.scenario_management import ScenarioManagementPage

class GUITestingApp:
    """Main application class for the GUI Testing Tool"""
    
    def __init__(self):
        """Initialize the application"""
        self.setup_application()
    
    def setup_application(self):
        """Set up the Streamlit application"""
        # Configure Streamlit page
        st.set_page_config(**settings.get_page_config())
        
        # Apply theme CSS
        st.markdown(settings.get_theme_css(), unsafe_allow_html=True)
        
        # Setup logging
        setup_logging(
            log_level="DEBUG" if settings.app.debug else "INFO",
            log_file="logs/app.log" if not settings.app.debug else None
        )
        
        logger.info(f"Starting GUI Testing Tool v{settings.app.version}")
    
    @PerformanceMonitor.time_function("app_initialization")
    def initialize_session(self):
        """Initialize session state and connections"""
        # Initialize session state
        SessionManager.initialize_session_state()
        
        # Initialize database connection if not already connected
        if not SessionManager.is_connected():
            with st.spinner("Initializing database connection..."):
                success, message = DatabaseManager.initialize_connection()
                
                if success:
                    # Initialize business scenarios
                    scenario_success, scenario_message = DatabaseManager.initialize_business_scenarios()
                    if scenario_success:
                        logger.info("Application initialized successfully")
                    else:
                        logger.warning(f"Scenarios initialization issue: {scenario_message}")
                else:
                    logger.error(f"Database connection failed: {message}")
    
    def render_header(self):
        """Render the application header"""
        UIComponents.render_header()
    
    def render_sidebar(self):
        """Render the sidebar with system status and controls"""
        with st.sidebar:
            UIComponents.render_connection_status(
                SessionManager.get('connection_status'),
                SessionManager.get('scenarios_initialized', False)
            )
            
            # Connection refresh button
            if st.button("🔄 Refresh Connection", key="refresh_connection"):
                with st.spinner("Refreshing connection..."):
                    DatabaseManager.refresh_connection()
                st.rerun()
            
            # Debug information (if enabled)
            if settings.app.debug:
                self._render_debug_sidebar()
    
    def _render_debug_sidebar(self):
        """Render debug information in sidebar"""
        with st.expander("🔧 Debug Info"):
            st.write("**Session State Keys:**")
            st.write(list(st.session_state.keys()))
            
            st.write("**Database Stats:**")
            try:
                stats = DatabaseManager.get_database_stats()
                if stats:
                    st.json(stats)
                else:
                    st.write("No database connection")
            except Exception as e:
                st.write(f"Error: {e}")
    
    def render_main_content(self):
        """Render the main application content"""
        # Check if we can proceed
        issues = SessionManager.validate_session_state()
        
        if issues:
            self._render_connection_issues(issues)
            return
        
        # Main tabbed interface
        tab1, tab2, tab3 = st.tabs([
            "🔍 Query & Test Generation", 
            "🕸️ Knowledge Graph Explorer", 
            "📋 Scenario Management"
        ])
        
        with tab1:
            QueryGenerationPage.render()
        
        with tab2:
            KnowledgeGraphPage.render()
        
        with tab3:
            ScenarioManagementPage.render()
    
    def _render_connection_issues(self, issues: dict):
        """Render connection issues and troubleshooting"""
        st.error("❌ Cannot proceed due to connection issues:")
        
        for component, issue in issues.items():
            st.error(f"• {component}: {issue}")
        
        st.markdown("### 🔧 Troubleshooting:")
        st.markdown("""
        1. **Check Neo4j Database:**
           - Ensure Neo4j is running on the configured port
           - Verify username and password are correct
           - Check network connectivity
        
        2. **Check Configuration:**
           - Review database URI in settings
           - Ensure knowledge graph components are available
        
        3. **Retry Connection:**
           - Use the "Refresh Connection" button in the sidebar
           - Restart the application if issues persist
        """)
        
        # Manual connection test
        with st.expander("🧪 Test Connection Manually"):
            col1, col2 = st.columns(2)
            
            with col1:
                test_uri = st.text_input("Database URI", value=settings.database.uri)
                test_user = st.text_input("Username", value=settings.database.username)
            
            with col2:
                test_pass = st.text_input("Password", type="password", value="")
                
                if st.button("Test Connection", type="primary"):
                    if test_pass:
                        success, message = DatabaseManager.test_connection(test_uri, test_user, test_pass)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                    else:
                        st.warning("Please enter password")
    
    @PerformanceMonitor.time_function("full_app_render")
    def run(self):
        """Main application run method"""
        try:
            # Initialize the session
            self.initialize_session()
            
            # Render application components
            self.render_header()
            self.render_sidebar()
            self.render_main_content()
            
            # Footer
            self._render_footer()
            
        except Exception as e:
            logger.error(f"Application error: {e}")
            st.error(f"❌ Application error: {str(e)}")
            
            if settings.app.debug:
                st.exception(e)
    
    def _render_footer(self):
        """Render application footer"""
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"**Version:** {settings.app.version}")
        
        with col2:
            if SessionManager.is_connected():
                st.markdown("**Status:** 🟢 Connected")
            else:
                st.markdown("**Status:** 🔴 Disconnected")
        
        with col3:
            if settings.app.debug:
                st.markdown("**Mode:** 🔧 Debug")
            else:
                st.markdown("**Mode:** 🚀 Production")

# Application entry point
def main():
    """Main application entry point"""
    try:
        app = GUITestingApp()
        app.run()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        st.stop()
        
    except Exception as e:
        logger.critical(f"Critical application error: {e}")
        st.error("❌ Critical application error. Please check logs and restart.")
        
        if settings.app.debug:
            st.exception(e)
        
        st.stop()
    
    finally:
        # Cleanup on exit
        try:
            DatabaseManager.close_connection()
            logger.info("Application cleanup completed")
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")

if __name__ == "__main__":
    main()