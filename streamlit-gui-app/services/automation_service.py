import requests
import json
from typing import Dict, Any, Tuple, Optional
from utils.logging_config import logger, ErrorContext
from config.settings import settings

class AutomationService:
    """Service for triggering and monitoring test automation"""
    
    @staticmethod
    def execute_scenario(scenario_plan, start_state: str = "HomePage") -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Execute a scenario plan via FastAPI automation backend
        
        Args:
            scenario_plan: ScenarioPlan object with test steps
            start_state: Starting state for execution
            
        Returns:
            Tuple of (success, message, response_data)
        """
        if not scenario_plan or not scenario_plan.steps:
            return False, "No scenario plan provided", None
        
        try:
            with ErrorContext("Automation execution", show_in_ui=False):
                # Convert scenario plan to API payload
                payload = AutomationService._convert_scenario_to_payload(scenario_plan, start_state)
                
                # Get automation service URL
                endpoint = f"{settings.automation.base_url}/run"
                
                logger.info(f"Triggering automation execution at {endpoint}")
                logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
                
                # Make API request
                response = requests.post(
                    endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=settings.automation.timeout
                )
                
                response.raise_for_status()
                response_data = response.json()
                
                success_message = f"✅ Automation started successfully! Execution ID: {response_data.get('execution_id', 'N/A')}"
                logger.info(success_message)
                
                return True, success_message, response_data
                
        except requests.exceptions.ConnectionError:
            error_msg = "❌ Cannot connect to automation service. Please ensure FastAPI server is running on http://localhost:8000"
            logger.error(error_msg)
            return False, error_msg, None
            
        except requests.exceptions.Timeout:
            error_msg = "❌ Request timed out. Automation service may be busy."
            logger.error(error_msg)
            return False, error_msg, None
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"❌ Automation service error: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            return False, error_msg, None
            
        except Exception as e:
            error_msg = f"❌ Unexpected error during automation execution: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    @staticmethod
    def _convert_scenario_to_payload(scenario_plan, start_state: str) -> Dict[str, Any]:
        """
        Convert ScenarioPlan object to FastAPI payload format
        
        Args:
            scenario_plan: ScenarioPlan object
            start_state: Starting state
            
        Returns:
            Dictionary payload for FastAPI
        """
        payload = {
            "scenario_id": scenario_plan.scenario_id,
            "scenario_title": scenario_plan.scenario_title,
            "start_state": start_state,
            "steps": []
        }
        
        # Convert each ExecutorStep
        for step in scenario_plan.steps:
            step_data = {
                "step_id": step.step_id,
                "description": step.description,
                "action_type": step.action_type,
                "query_for_qwen": step.query_for_qwen,
                "alternative_actions": getattr(step, 'alternative_actions', []),
                "expected_state": step.expected_state
            }
            payload["steps"].append(step_data)
        
        # Add optional fields if they exist
        if hasattr(scenario_plan, 'preconditions'):
            payload["preconditions"] = scenario_plan.preconditions
        if hasattr(scenario_plan, 'postconditions'):
            payload["postconditions"] = scenario_plan.postconditions
        if hasattr(scenario_plan, 'environment_toggles'):
            payload["environment_toggles"] = scenario_plan.environment_toggles
        
        return payload
    
    @staticmethod
    def check_automation_service_health() -> Tuple[bool, str]:
        """
        Check if the automation service is running and healthy
        
        Returns:
            Tuple of (is_healthy, status_message)
        """
        try:
            health_endpoint = f"{settings.automation.base_url}/health"
            
            response = requests.get(health_endpoint, timeout=settings.automation.health_check_timeout)
            response.raise_for_status()
            
            return True, "🟢 Automation service is running"
            
        except requests.exceptions.ConnectionError:
            return False, "🔴 Automation service not reachable"
        except requests.exceptions.Timeout:
            return False, "🟡 Automation service timeout"
        except Exception as e:
            return False, f"🔴 Automation service error: {str(e)}"
    
    @staticmethod
    def get_execution_status(execution_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Get the status of a running execution
        
        Args:
            execution_id: ID of the execution to check
            
        Returns:
            Tuple of (success, status_data)
        """
        try:
            status_endpoint = f"{settings.automation.base_url}/status/{execution_id}"
            
            response = requests.get(status_endpoint, timeout=10)
            response.raise_for_status()
            
            return True, response.json()
            
        except Exception as e:
            logger.error(f"Error getting execution status: {e}")
            return False, {"error": str(e)}