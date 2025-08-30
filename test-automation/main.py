
import time
import sys
from pathlib import Path
from typing import List
from graph.workflow import build_workflow
from graph import nodes
from ai_agents.evaluator import AIEvaluator
from utils.demo_coordinates import DemoCoordinator

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
from utils.executor_runner import run_scenario_with_planning
from  utils.logging import setup_logger

logger = setup_logger()

def run_automation(business_goal: str, scenarios: List):
    logger.info("Starting Mobile UI Automation")
    print("Starting Mobile UI Automation")
    
    driver_manager = DriverManager()
    driver_manager.wait_for_app_launch(4)
    screenshot_manager = ScreenshotManager()
    evaluator = AIEvaluator()
    processor_config = ProcessorConfig()

    DEMO_MODE = False
    
    try:
        logger.info("Setting up Appium driver...")
        driver = driver_manager.setup_driver()
        time.sleep(10)

        screen_size = driver_manager.get_screen_size()
        
        mobile_use = MobileUse(
            cfg={
                "display_width_px": screen_size["width"],
                "display_height_px": screen_size["height"]
            }, 
            driver=driver
        )
        
        qwen_client = QwenClient()
        demo_coordinator = None
        action_processor = ActionProcessor(driver_manager, mobile_use, qwen_client)

        if DEMO_MODE:
            demo_coordinator = DemoCoordinator(
                mobile_use=mobile_use,
                execute_with_retry_func=action_processor.execute_with_retry
            )
           
            action_processor.demo_coordinator = demo_coordinator

        action_processor = ActionProcessor(driver_manager, mobile_use, qwen_client,demo_coordinator=demo_coordinator)

        
        
        guard = InterruptionGuard(
            llm_client_factory=lambda: qwen_client.client,
            execute_with_retry=action_processor.execute_with_retry,
            normalize_mobile_action=action_processor.normalize_mobile_action,
            allowlist_steps=["record", "camera", "microphone", "login", "sign in"],
            blocklist_ids=["ad_", "promo_", "offer_", "interstitial", "com.google.android.gms.ads"]
        )

        nodes.set_dependencies(
            driver_manager,
            screenshot_manager,
            action_processor,
            evaluator,
            guard
        )
        
        # business_goal = 'Go to the profile page, click edit profile and change the name to Angie and save'
        print(f"Business Goal: {business_goal}")
        logger.info(f"Business Goal: {business_goal}")

        ## Uncomment to use step_executor instead of graph
        # step_executor = StepExecutor(driver_manager, action_processor, guard, processor_config)
        
        screenshot_path = screenshot_manager.take_screenshot(driver)
        # planner = MultiScenarioPlannerAgent(api_key=config.DASHSCOPE_API_KEY)
        # scenarios = planner.generate_scenarios(business_goal, complexity="medium")

        if not scenarios:
            print("⚠️ No scenarios generated. Exiting.")
            return      
        
        ## Uncomment to use step_executor instead of graph
        # run_scenario_with_planning(business_goal, step_executor, complexity="medium")

        graph = build_workflow()
        

        for scenario in scenarios:
            print(f"\n🚀 Executing Scenario {scenario.scenario_id}: {scenario.scenario_title}")
            logger.info(f"🚀 Executing Scenario {scenario.scenario_id}: {scenario.scenario_title}")

            for step in scenario.steps:
                logger.info(f" ▶ Step {step.step_id}: {step.description} [{step.action_type}]")
                print(f"\n   ▶ Step {step.step_id}: {step.description} [{step.action_type}]")

                # build graph state from planner step
                state = {
                    "business_goal": business_goal,
                    "user_query": getattr(step, "query_for_qwen", step.description),
                    "step_description": step.description,
                    "expected_state_hint": step.expected_state,
                    "cycle": 0,
                    "done": False,
                    "notes": []
                }

                result = graph.invoke(state)

                intr = guard.detect(driver, screen_size["width"], screen_size["height"])
                if intr.present:
                    screenshot_path = screenshot_manager.take_screenshot(driver)
                    screenshot_b64 = screenshot_manager.encode_image(screenshot_path)
                    logger.send_event({
                        "type": "screenshot",
                        "step_id": step.step_id,
                        "image_b64": screenshot_b64
                    })

                er = result.get("eval_result", {})
                logger.info(
                    f"[Evaluator] ok={er.get('ok')} "
                    f"recovery={er.get('recovery')} "
                    f"reason={er.get('reason')} "
                    f"suggestions={er.get('suggestions')}"
                )

                if result.get("done"):
                    print(f"   ✅ Step {step.step_id} completed | Notes: {result.get('notes')}")
                    logger.info(f"   ✅ Step {step.step_id} completed | Notes: {result.get('notes')}")
                else:
                    print(f"   ❌ Step {step.step_id} failed | Notes: {result.get('notes')}")
                    logger.info(f"   ❌ Step {step.step_id} failed | Notes: {result.get('notes')}")

            print("↻ Resetting GUI for next scenario...")
            logger.info("↻ Resetting GUI for next scenario...")
            driver_manager.reset_app(clear_data=False)
            time.sleep(1.0)
        
    except Exception as e:
        print(f"❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Cleaning up...")
        driver_manager.quit_driver()
        print("✅ Automation completed")
        logger.info("✅ Automation completed")

# if __name__ == "__main__":
#     main()

