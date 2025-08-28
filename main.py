
import time
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.driver_manager import DriverManager
from core.screenshot_manager import ScreenshotManager
from ai_agents.step_executor import StepExecutor
from ai_agents.action_processor import ActionProcessor
from ai_agents.interruption_handler import InterruptionGuard
from ai_agents.planning_agent import MultiScenarioPlannerAgent
from ai_agents.qwen_agent import QwenClient
from models.execution_models import ProcessorConfig
from tools.mobile_tool import MobileUse
from config.settings import config

def main():
    print("Starting Mobile UI Automation")
    
    driver_manager = DriverManager()
    screenshot_manager = ScreenshotManager()
    processor_config = ProcessorConfig()
    
    try:
        print("Setting up Appium driver...")
        driver = driver_manager.setup_driver()
        driver_manager.wait_for_app_launch(4)
        
        mobile_use = MobileUse(
            cfg={
                "display_width_px": 1080, 
                "display_height_px": 1920
            }, 
            driver=driver
        )
        
        qwen_client = QwenClient()
        action_processor = ActionProcessor(driver_manager, mobile_use, qwen_client)
        
        guard = InterruptionGuard(
            llm_client_factory=lambda: qwen_client.client,
            execute_with_retry=action_processor.execute_with_retry,
            normalize_mobile_action=action_processor.normalize_mobile_action,
            allowlist_steps=["record", "camera", "microphone", "login", "sign in"],
            blocklist_ids=["ad_", "promo_", "offer_", "interstitial", "com.google.android.gms.ads"]
        )
        

        step_executor = StepExecutor(driver_manager, action_processor, guard, processor_config)
        
        screenshot_path = screenshot_manager.take_screenshot(driver)
        
        business_goal = 'Comment on a video'
        print(f"Business Goal: {business_goal}")
        
        run_scenario_with_planning(business_goal, step_executor, complexity="medium")
        
    except KeyboardInterrupt:
        print("\n⏹️ Automation interrupted by user")
    except Exception as e:
        print(f"❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Cleaning up...")
        driver_manager.quit_driver()
        print("✅ Automation completed")

def run_scenario_with_planning(business_goal: str, step_executor: StepExecutor, complexity: str = "medium"):
    print(f"Generating plan for: {business_goal}")
    
    planner = MultiScenarioPlannerAgent(api_key=config.DASHSCOPE_API_KEY)
    scenarios = planner.generate_scenarios(business_goal, complexity)
    
    if not scenarios:
        print("⚠️ No scenarios generated. Exiting.")
        return
    
    for scenario in scenarios:
        print(f"Full Scenario: {scenario}")
        print(f"\n🚀 Executing Scenario {scenario.scenario_id}: {scenario.scenario_title}")
        print(f"   ✅ Success Criteria: {scenario.success_criteria}")
        print(f"   ❌ Failure Cases: {scenario.failure_scenarios}")
        

        for step in scenario.steps:
            print(f"\n   ▶ Step {step.step_id}: {step.description} [{step.action_type}]")
            
            # screenshot before step
            screenshot_path = step_executor.screenshot_manager.take_screenshot(
                step_executor.driver_manager.get_driver()
            )
            
            success = step_executor.execute_step_with_guard(
                business_goal, step, screenshot_path
            )
            
            if not success:
                print(f"   ❌ Step {step.step_id} failed")

            else:
                print(f"   ✅ Step {step.step_id} completed")
            
            time.sleep(1.0)
        
        print(f"✅ Finished Scenario {scenario.scenario_id}\n")

if __name__ == "__main__":
    main()