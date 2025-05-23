from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Review
from .serializers import ReviewSerializer
from orders.models import Order, OrderItem

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', 'rating']

    def get_queryset(self):
        return Review.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        product = serializer.validated_data['product']
        # Check if user has purchased the product (delivered order)
        has_purchased = Order.objects.filter(
            customer=user,
            status='delivered',
            items__product=product
        ).exists()
        if not has_purchased:
            raise permissions.PermissionDenied('You can only review products you have purchased.')
        # Check if user has already reviewed this product
        if Review.objects.filter(user=user, product=product).exists():
            raise permissions.PermissionDenied('You have already reviewed this product.')
        serializer.save(user=user)

    @action(detail=False, methods=['get'])
    def product_reviews(self, request):
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response(
                {'error': 'product_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        reviews = Review.objects.filter(product_id=product_id)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data) 