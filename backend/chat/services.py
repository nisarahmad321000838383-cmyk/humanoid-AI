from huggingface_hub import InferenceClient
from django.conf import settings
from typing import Dict, List, Optional


class HuggingFaceService:
    """
    Service to interact with Hugging Face Chat Completion API.
    Using Qwen/Qwen3-235B-A22B model for chat completion.
    """
    
    def __init__(self, user=None):
        """
        Initialize the HuggingFace service.
        
        Args:
            user: The user making the request. If provided, will use their assigned HF token.
        """
        self.user = user
        self.model = settings.HUGGINGFACE_MODEL
        
        # Get the appropriate API token
        self.api_token = self._get_api_token()
        
        # Use the Hugging Face InferenceClient for Chat Completion API
        self.client = InferenceClient(
            model=self.model,
            token=self.api_token
        )
        
        # Store relevant products found during context search
        self.relevant_products = []
        
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

IMPORTANT: When you receive product or business information in your context:
- Product images are automatically displayed to users alongside your responses
- DO NOT say you cannot show, display, or share images
- Simply describe the products/businesses naturally
- The visual content is handled by the system automatically

If you're unsure about something, clearly state your uncertainty rather than guessing or fabricating information."""
    
    def _get_api_token(self):
        """
        Get the appropriate HuggingFace API token for the user.
        Uses assigned token if available, otherwise falls back to settings.
        """
        if self.user:
            from accounts.models import UserHFTokenAssignment
            
            # Get the active assignment for this user
            assignment = UserHFTokenAssignment.objects.filter(
                user=self.user,
                is_active=True
            ).select_related('hf_token').first()
            
            if assignment and assignment.hf_token.is_active:
                return assignment.hf_token.token
        
        # Fallback to settings token
        return settings.HUGGINGFACE_API_TOKEN
    
    def generate_response(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        deep_dive: bool = False
    ) -> str:
        """
        Generate a response using the Hugging Face Chat Completion API.
        Searches for relevant business information in ChromaDB and includes it in context.
        
        Args:
            user_message: The user's message
            conversation_history: Previous messages in the conversation
            deep_dive: If True, enables deep thinking mode with detailed analysis
            
        Returns:
            The AI's response text
        """
        # Search for relevant business and product information in ChromaDB
        business_context = self._get_business_context(user_message)
        product_context = self._get_product_context(user_message)
        
        # Choose system prompt based on deep dive mode
        if deep_dive:
            system_prompt = """You are Humanoid AI, an advanced AI assistant with the core principle of "No Hallucination". 

DEEP DIVE MODE IS ENABLED - You should think deeply and provide comprehensive, detailed responses.

Your responses must be:
- Accurate and fact-based
- Honest about limitations and uncertainties
- Clear when you don't know something
- Free from made-up information or false claims
- Detailed, thorough, and comprehensive
- Well-structured with clear explanations
- Include reasoning, examples, and multiple perspectives when relevant

In Deep Dive mode:
- Take time to think through the question carefully
- Provide detailed explanations with context
- Include examples, analogies, or step-by-step breakdowns
- Consider multiple angles and perspectives
- Elaborate on key concepts
- You may write longer responses (no strict line limit, but stay focused)

IMPORTANT: When you receive product or business information in your context:
- Product images are automatically displayed to users alongside your responses
- DO NOT say you cannot show, display, or share images
- Simply describe the products/businesses naturally and in detail
- The visual content is handled by the system automatically

If you're unsure about something, clearly state your uncertainty rather than guessing or fabricating information."""
        else:
            system_prompt = self.system_prompt
        
        # Build messages list for Chat Completion API
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add business context if found
        if business_context:
            messages.append({"role": "system", "content": business_context})
        
        # Add product context if found
        if product_context:
            messages.append({"role": "system", "content": product_context})
        
        # Add conversation history if exists
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Adjust parameters based on deep dive mode
        max_tokens = 3000 if deep_dive else 2000
        temperature = 0.8 if deep_dive else 0.7
        
        try:
            # Use the InferenceClient's chat_completion method
            response = self.client.chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
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
            # Log the actual error for debugging (only in development)
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"HuggingFace API Error: {str(e)}")
            
            # Check if it's an authentication/token error
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in ['token', 'auth', 'unauthorized', '401', '403']):
                error_msg = "Invalid HuggingFace API token. Please contact the administrator to add a valid token in Settings."
            else:
                # Generic error message to mask the underlying API provider
                error_msg = "Something went wrong! Try Again! Send another message!"
            raise Exception(error_msg)
    
    def _get_business_context(self, query: str) -> str:
        """
        Search for relevant business information in ChromaDB based on the query.
        
        Args:
            query: The user's query
            
        Returns:
            Formatted business context string or empty string
        """
        try:
            from .chroma_service import chroma_service
            
            # Search for relevant businesses (will return up to 3, or fewer if not enough exist)
            results = chroma_service.search_businesses(query, n_results=3)
            
            if not results or len(results) == 0:
                return ""
            
            # Format business information for the AI
            context_parts = ["\n--- RELEVANT BUSINESS INFORMATION ---"]
            context_parts.append("The following businesses may be relevant to the user's query:\n")
            
            for i, business in enumerate(results, 1):
                context_parts.append(f"\nBusiness {i} (Owner: {business.get('username', 'Unknown')}):")
                context_parts.append(business.get('business_info', 'No information available'))
                context_parts.append("---")
            
            context_parts.append("\nIf the user's query is related to any of these businesses, include relevant information in your response.")
            context_parts.append("If not related, ignore this context and respond to the user's query normally.")
            context_parts.append("--- END OF BUSINESS INFORMATION ---\n")
            
            return "\n".join(context_parts)
        except Exception as e:
            print(f"Error getting business context: {e}")
            return ""
    
    def _get_product_context(self, query: str) -> str:
        """
        Search for relevant product information in ChromaDB based on the query.
        
        Args:
            query: The user's query
            
        Returns:
            Formatted product context string or empty string
        """
        try:
            from .chroma_service import chroma_service
            from accounts.models_product import Product
            from accounts.serializers_product import ProductSerializer
            
            # Reset relevant products for this query
            self.relevant_products = []
            
            # Search for relevant products (will return up to 5, or fewer if not enough exist)
            results = chroma_service.search_products(query, n_results=5)
            
            if not results or len(results) == 0:
                return ""
            
            # Format product information for the AI
            context_parts = ["\n--- RELEVANT PRODUCT INFORMATION ---"]
            context_parts.append("The following products may be relevant to the user's query:\n")
            
            for i, product in enumerate(results, 1):
                context_parts.append(f"\nProduct {i} (Business Owner: {product.get('username', 'Unknown')}):")
                context_parts.append(product.get('product_description', 'No information available'))
                
                # Get product images and business info if product_db_id is available
                product_db_id = product.get('product_db_id')
                if product_db_id:
                    try:
                        product_obj = Product.objects.select_related('business', 'business__user').prefetch_related('images').get(id=product_db_id)
                        image_count = product_obj.images.count()
                        
                        # Add business info to context
                        if product_obj.business:
                            business = product_obj.business
                            context_parts.append(f"Owner Company: {business.user.username}")
                            context_parts.append(f"Business Details: {business.business_info}")
                        
                        if image_count > 0:
                            context_parts.append(f"Images: This product has {image_count} image(s) available.")
                            context_parts.append(f"Product ID: {product_db_id}")
                            
                            # Store product data for response (includes business_info via serializer)
                            serializer = ProductSerializer(product_obj)
                            self.relevant_products.append(serializer.data)
                        else:
                            # Still include products without images but with business info
                            serializer = ProductSerializer(product_obj)
                            self.relevant_products.append(serializer.data)
                    except Product.DoesNotExist:
                        pass
                
                context_parts.append("---")
            
            context_parts.append("\nIMPORTANT INSTRUCTIONS FOR HANDLING PRODUCTS:")
            context_parts.append("- If the user's query is related to any of these products, include relevant product information in your response.")
            context_parts.append("- The product images ARE AUTOMATICALLY DISPLAYED to the user alongside your message.")
            context_parts.append("- DO NOT say you cannot display or share images - they are already visible to the user.")
            context_parts.append("- Simply describe the products naturally and mention details like name, price, and specifications.")
            context_parts.append("- You can say things like 'Here are the products' or 'I found these items for you' or 'Check out these options'.")
            context_parts.append("- The images with full product details are shown in product cards next to your response.")
            context_parts.append("- If not related to the query, ignore this context and respond normally.")
            context_parts.append("--- END OF PRODUCT INFORMATION ---\n")
            
            return "\n".join(context_parts)
        except Exception as e:
            print(f"Error getting product context: {e}")
            return ""
