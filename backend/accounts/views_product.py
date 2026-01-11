from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models_product import Product, ProductImage
from .serializers_product import ProductSerializer, ProductCreateUpdateSerializer
from chat.chroma_service import chroma_service


class ProductListCreateView(generics.ListCreateAPIView):
    """
    API endpoint to list all products for the current user's business
    or create a new product.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ProductSerializer
    pagination_class = None  # Disable pagination to return plain array
    
    def get_queryset(self):
        """Get products for current user's business."""
        # Check if user has a business
        if not hasattr(self.request.user, 'business'):
            return Product.objects.none()
        
        return Product.objects.filter(business=self.request.user.business).prefetch_related('images')
    
    def create(self, request, *args, **kwargs):
        """Create a new product for the current user's business."""
        # Check if user has a business
        if not hasattr(request.user, 'business'):
            return Response({
                'error': 'You must register a business first before adding products.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check product limit (max 10 products per business)
        existing_products_count = Product.objects.filter(business=request.user.business).count()
        if existing_products_count >= 10:
            return Response({
                'error': f'Maximum 10 products allowed per business. You already have {existing_products_count} products.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate input using simplified serializer
        input_serializer = ProductCreateUpdateSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        
        # Create product using full serializer
        validated_data = input_serializer.validated_data
        product_data = {
            'product_description': validated_data['product_description'],
            'images_upload': validated_data['images'],
            'business': request.user.business.id
        }
        
        serializer = self.get_serializer(data=product_data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save(business=request.user.business)
        
        return Response({
            'message': 'Product created successfully',
            'product': ProductSerializer(product).data
        }, status=status.HTTP_201_CREATED)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update, or delete a product.
    Users can only access products from their own business.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        """Get products for current user's business."""
        if not hasattr(self.request.user, 'business'):
            return Product.objects.none()
        
        return Product.objects.filter(business=self.request.user.business).prefetch_related('images')
    
    def update(self, request, *args, **kwargs):
        """Update a product."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Validate input using simplified serializer
        input_serializer = ProductCreateUpdateSerializer(data=request.data, partial=partial)
        input_serializer.is_valid(raise_exception=True)
        
        # Update using full serializer
        validated_data = input_serializer.validated_data
        update_data = {
            'product_description': validated_data.get('product_description', instance.product_description),
        }
        
        # Only update images if provided
        if 'images' in validated_data:
            update_data['images_upload'] = validated_data['images']
        
        serializer = self.get_serializer(instance, data=update_data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'message': 'Product updated successfully',
            'product': serializer.data
        })
    
    def destroy(self, request, *args, **kwargs):
        """Delete a product and remove from ChromaDB."""
        instance = self.get_object()
        
        # Delete from ChromaDB
        chroma_service.delete_product(instance.chroma_id)
        
        # Delete associated images (cascade should handle this, but explicit is better)
        instance.images.all().delete()
        
        # Delete product from MySQL
        self.perform_destroy(instance)
        
        return Response({
            'message': 'Product deleted successfully'
        }, status=status.HTTP_200_OK)


class ProductStatsView(generics.GenericAPIView):
    """
    API endpoint to get product statistics for current user's business.
    """
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        """Get product statistics."""
        if not hasattr(request.user, 'business'):
            return Response({
                'has_business': False,
                'message': 'You must register a business first.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        business = request.user.business
        products_count = Product.objects.filter(business=business).count()
        max_products = 10
        remaining_slots = max_products - products_count
        
        return Response({
            'has_business': True,
            'total_products': products_count,
            'max_products': max_products,
            'remaining_slots': remaining_slots,
            'can_add_more': remaining_slots > 0
        })


class ProductSearchView(generics.GenericAPIView):
    """
    API endpoint to search for products using ChromaDB semantic search.
    """
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        """Search for products based on query."""
        query = request.data.get('query', '')
        n_results = request.data.get('n_results', 5)
        business_id = request.data.get('business_id', None)
        
        if not query:
            return Response({
                'error': 'Query parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Search in ChromaDB
        results = chroma_service.search_products(query, n_results, business_id)
        
        # Get full product details from database
        products = []
        for result in results:
            try:
                # Extract product_id from chroma_id (format: product_{business_id}_{uuid})
                chroma_id = result['id']
                product = Product.objects.filter(chroma_id=chroma_id).prefetch_related('images').first()
                
                if product:
                    products.append({
                        'id': product.id,
                        'business_id': product.business.id,
                        'username': product.business.user.username,
                        'product_description': product.product_description,
                        'images_count': product.images.count(),
                        'first_image': ProductSerializer(product).data['images'][0] if product.images.exists() else None,
                        'relevance_score': 1 - result.get('distance', 0) if result.get('distance') is not None else None
                    })
            except Exception as e:
                print(f"Error processing product result: {e}")
                continue
        
        return Response({
            'query': query,
            'results': products,
            'count': len(products)
        })
