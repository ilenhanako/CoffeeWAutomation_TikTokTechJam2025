"""
Database connection and management services
"""

import sys
import os
from typing import Optional, Tuple
import streamlit as st

# Add knowledge graph path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'knowledge-graph'))

from config.settings import settings
from utils.logging_config import logger, ErrorContext
from utils.session_manager import SessionManager

try:
    from src.graph.neo4j_knowledge_graph import Neo4jKnowledgeGraph
    from src.graph.query_interface import GraphQueryInterface
except ImportError as e:
    logger.error(f"Failed to import knowledge graph components: {e}")
    Neo4jKnowledgeGraph = None
    GraphQueryInterface = None

class DatabaseManager:
    """Manages database connections and initialization"""
    
    @staticmethod
    def initialize_connection() -> Tuple[bool, str]:
        """
        Initialize Neo4j connection and query interface
        
        Returns:
            Tuple of (success, error_message)
        """
        if Neo4jKnowledgeGraph is None or GraphQueryInterface is None:
            return False, "Knowledge graph components not available"
        
        try:
            with ErrorContext("Database connection initialization"):
                db_config = settings.get_database_config()
                logger.info(f"Connecting to Neo4j at {db_config['uri']}")
                
                # Initialize knowledge graph
                kg = Neo4jKnowledgeGraph(
                    uri=db_config['uri'],
                    username=db_config['username'],
                    password=db_config['password']
                )
                
                # Test connection
                with kg.get_session() as session:
                    result = session.run("RETURN 1 as test")
                    test_result = result.single()
                    if not test_result or test_result['test'] != 1:
                        raise Exception("Connection test failed")
                
                # Initialize query interface
                query_interface = GraphQueryInterface(kg)
                
                # Update session state
                SessionManager.update({
                    'kg': kg,
                    'query_interface': query_interface,
                    'connection_status': 'connected'
                })
                
                logger.info("Database connection established successfully")
                return True, "Connected successfully"
                
        except Exception as e:
            error_msg = f"Database connection failed: {str(e)}"
            logger.error(error_msg)
            SessionManager.set('connection_status', f"error: {str(e)}")
            return False, error_msg
    
    @staticmethod
    def initialize_business_scenarios() -> Tuple[bool, str]:
        """
        Initialize business scenarios in ChromaDB
        
        Returns:
            Tuple of (success, message)
        """
        query_interface = SessionManager.get('query_interface')
        if not query_interface:
            return False, "Query interface not available"
        
        try:
            with ErrorContext("Business scenarios initialization"):
                # Check if scenarios already exist
                try:
                    kg = SessionManager.get('kg')
                    similar_scenarios = kg.find_similar_business_scenarios("test query", top_k=1)
                    
                    if similar_scenarios:
                        SessionManager.set('scenarios_initialized', True)
                        logger.info("Found existing business scenarios in ChromaDB")
                        return True, "Scenarios already loaded"
                    
                except Exception:
                    logger.debug("No existing scenarios found, will initialize new ones")
                
                # Initialize new scenarios
                logger.info("Loading business scenarios into ChromaDB...")
                query_interface.add_sample_business_scenarios()
                SessionManager.set('scenarios_initialized', True)
                
                logger.info("Business scenarios loaded successfully")
                return True, "Business scenarios loaded into persistent ChromaDB"
                
        except Exception as e:
            error_msg = f"Failed to initialize scenarios: {str(e)}"
            logger.error(error_msg)
            SessionManager.set('scenarios_initialized', False)
            return False, error_msg
    
    @staticmethod
    def refresh_connection() -> None:
        """Refresh the database connection"""
        logger.info("Refreshing database connection...")
        
        # Clear existing connection state
        SessionManager.reset_connection_state()
        
        # Reinitialize
        success, message = DatabaseManager.initialize_connection()
        
        if success:
            # Also reinitialize scenarios
            scenario_success, scenario_message = DatabaseManager.initialize_business_scenarios()
            if not scenario_success:
                logger.warning(f"Scenarios not initialized: {scenario_message}")
        
        logger.info(f"Connection refresh completed: {message}")
    
    @staticmethod
    def test_connection(uri: str, username: str, password: str) -> Tuple[bool, str]:
        """
        Test a database connection with provided credentials
        
        Args:
            uri: Neo4j URI
            username: Neo4j username  
            password: Neo4j password
            
        Returns:
            Tuple of (success, message)
        """
        if Neo4jKnowledgeGraph is None:
            return False, "Knowledge graph components not available"
        
        try:
            with ErrorContext("Database connection test", show_in_ui=False):
                test_kg = Neo4jKnowledgeGraph(uri, username, password)
                
                with test_kg.get_session() as session:
                    session.run("RETURN 1")
                
                test_kg.close()
                logger.info(f"Connection test successful for {uri}")
                return True, "Connection successful!"
                
        except Exception as e:
            error_msg = f"Connection test failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def get_database_stats() -> dict:
        """Get database statistics"""
        kg = SessionManager.get('kg')
        if not kg:
            return {}
        
        try:
            with kg.get_session() as session:
                # Get node counts
                result = session.run("MATCH (n) RETURN count(n) as total_nodes")
                total_nodes = result.single()['total_nodes']
                
                # Get relationship counts
                result = session.run("MATCH ()-[r]->() RETURN count(r) as total_relationships")
                total_relationships = result.single()['total_relationships']
                
                # Get states count
                result = session.run("MATCH (s:State) RETURN count(s) as states")
                states = result.single()['states']
                
                # Get components count
                result = session.run("MATCH (c:Component) RETURN count(c) as components")
                components = result.single()['components']
                
                return {
                    'total_nodes': total_nodes,
                    'total_relationships': total_relationships,
                    'states': states,
                    'components': components
                }
                
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}
    
    @staticmethod
    def close_connection() -> None:
        """Close the database connection"""
        kg = SessionManager.get('kg')
        if kg:
            try:
                kg.close()
                logger.info("Database connection closed")
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")
        
        SessionManager.reset_connection_state()