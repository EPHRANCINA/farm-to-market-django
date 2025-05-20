from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.models import Order, Product, User
from api.app import db

bp = Blueprint('orders', __name__, url_prefix='/api/orders')

@bp.route('', methods=['GET'])
@jwt_required()
def get_orders():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Get query parameters
    status = request.args.get('status')
    
    # Base query
    if user.role == 'farmer':
        # Farmers see orders for their products
        query = Order.query.join(Product).filter(Product.seller_id == current_user_id)
    else:
        # Buyers see their own orders
        query = Order.query.filter(Order.buyer_id == current_user_id)
    
    # Apply status filter if provided
    if status:
        query = query.filter(Order.status == status)
    
    orders = query.all()
    
    return jsonify({
        'orders': [{
            'id': order.id,
            'product': {
                'id': order.product.id,
                'name': order.product.name,
                'price': order.product.price
            },
            'quantity': order.quantity,
            'total_price': order.total_price,
            'status': order.status,
            'buyer': {
                'id': order.buyer.id,
                'username': order.buyer.username
            },
            'seller': {
                'id': order.product.seller.id,
                'username': order.product.seller.username
            },
            'created_at': order.created_at.isoformat()
        } for order in orders]
    })

@bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    order = Order.query.get_or_404(order_id)
    
    # Check if user has permission to view this order
    if user.role == 'buyer' and order.buyer_id != current_user_id:
        return jsonify({'error': 'Unauthorized to view this order'}), 403
    if user.role == 'farmer' and order.product.seller_id != current_user_id:
        return jsonify({'error': 'Unauthorized to view this order'}), 403
    
    return jsonify({
        'order': {
            'id': order.id,
            'product': {
                'id': order.product.id,
                'name': order.product.name,
                'price': order.product.price,
                'description': order.product.description,
                'image_url': order.product.image_url
            },
            'quantity': order.quantity,
            'total_price': order.total_price,
            'status': order.status,
            'buyer': {
                'id': order.buyer.id,
                'username': order.buyer.username,
                'email': order.buyer.email
            },
            'seller': {
                'id': order.product.seller.id,
                'username': order.product.seller.username,
                'email': order.product.seller.email
            },
            'created_at': order.created_at.isoformat()
        }
    })

@bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if user.role != 'buyer':
        return jsonify({'error': 'Only buyers can create orders'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['product_id', 'quantity']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    product = Product.query.get_or_404(data['product_id'])
    
    # Check if requested quantity is available
    if product.quantity < data['quantity']:
        return jsonify({'error': 'Requested quantity not available'}), 400
    
    # Calculate total price
    total_price = product.price * data['quantity']
    
    new_order = Order(
        buyer_id=current_user_id,
        product_id=product.id,
        quantity=data['quantity'],
        total_price=total_price,
        status='pending'
    )
    
    # Update product quantity
    product.quantity -= data['quantity']
    
    db.session.add(new_order)
    db.session.commit()
    
    return jsonify({
        'message': 'Order created successfully',
        'order': {
            'id': new_order.id,
            'product': {
                'id': product.id,
                'name': product.name,
                'price': product.price
            },
            'quantity': new_order.quantity,
            'total_price': new_order.total_price,
            'status': new_order.status,
            'created_at': new_order.created_at.isoformat()
        }
    }), 201

@bp.route('/<int:order_id>', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    order = Order.query.get_or_404(order_id)
    
    # Only the seller can update order status
    if user.role != 'farmer' or order.product.seller_id != current_user_id:
        return jsonify({'error': 'Unauthorized to update this order'}), 403
    
    data = request.get_json()
    
    if 'status' not in data:
        return jsonify({'error': 'Status is required'}), 400
    
    valid_statuses = ['pending', 'confirmed', 'completed', 'cancelled']
    if data['status'] not in valid_statuses:
        return jsonify({'error': 'Invalid status'}), 400
    
    # If order is cancelled, return quantity to product
    if data['status'] == 'cancelled' and order.status != 'cancelled':
        order.product.quantity += order.quantity
    
    order.status = data['status']
    db.session.commit()
    
    return jsonify({
        'message': 'Order status updated successfully',
        'order': {
            'id': order.id,
            'status': order.status,
            'updated_at': order.created_at.isoformat()
        }
    }) 