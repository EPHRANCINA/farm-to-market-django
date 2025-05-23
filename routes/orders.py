from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.order import Order, OrderItem
from models.product import Product
from models.user import User
from app import db

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/', methods=['GET'])
@jwt_required()
def get_orders():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role == 'farmer':
        # Get orders for products sold by the farmer
        orders = Order.query.join(OrderItem).join(Product).filter(
            Product.seller_id == user_id
        ).distinct().all()
    else:
        # Get orders made by the buyer
        orders = Order.query.filter_by(buyer_id=user_id).all()
    
    return jsonify([order.to_dict() for order in orders]), 200

@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    order = Order.query.get_or_404(order_id)
    
    # Check if user has permission to view this order
    if user.role == 'farmer':
        if not any(item.product.seller_id == user_id for item in order.items):
            return jsonify({'error': 'Unauthorized to view this order'}), 403
    elif order.buyer_id != user_id:
        return jsonify({'error': 'Unauthorized to view this order'}), 403
    
    return jsonify(order.to_dict()), 200

@orders_bp.route('/', methods=['POST'])
@jwt_required()
def create_order():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role != 'buyer':
        return jsonify({'error': 'Only buyers can create orders'}), 403
    
    data = request.get_json()
    
    # Create order
    order = Order(
        buyer_id=user_id,
        shipping_address=data['shipping_address'],
        total_amount=0  # Will be calculated
    )
    
    total_amount = 0
    
    # Create order items
    for item_data in data['items']:
        product = Product.query.get_or_404(item_data['product_id'])
        
        if product.quantity < item_data['quantity']:
            return jsonify({'error': f'Not enough quantity available for {product.name}'}), 400
        
        order_item = OrderItem(
            product_id=product.id,
            quantity=item_data['quantity'],
            price_at_time=product.price
        )
        
        total_amount += product.price * item_data['quantity']
        product.quantity -= item_data['quantity']
        
        order.items.append(order_item)
    
    order.total_amount = total_amount
    db.session.add(order)
    db.session.commit()
    
    return jsonify({
        'message': 'Order created successfully',
        'order': order.to_dict()
    }), 201

@orders_bp.route('/<int:order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    order = Order.query.get_or_404(order_id)
    
    if user.role != 'farmer':
        return jsonify({'error': 'Only farmers can update order status'}), 403
    
    # Check if user is the seller of any product in the order
    if not any(item.product.seller_id == user_id for item in order.items):
        return jsonify({'error': 'Unauthorized to update this order'}), 403
    
    data = request.get_json()
    new_status = data['status']
    
    if new_status not in ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']:
        return jsonify({'error': 'Invalid status'}), 400
    
    order.status = new_status
    db.session.commit()
    
    return jsonify({
        'message': 'Order status updated successfully',
        'order': order.to_dict()
    }), 200 