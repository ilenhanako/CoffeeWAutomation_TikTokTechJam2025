"""
Simple status monitoring for automation execution (replaces WebSocket manager)
"""

import streamlit as st
import requests
from typing import Dict, Any, Optional, Tuple
from utils.logging_config import logger
from config.settings import settings


class ExecutionStatusMonitor:
    """Simple HTTP-based status monitoring for automation execution"""
    
    @staticmethod
    def get_execution_status(execution_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Get the current status of an automation execution
        
        Args:
            execution_id: ID of the execution to check
            
        Returns:
            Tuple of (success, status_data)
        """
        try:
            status_endpoint = f"{settings.automation.base_url}/status/{execution_id}"
            
            response = requests.get(
                status_endpoint, 
                timeout=settings.automation.health_check_timeout
            )
            response.raise_for_status()
            
            status_data = response.json()
            logger.debug(f"Retrieved status for execution {execution_id}: {status_data}")
            
            return True, status_data
            
        except requests.exceptions.ConnectionError:
            return False, {"error": "Cannot connect to automation service"}
        except requests.exceptions.Timeout:
            return False, {"error": "Request timeout"}
        except requests.exceptions.HTTPError as e:
            return False, {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            logger.error(f"Error getting execution status: {e}")
            return False, {"error": str(e)}
    
    @staticmethod
    def get_execution_logs(execution_id: str) -> Tuple[bool, str]:
        """
        Get logs for a completed execution
        
        Args:
            execution_id: ID of the execution
            
        Returns:
            Tuple of (success, logs_content)
        """
        try:
            logs_endpoint = f"{settings.automation.base_url}/logs/{execution_id}"
            
            response = requests.get(
                logs_endpoint,
                timeout=settings.automation.timeout
            )
            response.raise_for_status()
            
            return True, response.text
            
        except Exception as e:
            logger.error(f"Error getting execution logs: {e}")
            return False, f"Error retrieving logs: {str(e)}"
    
    @staticmethod
    def get_execution_screenshot(execution_id: str) -> Tuple[bool, Optional[bytes]]:
        """
        Get final screenshot for a completed execution
        
        Args:
            execution_id: ID of the execution
            
        Returns:
            Tuple of (success, screenshot_bytes)
        """
        try:
            screenshot_endpoint = f"{settings.automation.base_url}/screenshot/{execution_id}"
            
            response = requests.get(
                screenshot_endpoint,
                timeout=settings.automation.timeout
            )
            response.raise_for_status()
            
            return True, response.content
            
        except Exception as e:
            logger.error(f"Error getting execution screenshot: {e}")
            return False, None


class StreamlitStatusMonitor:
    """Streamlit-specific status monitoring utilities"""
    
    @staticmethod
    def render_execution_status(execution_id: str) -> None:
        """
        Render execution status with manual refresh capability
        
        Args:
            execution_id: ID of the execution to monitor
        """
        st.markdown("---")
        st.markdown("### 📊 Execution Status")
        
        # Create columns for status and refresh button
        col_status, col_refresh = st.columns([3, 1])
        
        with col_refresh:
            refresh_clicked = st.button(
                "🔄 Check Progress", 
                key=f"refresh_status_{execution_id}",
                use_container_width=True
            )
        
        # Get current status from session state or refresh
        status_key = f"execution_status_{execution_id}"
        
        if refresh_clicked or status_key not in st.session_state:
            with st.spinner("Checking execution status..."):
                success, status_data = ExecutionStatusMonitor.get_execution_status(execution_id)
                
                if success:
                    st.session_state[status_key] = status_data
                else:
                    st.session_state[status_key] = {"error": status_data.get("error", "Unknown error")}
        
        # Display status
        with col_status:
            status_data = st.session_state.get(status_key, {})
            StreamlitStatusMonitor._render_status_display(status_data)
        
        # If execution is complete, show final results
        if status_data.get("status") == "completed":
            StreamlitStatusMonitor._render_final_results(execution_id)
    
    @staticmethod
    def _render_status_display(status_data: Dict[str, Any]) -> None:
        """Render the status display based on status data"""
        
        if "error" in status_data:
            st.error(f"❌ {status_data['error']}")
            return
        
        status = status_data.get("status", "unknown")
        current_step = status_data.get("current_step", 0)
        total_steps = status_data.get("total_steps", 0)
        
        # Status indicator
        if status == "running":
            st.info(f"🔄 **Running** - Step {current_step}/{total_steps}")
        elif status == "completed":
            st.success(f"✅ **Completed** - All {total_steps} steps finished")
        elif status == "failed":
            st.error(f"❌ **Failed** - Error at step {current_step}/{total_steps}")
        else:
            st.warning(f"⚠️ **{status.title()}**")
        
        # Progress bar if we have step information
        if total_steps > 0:
            progress = current_step / total_steps
            st.progress(progress)
            st.caption(f"Progress: {current_step}/{total_steps} steps ({progress:.1%})")
        
        # Current step information
        if status_data.get("current_step_description"):
            st.markdown(f"**Current Step:** {status_data['current_step_description']}")
        
        # Execution time
        if status_data.get("execution_time"):
            st.caption(f"Execution Time: {status_data['execution_time']}")
    
    @staticmethod
    def _render_final_results(execution_id: str) -> None:
        """Render final results for completed execution"""
        st.markdown("---")
        st.markdown("### 📋 Final Results")
        
        # Create tabs for logs and screenshot
        tab_logs, tab_screenshot = st.tabs(["📜 Logs", "📸 Screenshot"])
        
        with tab_logs:
            if st.button("📥 Load Logs", key=f"load_logs_{execution_id}"):
                with st.spinner("Loading execution logs..."):
                    success, logs = ExecutionStatusMonitor.get_execution_logs(execution_id)
                    
                    if success:
                        st.text_area(
                            "Execution Logs",
                            value=logs,
                            height=400,
                            key=f"logs_{execution_id}",
                            label_visibility="collapsed"
                        )
                    else:
                        st.error(f"Failed to load logs: {logs}")
        
        with tab_screenshot:
            if st.button("📷 Load Screenshot", key=f"load_screenshot_{execution_id}"):
                with st.spinner("Loading final screenshot..."):
                    success, screenshot_bytes = ExecutionStatusMonitor.get_execution_screenshot(execution_id)
                    
                    if success and screenshot_bytes:
                        st.image(
                            screenshot_bytes,
                            caption="Final Screenshot",
                            use_column_width=True
                        )
                    else:
                        st.error("Failed to load screenshot")
    
    @staticmethod
    def clear_execution_data(execution_id: str) -> None:
        """
        Clear cached execution data from session state
        
        Args:
            execution_id: ID of the execution to clear
        """
        keys_to_remove = [
            f"execution_status_{execution_id}",
            f"logs_{execution_id}",
            f"screenshot_{execution_id}"
        ]
        
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]
        
        logger.debug(f"Cleared execution data for {execution_id}")