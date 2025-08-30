"""
Business logic for scenario management and processing
"""

import sys
import os
from typing import List, Dict, Any, Optional, Tuple
import json

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'knowledge-graph'))

from config.settings import settings
from utils.logging_config import logger, ErrorContext
from utils.session_manager import SessionManager

try:
    from src.scenarios.business_scenarios import get_all_business_scenarios
    from src.models.scenario import ScenarioType
except ImportError as e:
    logger.error(f"Failed to import scenario components: {e}")
    get_all_business_scenarios = None
    ScenarioType = None

class ScenarioService:
    """Service for managing business scenarios and test generation"""
    
    @staticmethod
    def generate_test_steps(query: str, start_state: str = "HomePage") -> Tuple[bool, Any, str]:
        """
        Generate test steps from a natural language query
        
        Args:
            query: Natural language query
            start_state: Starting state for the scenario
            
        Returns:
            Tuple of (success, scenario_plan, message)
        """
        query_interface = SessionManager.get('query_interface')
        if not query_interface:
            return False, None, "Query interface not available"
        
        if not query.strip():
            return False, None, "Please provide a test scenario description"
        
        try:
            with ErrorContext("Test step generation", show_in_ui=False):
                logger.info(f"Generating test steps for query: '{query}' from state: {start_state}")
                
                # Execute the query
                scenario_plan = query_interface.query_business_scenario(query, start_state)
                
                if scenario_plan and scenario_plan.steps:
                    SessionManager.set('current_plan', scenario_plan)
                    message = f"Generated {len(scenario_plan.steps)} test steps successfully"
                    logger.info(message)
                    return True, scenario_plan, message
                else:
                    message = "No test steps could be generated. Try rephrasing your scenario."
                    logger.warning(message)
                    return False, scenario_plan, message
                    
        except Exception as e:
            error_msg = f"Error generating test steps: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
    
    @staticmethod
    def get_scenario_statistics() -> Dict[str, int]:
        """Get statistics about available scenarios"""
        if get_all_business_scenarios is None:
            return {}
        
        try:
            scenarios = get_all_business_scenarios()
            
            # Count features
            features = set(s.feature for s in scenarios)
            
            # Count tags
            all_tags = set()
            for s in scenarios:
                all_tags.update(s.tags)
            
            return {
                'total_scenarios': len(scenarios),
                'features_covered': len(features),
                'unique_tags': len(all_tags)
            }
            
        except Exception as e:
            logger.error(f"Error getting scenario statistics: {e}")
            return {}
    
    @staticmethod
    def search_scenarios(
        feature_filter: str = "All",
        type_filter: str = "All", 
        tag_filter: str = "All",
        search_query: str = ""
    ) -> List[Any]:
        """
        Search and filter business scenarios
        
        Args:
            feature_filter: Feature to filter by
            type_filter: Scenario type to filter by
            tag_filter: Tag to filter by
            search_query: Text search query
            
        Returns:
            List of filtered scenarios
        """
        if get_all_business_scenarios is None:
            logger.warning("Business scenarios not available")
            return []
        
        try:
            with ErrorContext("Scenario search", show_in_ui=False):
                all_scenarios = get_all_business_scenarios()
                filtered_scenarios = all_scenarios
                
                # Apply feature filter
                if feature_filter != "All":
                    filtered_scenarios = [s for s in filtered_scenarios if s.feature == feature_filter]
                
                # Apply type filter
                if type_filter != "All":
                    filtered_scenarios = [s for s in filtered_scenarios if s.scenario_type == type_filter]
                
                # Apply tag filter
                if tag_filter != "All":
                    filtered_scenarios = [s for s in filtered_scenarios if tag_filter in s.tags]
                
                # Apply text search
                if search_query:
                    search_lower = search_query.lower()
                    filtered_scenarios = [
                        s for s in filtered_scenarios if 
                        search_lower in s.title.lower() or 
                        search_lower in s.feature.lower() or
                        search_lower in s.goal.lower()
                    ]
                
                logger.debug(f"Filtered scenarios: {len(filtered_scenarios)} from {len(all_scenarios)} total")
                return filtered_scenarios
                
        except Exception as e:
            logger.error(f"Error searching scenarios: {e}")
            return []
    
    @staticmethod
    def get_filter_options() -> Dict[str, List[str]]:
        """Get available filter options for scenarios"""
        if get_all_business_scenarios is None:
            return {"features": [], "types": [], "tags": []}
        
        try:
            scenarios = get_all_business_scenarios()
            
            # Get unique features
            features = sorted(list(set(s.feature for s in scenarios)))
            
            # Get scenario types
            if ScenarioType:
                types = [t.value for t in ScenarioType]
            else:
                types = sorted(list(set(s.scenario_type for s in scenarios)))
            
            # Get unique tags
            all_tags = set()
            for s in scenarios:
                all_tags.update(s.tags)
            tags = sorted(list(all_tags))
            
            return {
                "features": features,
                "types": types,
                "tags": tags
            }
            
        except Exception as e:
            logger.error(f"Error getting filter options: {e}")
            return {"features": [], "types": [], "tags": []}
    
    @staticmethod
    def create_scenario(scenario_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Create a new business scenario
        
        Args:
            scenario_data: Dictionary containing scenario information
            
        Returns:
            Tuple of (success, message)
        """
        try:
            with ErrorContext("Scenario creation", show_in_ui=False):
                # Validate required fields
                required_fields = ['title', 'feature', 'goal']
                for field in required_fields:
                    if not scenario_data.get(field):
                        return False, f"Missing required field: {field}"
                
                # In a production system, this would save to database
                logger.info(f"Created scenario: {scenario_data['title']}")
                return True, "Scenario created successfully (demo mode)"
                
        except Exception as e:
            error_msg = f"Error creating scenario: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def export_scenarios(format_type: str = "json") -> Tuple[bool, Any, str]:
        """
        Export scenarios in specified format
        
        Args:
            format_type: Export format ("json" or "csv")
            
        Returns:
            Tuple of (success, data, message)
        """
        if get_all_business_scenarios is None:
            return False, None, "Business scenarios not available"
        
        try:
            with ErrorContext("Scenario export", show_in_ui=False):
                scenarios = get_all_business_scenarios()
                
                if format_type.lower() == "json":
                    data = [s.model_dump() for s in scenarios]
                    json_data = json.dumps(data, indent=2)
                    return True, json_data, f"Exported {len(scenarios)} scenarios as JSON"
                
                elif format_type.lower() == "csv":
                    import pandas as pd
                    
                    summary_data = []
                    for s in scenarios:
                        summary_data.append({
                            'ID': s.id,
                            'Title': s.title,
                            'Feature': s.feature,
                            'Goal': s.goal,
                            'Type': s.scenario_type,
                            'Tags': ', '.join(s.tags),
                            'Steps Count': len(s.given_conditions) + len(s.when_actions) + len(s.then_expectations)
                        })
                    
                    df = pd.DataFrame(summary_data)
                    csv_data = df.to_csv(index=False)
                    return True, csv_data, f"Exported {len(scenarios)} scenarios as CSV"
                
                else:
                    return False, None, f"Unsupported export format: {format_type}"
                    
        except Exception as e:
            error_msg = f"Error exporting scenarios: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
    
    @staticmethod
    def format_plan_as_text(plan: Any) -> str:
        """Format a scenario plan as readable text"""
        if not plan:
            return "No plan available"
        
        try:
            text = f"Test Plan: {plan.scenario_title}\n"
            text += "=" * 50 + "\n\n"
            
            for step in plan.steps:
                text += f"Step {step.step_id}: {step.description}\n"
                text += f"  Action: {step.action_type.upper()}\n"
                text += f"  Query: {step.query_for_qwen}\n"
                if step.expected_state:
                    text += f"  Expected Result: {step.expected_state}\n"
                text += "\n"
            
            return text
            
        except Exception as e:
            logger.error(f"Error formatting plan as text: {e}")
            return f"Error formatting plan: {str(e)}"