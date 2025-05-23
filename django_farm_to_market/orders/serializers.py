from rest_framework import serializers
from .models import Order, OrderItem
from products.serializers import ProductSerializer
from auth_app.serializers import UserSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_available=True),
        write_only=True,
        source='product'
    )

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_id', 'quantity', 'price', 'created_at')
        read_only_fields = ('id', 'price', 'created_at')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'customer', 'status', 'total_amount', 'shipping_address', 
                 'items', 'created_at', 'updated_at')
        read_only_fields = ('id', 'total_amount', 'created_at', 'updated_at')

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        
        total_amount = 0
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            price = product.price
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price
            )
            total_amount += price * quantity
        
        order.total_amount = total_amount
        order.save()
        return order 