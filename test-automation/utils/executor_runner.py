
# Deprecated: Previous implementation of step_executor (kept for reference).
# Replaced by graph/nodes

import time
from ai_agents.planning_agent import MultiScenarioPlannerAgent
from ai_agents.step_executor import StepExecutor
from config.settings import config

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