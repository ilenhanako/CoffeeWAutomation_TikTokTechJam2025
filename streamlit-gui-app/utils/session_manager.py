"""
Session state management utilities for Streamlit app
"""

import streamlit as st
from typing import Any, Dict, Optional, Callable
from utils.logging_config import logger, ErrorContext

class SessionManager:
    """Manages Streamlit session state with type safety and validation"""
    
    @staticmethod
    def initialize_session_state() -> None:
        """Initialize all session state variables with default values"""
        defaults = {
            'kg': None,
            'query_interface': None,
            'connection_status': 'disconnected',
            'current_plan': None,
            'scenarios_initialized': False,
            'neo4j_uri': "bolt://localhost:7687",
            'neo4j_user': "neo4j", 
            'neo4j_pass': "tiktoktechjam",
            'planning_agent_data': None,
            'execution_data': None
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
                logger.debug(f"Initialized session state: {key} = {default_value}")
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """Safely get a value from session state"""
        return st.session_state.get(key, default)
    
    @staticmethod
    def set(key: str, value: Any) -> None:
        """Set a value in session state with logging"""
        old_value = st.session_state.get(key)
        st.session_state[key] = value
        logger.debug(f"Session state updated: {key} = {value} (was: {old_value})")
    
    @staticmethod
    def update(updates: Dict[str, Any]) -> None:
        """Update multiple session state values"""
        for key, value in updates.items():
            SessionManager.set(key, value)
    
    @staticmethod
    def clear_key(key: str) -> None:
        """Clear a specific session state key"""
        if key in st.session_state:
            del st.session_state[key]
            logger.debug(f"Cleared session state key: {key}")
    
    @staticmethod
    def reset_connection_state() -> None:
        """Reset connection-related session state"""
        keys_to_clear = ['kg', 'query_interface', 'connection_status', 'scenarios_initialized']
        for key in keys_to_clear:
            SessionManager.clear_key(key)
        logger.info("Reset connection state")
    
    @staticmethod
    def is_connected() -> bool:
        """Check if the application is connected to Neo4j"""
        return SessionManager.get('connection_status') == 'connected'
    
    @staticmethod
    def has_current_plan() -> bool:
        """Check if there's a current scenario plan"""
        plan = SessionManager.get('current_plan')
        return plan is not None and hasattr(plan, 'steps') and len(plan.steps) > 0
    
    @staticmethod
    def validate_session_state() -> Dict[str, str]:
        """Validate session state and return any issues"""
        issues = {}
        
        # Check required components
        if not SessionManager.get('kg'):
            issues['kg'] = "Knowledge graph not initialized"
        
        if not SessionManager.get('query_interface'):
            issues['query_interface'] = "Query interface not initialized"
        
        if SessionManager.get('connection_status') != 'connected':
            issues['connection'] = "Not connected to Neo4j database"
        
        return issues