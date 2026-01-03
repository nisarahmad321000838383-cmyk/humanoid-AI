import requests
from django.conf import settings
from typing import Dict, List, Optional


class HuggingFaceService:
    """
    Service to interact with Hugging Face Inference API.
    Using Qwen/Qwen2.5-72B-Instruct model for chat completion.
    """
    
    def __init__(self):
        self.api_token = settings.HUGGINGFACE_API_TOKEN
        self.model = settings.HUGGINGFACE_MODEL
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        # System prompt emphasizing no hallucination
        self.system_prompt = """You are Humanoid AI, an advanced AI assistant with the core principle of "No Hallucination". 
Your responses must be:
- Accurate and fact-based
- Honest about limitations and uncertainties
- Clear when you don't know something
- Free from made-up information or false claims
- Helpful, professional, and concise

If you're unsure about something, clearly state your uncertainty rather than guessing or fabricating information."""
    
    def generate_response(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate a response using the Hugging Face API.
        
        Args:
            user_message: The user's message
            conversation_history: Previous messages in the conversation
            
        Returns:
            The AI's response text
        """
        # Build messages list
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add conversation history if exists
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Prepare the payload
        payload = {
            "inputs": self._format_messages_for_api(messages),
            "parameters": {
                "max_new_tokens": 2000,
                "temperature": 0.7,
                "top_p": 0.95,
                "return_full_text": False
            }
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Handle different response formats
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get('generated_text', '')
            elif isinstance(result, dict):
                generated_text = result.get('generated_text', result.get('text', ''))
            else:
                generated_text = str(result)
            
            return generated_text.strip()
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error communicating with Hugging Face API: {str(e)}"
            if hasattr(e.response, 'text'):
                error_msg += f"\nResponse: {e.response.text}"
            raise Exception(error_msg)
    
    def _format_messages_for_api(self, messages: List[Dict[str, str]]) -> str:
        """
        Format messages into a prompt string for the API.
        """
        formatted_prompt = ""
        for msg in messages:
            role = msg['role']
            content = msg['content']
            
            if role == 'system':
                formatted_prompt += f"System: {content}\n\n"
            elif role == 'user':
                formatted_prompt += f"User: {content}\n\n"
            elif role == 'assistant':
                formatted_prompt += f"Assistant: {content}\n\n"
        
        formatted_prompt += "Assistant: "
        return formatted_prompt
