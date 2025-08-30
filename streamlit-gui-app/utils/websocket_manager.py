"""
WebSocket manager for real-time automation monitoring
"""

import streamlit as st
import websocket
import threading
import json
import base64
from typing import List, Optional
from utils.logging_config import logger
from config.settings import settings
import time

class WebSocketManager:
    """Manages WebSocket connection for real-time automation monitoring"""
    
    def __init__(self, websocket_url: str = None):
        self.websocket_url = websocket_url or self._get_websocket_url()
        self.ws = None
        self.thread = None
        self.is_connected = False
        self.logs: List[str] = []
        self.current_screenshot: Optional[bytes] = None
        self.current_step_id: Optional[int] = None
        self.connection_attempts = 0
        self.max_connection_attempts = 3
        
    def _get_websocket_url(self) -> str:
        """Get WebSocket URL from settings"""
        # Use the configured websocket URL directly, or derive from base URL
        if hasattr(settings.automation, 'websocket_url') and settings.automation.websocket_url:
            return settings.automation.websocket_url
        
        # Fallback: derive from base URL
        base_url = settings.automation.base_url
        ws_url = base_url.replace('http://', 'ws://').replace('https://', 'wss://')
        return f"{ws_url}/logs"
    
    def connect(self) -> bool:
        """
        Establish WebSocket connection
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        if self.is_connected and self.ws:
            return True
            
        try:
            self.connection_attempts += 1
            logger.info(f"Attempting to connect to WebSocket: {self.websocket_url}")
            
            self.ws = websocket.WebSocketApp(
                self.websocket_url,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
                on_open=self._on_open
            )
            
            # Start WebSocket in a background thread
            self.thread = threading.Thread(target=self.ws.run_forever, daemon=True)
            self.thread.start()
            
            # Wait a bit for connection to establish
            time.sleep(1)
            
            return self.is_connected
            
        except Exception as e:
            logger.error(f"Failed to connect to WebSocket: {e}")
            self.logs.append(f"[WebSocket Error] Failed to connect: {e}")
            return False
    
    def disconnect(self):
        """Close WebSocket connection"""
        if self.ws:
            self.ws.close()
        self.is_connected = False
        self.connection_attempts = 0
        logger.info("WebSocket connection closed")
    
    def _on_open(self, _ws):
        """Handle WebSocket connection opened"""
        self.is_connected = True
        self.connection_attempts = 0
        logger.info("WebSocket connection established")
        self.logs.append("[WebSocket] Connected to automation monitor")
    
    def _on_message(self, _ws, message: str):
        """Handle incoming WebSocket messages"""
        try:
            event = json.loads(message)
        except json.JSONDecodeError:
            logger.warning(f"Received invalid JSON message: {message}")
            return

        message_type = event.get("type")
        
        if message_type == "log":
            log_message = event.get("message", "")
            self.logs.append(log_message)
            logger.debug(f"WebSocket log: {log_message}")
            
        elif message_type == "screenshot":
            try:
                img_b64 = event.get("image_b64", "")
                self.current_screenshot = base64.b64decode(img_b64)
                self.current_step_id = event.get("step_id")
                logger.debug(f"Received screenshot for step {self.current_step_id}")
            except Exception as e:
                error_msg = f"[Screenshot Error] Failed to decode: {e}"
                self.logs.append(error_msg)
                logger.error(error_msg)
                
        elif message_type == "step_complete":
            step_info = event.get("step_info", {})
            step_id = step_info.get("step_id")
            status = step_info.get("status", "unknown")
            self.logs.append(f"[Step {step_id}] Completed with status: {status}")
            
        elif message_type == "execution_complete":
            execution_info = event.get("execution_info", {})
            status = execution_info.get("status", "unknown")
            self.logs.append(f"[Execution] Completed with status: {status}")
            
        else:
            logger.debug(f"Received unknown message type: {message_type}")
    
    def _on_error(self, _ws, error):
        """Handle WebSocket errors"""
        error_msg = f"[WebSocket Error] {error}"
        self.logs.append(error_msg)
        logger.error(error_msg)
        
        # Try to reconnect if we haven't exceeded max attempts
        if self.connection_attempts < self.max_connection_attempts:
            logger.info("Attempting to reconnect...")
            time.sleep(2)  # Wait before reconnecting
            self.connect()
    
    def _on_close(self, _ws, close_status_code, close_msg):
        """Handle WebSocket connection closed"""
        self.is_connected = False
        close_message = "[WebSocket] Connection closed"
        if close_status_code:
            close_message += f" (Code: {close_status_code})"
        if close_msg:
            close_message += f" - {close_msg}"
            
        self.logs.append(close_message)
        logger.info(close_message)
    
    def get_recent_logs(self, max_logs: int = 100) -> List[str]:
        """
        Get recent log messages
        
        Args:
            max_logs: Maximum number of logs to return
            
        Returns:
            List of recent log messages
        """
        return self.logs[-max_logs:] if self.logs else []
    
    def get_current_screenshot(self) -> tuple[Optional[bytes], Optional[int]]:
        """
        Get the current screenshot
        
        Returns:
            Tuple of (screenshot_bytes, step_id)
        """
        return self.current_screenshot, self.current_step_id
    
    def clear_logs(self):
        """Clear all stored logs"""
        self.logs.clear()
        logger.debug("WebSocket logs cleared")


class StreamlitWebSocketMonitor:
    """Streamlit-specific WebSocket monitoring utilities"""
    
    @staticmethod
    def initialize_websocket_in_session() -> WebSocketManager:
        """
        Initialize WebSocket manager in Streamlit session state
        
        Returns:
            WebSocketManager instance
        """
        if "ws_manager" not in st.session_state:
            st.session_state.ws_manager = WebSocketManager()
            
        return st.session_state.ws_manager
    
    @staticmethod
    def render_monitoring_ui(ws_manager: WebSocketManager, col1, col2):
        """
        Render monitoring UI components in the provided columns
        
        Args:
            ws_manager: WebSocketManager instance
            col1: Streamlit column for logs
            col2: Streamlit column for screenshots
        """
        # Logs display
        with col1:
            st.markdown("### 📋 Execution Logs")
            
            if ws_manager.is_connected:
                st.markdown("🟢 **Connected to automation monitor**")
            else:
                st.markdown("🔴 **Not connected to automation monitor**")
                if st.button("🔄 Reconnect"):
                    ws_manager.connect()
                    st.rerun()
            
            # Display logs
            recent_logs = ws_manager.get_recent_logs()
            if recent_logs:
                logs_text = "\n".join(recent_logs)
                st.text_area(
                    "Logs",
                    value=logs_text,
                    height=400,
                    key="automation_logs",
                    label_visibility="collapsed"
                )
            else:
                st.info("No logs available yet. Start an automation to see logs here.")
        
        # Screenshot display  
        with col2:
            st.markdown("### 📸 Current Screenshot")
            
            screenshot_bytes, step_id = ws_manager.get_current_screenshot()
            if screenshot_bytes:
                caption = f"Step {step_id}" if step_id else "Current State"
                st.image(
                    screenshot_bytes,
                    caption=caption,
                    use_column_width=True
                )
            else:
                st.info("No screenshot available yet. Screenshots will appear here during execution.")
    
    @staticmethod
    def start_monitoring_for_execution(_execution_id: str) -> WebSocketManager:
        """
        Start monitoring for a specific execution
        
        Args:
            execution_id: ID of the execution to monitor
            
        Returns:
            WebSocketManager instance
        """
        ws_manager = StreamlitWebSocketMonitor.initialize_websocket_in_session()
        
        # Connect if not already connected
        if not ws_manager.is_connected:
            success = ws_manager.connect()
            if success:
                st.success("🟢 Connected to automation monitor")
            else:
                st.error("🔴 Failed to connect to automation monitor")
        
        return ws_manager