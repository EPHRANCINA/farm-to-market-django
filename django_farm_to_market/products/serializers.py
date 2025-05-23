from rest_framework import serializers
from .models import Product, Category
from auth_app.serializers import UserSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    farmer = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True,
        source='category'
    )
    average_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'quantity', 'unit',
                 'category', 'category_id', 'farmer', 'image', 
                 'is_available', 'average_rating', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at', 'average_rating')

    def create(self, validated_data):
        validated_data['farmer'] = self.context['request'].user
        return super().create(validated_data) 