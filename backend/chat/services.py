from huggingface_hub import InferenceClient
from django.conf import settings
from typing import Dict, List, Optional


class HuggingFaceService:
    """
    Service to interact with Hugging Face Chat Completion API.
    Using Qwen/Qwen3-235B-A22B model for chat completion.
    """
    
    def __init__(self):
        self.api_token = settings.HUGGINGFACE_API_TOKEN
        self.model = settings.HUGGINGFACE_MODEL
        # Use the Hugging Face InferenceClient for Chat Completion API
        self.client = InferenceClient(
            model=self.model,
            token=self.api_token
        )
        # System prompt emphasizing no hallucination and response length limits
        self.system_prompt = """You are Humanoid AI, an advanced AI assistant with the core principle of "No Hallucination". 

Your responses must be:
- Accurate and fact-based
- Honest about limitations and uncertainties
- Clear when you don't know something
- Free from made-up information or false claims
- Helpful, professional, and concise
- LIMITED TO 5 LINES MAXIMUM unless the user explicitly requests more lines or a longer response

IMPORTANT RESPONSE LENGTH RULE:
- By default, keep your response to 10 lines or less (approximately 10 lines of text)
- If the user asks for a specific number of lines, honor their request
- If the user asks for a detailed, long, or comprehensive answer, you may exceed 10 lines
- Otherwise, always keep responses concise and within 10 lines

If you're unsure about something, clearly state your uncertainty rather than guessing or fabricating information."""
    
    def generate_response(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate a response using the Hugging Face Chat Completion API.
        
        Args:
            user_message: The user's message
            conversation_history: Previous messages in the conversation
            
        Returns:
            The AI's response text
        """
        # Build messages list for Chat Completion API
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add conversation history if exists
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            # Use the InferenceClient's chat_completion method
            response = self.client.chat_completion(
                messages=messages,
                max_tokens=2000,
                temperature=0.7,
                top_p=0.95,
                stream=False
            )
            
            # Extract the response content
            if response and hasattr(response, 'choices') and len(response.choices) > 0:
                message_content = response.choices[0].message.content
                return message_content.strip()
            
            # Fallback error handling
            raise Exception(f"Unexpected API response format: {response}")
            
        except Exception as e:
            error_msg = f"Error communicating with Hugging Face API: {str(e)}"
            raise Exception(error_msg)
