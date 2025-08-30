from openai import OpenAI
from typing import List, Dict, Any, Optional
from config.settings import config

class QwenClient:
    
    def __init__(self, api_key: str = None):
        self.api_key = config.DASHSCOPE_API_KEY
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=config.DASHSCOPE_BASE_URL
        )
    
    def chat_completion(self, messages: List[Dict[str, Any]], 
                       model: str = None, temperature: float = 0.3, 
                       max_tokens: int = None) -> str:
    
        model = model or config.QWEN_VL_MODEL
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in chat completion: {e}")
            raise
    
    def vision_analysis(self, image_b64: str, prompt: str, 
                       xml_context: str = None) -> str:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}},
                    {"type": "text", "text": prompt}
                ]
            }
        ]
        
        if xml_context:
            messages[0]["content"].insert(-1, {
                "type": "text", 
                "text": f"UI Hierarchy:\n{xml_context}"
            })
        
        return self.chat_completion(messages, model=config.QWEN_VL_MODEL)
    
    def text_completion(self, prompt: str, model: str = None, 
                       temperature: float = 0.1) -> str:
        messages = [{"role": "user", "content": prompt}]
        return self.chat_completion(
            messages, 
            model=model or config.QWEN_MODEL, 
            temperature=temperature
        )
    
    def vision_disambiguation(self, image_b64: str, candidates: List[Dict], 
                            user_query: str) -> Optional[int]:

        prompt = (
            "You are a mobile UI assistant.\n"
            "There are multiple possible elements matching the user query.\n"
            "Your job: choose the BEST one.\n\n"
            f"User Query: {user_query}\n\n"
            "Candidates:\n"
        )
        
        for i, node in enumerate(candidates):
            prompt += f"{i+1}. Bounds={node['bounds']} | Text='{node['text']}' | Desc='{node['content_desc']}' | ResID='{node['resource_id']}'\n"
        
        prompt += "\nRespond ONLY with a single integer ID (1..N) indicating the correct candidate.\n"
        
        try:
            response = self.vision_analysis(image_b64, prompt)
            return int(response.strip())
        except (ValueError, Exception) as e:
            print(f"Vision disambiguation failed: {e}")
            return None
    
    def create_mobile_action(self, image_b64: str, xml: str, user_query: str,
                           tools: List[Dict] = None, tool_choice: Dict = None) -> str:
        system_prompt = (
            "You are a mobile UI automation assistant. "
            "You MUST call the tool with ONE function call only, using exactly one of: "
            "click, long_press, swipe, type, key, system_button, open, wait, terminate. "
            "Do NOT output any thoughts, analysis, or plain text. Do NOT prefix with 'Thought:'. "
            "Wrap the function call inside <tool_call>{...}</tool_call> or output pure JSON only. "
            "For 'type' actions you MUST include a 'text' string to input. "
            "If the step or business goal implies commenting/posting/searching, generate a short, safe default, "
            "e.g., 'Great picture!' when commenting, if no explicit text was given."
        )
        
        messages = [
            {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}},
                    {"type": "text", "text": f"UI Hierarchy:\n{xml}"},
                    {"type": "text", "text": user_query}
                ]
            }
        ]
        
        return self.chat_completion(messages, temperature=0.3)