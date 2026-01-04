from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from .serializers import (
    ConversationSerializer,
    ConversationListSerializer,
    MessageSerializer,
    ChatRequestSerializer
)
from .services import HuggingFaceService


class ConversationListCreateView(generics.ListCreateAPIView):
    """
    API endpoint to list all conversations or create a new one.
    """
    permission_classes = (IsAuthenticated,)
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ConversationListSerializer
        return ConversationSerializer
    
    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ConversationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update or delete a conversation.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ConversationSerializer
    
    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)


class ChatView(generics.GenericAPIView):
    """
    API endpoint for chat interactions with Humanoid AI.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ChatRequestSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        conversation_id = serializer.validated_data.get('conversation_id')
        user_message = serializer.validated_data['message']
        title = serializer.validated_data.get('title', '')
        
        # Get or create conversation
        if conversation_id:
            conversation = get_object_or_404(
                Conversation,
                id=conversation_id,
                user=request.user
            )
        else:
            # Create new conversation
            conversation = Conversation.objects.create(
                user=request.user,
                title=title or user_message[:50]
            )
        
        # Save user message
        user_msg = Message.objects.create(
            conversation=conversation,
            role='user',
            content=user_message
        )
        
        try:
            # Get conversation history (exclude current user message, get last 10 for context)
            # We exclude the current message we just created
            history_messages = conversation.messages.exclude(id=user_msg.id).order_by('created_at')[:10]
            conversation_history = [
                {
                    'role': msg.role,
                    'content': msg.content
                }
                for msg in history_messages
            ]
            
            # Generate AI response
            hf_service = HuggingFaceService()
            ai_response = hf_service.generate_response(
                user_message=user_message,
                conversation_history=conversation_history
            )
            
            # Save AI response
            ai_msg = Message.objects.create(
                conversation=conversation,
                role='assistant',
                content=ai_response
            )
            
            return Response({
                'conversation_id': conversation.id,
                'user_message': MessageSerializer(user_msg).data,
                'ai_response': MessageSerializer(ai_msg).data,
                'conversation': ConversationSerializer(conversation).data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Delete the user message if AI response fails
            user_msg.delete()
            if not conversation_id:
                conversation.delete()
            
            return Response({
                'error': str(e),
                'message': 'Failed to generate AI response'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
