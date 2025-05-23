from rest_framework import serializers
from .models import Review
from auth_app.serializers import UserSerializer
from products.serializers import ProductSerializer

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True,
        source='product'
    )

    class Meta:
        model = Review
        fields = ('id', 'product', 'product_id', 'user', 'rating', 
                 'comment', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data) 