import json
from typing import Dict, List
from openai import OpenAI
from models.execution_models import ScenarioPlan, ExecutorStep
class MultiScenarioPlannerAgent:
    def __init__(self, api_key: str):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
        )

    def generate_scenarios(self, business_goal: str, complexity="medium") -> List[ScenarioPlan]:
        
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(business_goal, complexity)

        try:
            response = self.client.chat.completions.create(
                model="qwen2.5-7b-instruct",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=5000
            )

            response_text = response.choices[0].message.content.strip()
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                scenarios_data = json.loads(response_text[json_start:json_end])
                return self._parse_scenarios(scenarios_data)
            else:
                print("⚠️ No valid JSON in LLM response.")
                return []
        except Exception as e:
            print(f"❌ Error generating scenarios: {e}")
            return []

    def _build_system_prompt(self):
        return """You are an expert mobile test planner for TikTok UI automation.

TIKTOK UI KNOWLEDGE:
- Main feed: Vertical scrolling videos with UI on the right side
- Right side UI (top to bottom): Profile pic, Like button, Comment button, Share button
- Comment button: Speech bubble icon, always visible on video posts
- To comment: Click comment button → Comment panel opens → Click on the text field → Type in text field → Submit
- Submit button: triangle icon near comment field to submit
- Search: Magnifying glass icon at top, opens search screen with text input
- Navigation: Bottom tabs (Home, Discover, +, Inbox, Profile)
- Video interactions: Tap to pause/play, swipe up/down to scroll videos

ACTION RULES:
- Only use: click, type, swipe, long_press, key, system_button, open, wait
- Be specific about UI elements: "comment button (speech bubble icon)"
- Include fallback strategies for each step
- Validate that UI elements exist before interacting

PLANNING QUALITY:
- Generate realistic, tested scenarios
- Each step must be atomic (one clear action) eg. click one action and type is the next action
- Include UI verification steps
- Plan for common failure cases

Your task is to:
1. Take a single business goal.
2. Generate 2-4 **alternative test scenarios** that achieve the goal.
3. For each scenario, generate **executor-friendly steps**:
   - One action per step.
   - Be specific. Mention names, buttons, locations
   - Allowed action types: click, swipe, type, wait, verify.
   - Each step MUST have a description and a Qwen-friendly query string.
   - Include alternative_actions for fallback approaches.

Return ONLY valid JSON. No extra explanations."""

    def _build_user_prompt(self, business_goal: str, complexity: str):
        return f"""
Business Goal: "{business_goal}"
Complexity Level: {complexity}

Generate multiple TikTok automation scenarios to achieve the goal.
Output JSON format:
{{
    "scenarios": [
        {{
            "scenario_id": 1,
            "scenario_title": "",
            "success_criteria": "",
            "failure_scenarios": ["", ""],
            "steps": [
                {{
                    "step_id": 1,
                    "description": "Go to XX Button",
                    "action_type": "click",
                    "query_for_qwen": "Tap on the XX",
                    "alternative_actions": [""]
                }},
                {{
                    "step_id": 2,
                    "description": "S",
                    "action_type": "type",
                    "query_for_qwen": "Locate search bar and type creator name",
                    "alternative_actions": ["", ""]
                }},
                
            ]
        }}
    ]
}}
"""

    def _parse_scenarios(self, data: Dict) -> List[ScenarioPlan]:
        scenarios = []
        for s in data.get("scenarios", []):
            steps = []
            for step in s["steps"]:
                steps.append(ExecutorStep(
                    step_id=step["step_id"],
                    description=step["description"],
                    action_type=step["action_type"].lower(),
                    query_for_qwen=step.get("query_for_qwen", step["description"]),
                    alternative_actions=step.get("alternative_actions", [])
                ))
            scenarios.append(ScenarioPlan(
                scenario_id=s["scenario_id"],
                scenario_title=s["scenario_title"],
                steps=steps,
                success_criteria=s.get("success_criteria", "Scenario completed"),
                failure_scenarios=s.get("failure_scenarios", [])
            ))
        return scenarios
