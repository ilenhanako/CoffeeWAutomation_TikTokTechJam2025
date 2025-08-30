"""
Configuration settings for the GUI Testing Tool Streamlit app
"""

import os
from typing import Dict, Any
from dataclasses import dataclass
from pathlib import Path

@dataclass
class DatabaseConfig:
    """Neo4j database configuration"""
    uri: str = "bolt://localhost:7687"
    username: str = "neo4j"
    password: str = "tiktoktechjam"
    connection_timeout: int = 30
    max_retry_attempts: int = 3

@dataclass
class UIConfig:
    """UI configuration and theme settings"""
    page_title: str = "GUI Testing Tool"
    page_icon: str = "🤖"
    layout: str = "wide"
    sidebar_state: str = "expanded"
    
    # Theme colors
    primary_color: str = "#FE2C55"  # Razzmatazz
    secondary_color: str = "#25F4EE"  # Splash
    background_color: str = "#000000"  # Black
    text_color: str = "#FFFFFF"  # White
    grey_color: str = "#4A4A4A"
    dark_grey: str = "#1a1a1a"
    card_background: str = "#2a2a2a"

@dataclass
class AutomationConfig:
    """Automation service configuration"""
    base_url: str = "http://localhost:8000"
    websocket_url: str = "ws://localhost:8000/logs"
    timeout: int = 30
    health_check_timeout: int = 5
    max_retries: int = 3
    
@dataclass
class AppConfig:
    """Main application configuration"""
    app_title: str = "🤖 Bombotest GUI Test"
    app_description: str = "Generate automated test steps from natural language scenarios"
    version: str = "1.0.0"
    debug: bool = False
    
    # Performance settings
    cache_ttl: int = 300  # 5 minutes
    max_scenario_steps: int = 20
    default_spinner_text: str = "Processing..."
    
    # File paths
    knowledge_graph_path: str = "../knowledge-graph"
    chroma_db_path: str = "./chroma_db"

class Settings:
    """Centralized settings management"""
    
    def __init__(self):
        self.database = DatabaseConfig()
        self.ui = UIConfig()
        self.app = AppConfig()
        self.automation = AutomationConfig()
        self._load_from_environment()
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        # Database settings
        self.database.uri = os.getenv("NEO4J_URI", self.database.uri)
        self.database.username = os.getenv("NEO4J_USERNAME", self.database.username)
        self.database.password = os.getenv("NEO4J_PASSWORD", self.database.password)
        
        # App settings
        self.app.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.app.version = os.getenv("APP_VERSION", self.app.version)
        
        # Paths
        self.app.knowledge_graph_path = os.getenv("KG_PATH", self.app.knowledge_graph_path)
        self.app.chroma_db_path = os.getenv("CHROMA_DB_PATH", self.app.chroma_db_path)
        
        # Automation settings
        self.automation.base_url = os.getenv("AUTOMATION_BASE_URL", self.automation.base_url)
        self.automation.websocket_url = os.getenv("AUTOMATION_WEBSOCKET_URL", self.automation.websocket_url)
        self.automation.timeout = int(os.getenv("AUTOMATION_TIMEOUT", str(self.automation.timeout)))
        self.automation.health_check_timeout = int(os.getenv("AUTOMATION_HEALTH_TIMEOUT", str(self.automation.health_check_timeout)))
        self.automation.max_retries = int(os.getenv("AUTOMATION_MAX_RETRIES", str(self.automation.max_retries)))
    
    def get_page_config(self) -> Dict[str, Any]:
        """Get Streamlit page configuration"""
        return {
            "page_title": self.ui.page_title,
            "page_icon": self.ui.page_icon,
            "layout": self.ui.layout,
            "initial_sidebar_state": self.ui.sidebar_state
        }
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return {
            "uri": self.database.uri,
            "username": self.database.username,
            "password": self.database.password,
            "connection_timeout": self.database.connection_timeout,
            "max_retry_attempts": self.database.max_retry_attempts
        }
    
    def get_theme_css(self) -> str:
        """Generate CSS for the application theme"""
        return f"""
        <style>
            /* Global theme colors */
            .main {{
                background-color: {self.ui.background_color};
                color: {self.ui.text_color};
            }}
            
            /* Button styling */
            .stButton > button {{
                background-color: {self.ui.primary_color};
                color: {self.ui.text_color};
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }}
            
            .stButton > button:hover {{
                background-color: {self.ui.secondary_color};
                color: {self.ui.background_color};
                border: none;
            }}
            
            /* Input styling */
            .stSelectbox > div > div,
            .stTextArea > div > div > textarea,
            .stTextInput > div > div > input {{
                background-color: {self.ui.dark_grey};
                color: {self.ui.text_color};
                border: 1px solid {self.ui.grey_color};
            }}
            
            /* Expander styling */
            .stExpander {{
                background-color: {self.ui.dark_grey};
                border: 1px solid {self.ui.grey_color};
            }}
            
            /* Tab styling */
            .stTabs [data-baseweb="tab-list"] {{
                gap: 8px;
            }}
            
            .stTabs [data-baseweb="tab"] {{
                background-color: {self.ui.dark_grey};
                color: {self.ui.grey_color};
                border: 1px solid {self.ui.grey_color};
                border-radius: 8px 8px 0px 0px;
                padding: 10px 20px;
            }}
            
            .stTabs [aria-selected="true"] {{
                background-color: {self.ui.primary_color} !important;
                color: {self.ui.text_color} !important;
            }}
            
            /* Sidebar styling */
            .css-1d391kg {{
                background-color: {self.ui.dark_grey};
            }}
            
            /* Success/Error message styling */
            .stAlert > div {{
                background-color: {self.ui.secondary_color};
                color: {self.ui.background_color};
                border: none;
            }}
            
            /* Metric styling */
            .metric-container {{
                background-color: {self.ui.dark_grey};
                border: 1px solid {self.ui.secondary_color};
                border-radius: 8px;
                padding: 15px;
                text-align: center;
            }}
        </style>
        """

# Global settings instance
settings = Settings()