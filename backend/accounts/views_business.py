from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Business
from .serializers_business import BusinessSerializer, BusinessCreateUpdateSerializer
from chat.chroma_service import chroma_service


class BusinessRegisterView(generics.CreateAPIView):
    """
    API endpoint for users to register their business.
    Only non-admin users can register businesses.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = BusinessCreateUpdateSerializer
    
    def create(self, request, *args, **kwargs):
        # All users can register businesses now (admins included)
        
        # Check if user already has a business
        if hasattr(request.user, 'business'):
            return Response({
                'error': 'You already have a registered business. Please update it instead.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create business
        validated_data = serializer.validated_data
        business_serializer = BusinessSerializer(data={
            'business_info': validated_data['business_info'],
            'logo_upload': validated_data.get('logo', ''),
            'user': request.user.id
        })
        business_serializer.is_valid(raise_exception=True)
        
        # Save with user
        business = business_serializer.save(user=request.user)
        
        return Response({
            'message': 'Business registered successfully',
            'business': BusinessSerializer(business).data
        }, status=status.HTTP_201_CREATED)


class BusinessDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update or delete user's business.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = BusinessSerializer
    
    def get_object(self):
        # Users can only access their own business (all users including admins)
        return get_object_or_404(Business, user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Use simplified serializer for input validation
        input_serializer = BusinessCreateUpdateSerializer(data=request.data, partial=partial)
        input_serializer.is_valid(raise_exception=True)
        
        # Update using the full serializer
        validated_data = input_serializer.validated_data
        update_data = {
            'business_info': validated_data.get('business_info', instance.business_info),
            'logo_upload': validated_data.get('logo', '')
        }
        
        serializer = self.get_serializer(instance, data=update_data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'message': 'Business updated successfully',
            'business': serializer.data
        })
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Delete from ChromaDB
        chroma_service.delete_business(instance.chroma_id)
        
        # Delete from database
        self.perform_destroy(instance)
        
        return Response({
            'message': 'Business deleted successfully'
        }, status=status.HTTP_200_OK)


class BusinessSearchView(generics.GenericAPIView):
    """
    API endpoint to search for businesses (used internally by the chat service).
    """
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        query = request.data.get('query', '')
        n_results = request.data.get('n_results', 3)
        
        if not query:
            return Response({
                'error': 'Query parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Search in ChromaDB
        results = chroma_service.search_businesses(query, n_results)
        
        # Get full business details from database
        businesses = []
        for result in results:
            try:
                # Extract user_id from chroma_id (format: business_{user_id}_{uuid})
                parts = result['id'].split('_')
                if len(parts) >= 2:
                    user_id = int(parts[1])
                    business = Business.objects.filter(user_id=user_id).first()
                    if business:
                        businesses.append({
                            'id': business.id,
                            'username': business.user.username,
                            'business_info': business.business_info,
                            'logo_base64': BusinessSerializer(business).data.get('logo_base64'),
                            'relevance_score': 1 - result.get('distance', 0) if result.get('distance') is not None else None
                        })
            except Exception as e:
                print(f"Error processing business result: {e}")
                continue
        
        return Response({
            'query': query,
            'results': businesses,
            'count': len(businesses)
        })


class MyBusinessView(generics.RetrieveAPIView):
    """
    API endpoint to get current user's business.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = BusinessSerializer
    
    def get_object(self):
        # All users can have businesses (including admins)
        try:
            return Business.objects.get(user=self.request.user)
        except Business.DoesNotExist:
            return None
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance is None:
            return Response({
                'message': 'No business registered yet.',
                'has_business': False
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(instance)
        return Response({
            'has_business': True,
            'business': serializer.data
        })
