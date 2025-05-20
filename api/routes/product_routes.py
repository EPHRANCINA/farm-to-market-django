from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.models import Product, User
from api.app import db

bp = Blueprint('products', __name__, url_prefix='/api/products')

@bp.route('', methods=['GET'])
def get_products():
    # Get query parameters
    category = request.args.get('category')
    search = request.args.get('search')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    # Base query
    query = Product.query
    
    # Apply filters
    if category:
        query = query.filter(Product.category == category)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    products = query.all()
    
    return jsonify({
        'products': [{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': p.price,
            'quantity': p.quantity,
            'category': p.category,
            'image_url': p.image_url,
            'seller': {
                'id': p.seller.id,
                'username': p.seller.username
            },
            'created_at': p.created_at.isoformat()
        } for p in products]
    })

@bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({
        'product': {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'quantity': product.quantity,
            'category': product.category,
            'image_url': product.image_url,
            'seller': {
                'id': product.seller.id,
                'username': product.seller.username
            },
            'created_at': product.created_at.isoformat()
        }
    })

@bp.route('', methods=['POST'])
@jwt_required()
def create_product():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if user.role != 'farmer':
        return jsonify({'error': 'Only farmers can create products'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'description', 'price', 'quantity', 'category']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    new_product = Product(
        name=data['name'],
        description=data['description'],
        price=data['price'],
        quantity=data['quantity'],
        category=data['category'],
        image_url=data.get('image_url'),
        seller_id=current_user_id
    )
    
    db.session.add(new_product)
    db.session.commit()
    
    return jsonify({
        'message': 'Product created successfully',
        'product': {
            'id': new_product.id,
            'name': new_product.name,
            'description': new_product.description,
            'price': new_product.price,
            'quantity': new_product.quantity,
            'category': new_product.category,
            'image_url': new_product.image_url,
            'seller_id': new_product.seller_id,
            'created_at': new_product.created_at.isoformat()
        }
    }), 201

@bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    current_user_id = get_jwt_identity()
    product = Product.query.get_or_404(product_id)
    
    if product.seller_id != current_user_id:
        return jsonify({'error': 'Unauthorized to update this product'}), 403
    
    data = request.get_json()
    
    # Update fields if provided
    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    if 'price' in data:
        product.price = data['price']
    if 'quantity' in data:
        product.quantity = data['quantity']
    if 'category' in data:
        product.category = data['category']
    if 'image_url' in data:
        product.image_url = data['image_url']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Product updated successfully',
        'product': {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'quantity': product.quantity,
            'category': product.category,
            'image_url': product.image_url,
            'seller_id': product.seller_id,
            'created_at': product.created_at.isoformat()
        }
    })

@bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    current_user_id = get_jwt_identity()
    product = Product.query.get_or_404(product_id)
    
    if product.seller_id != current_user_id:
        return jsonify({'error': 'Unauthorized to delete this product'}), 403
    
    db.session.delete(product)
    db.session.commit()
    
    return jsonify({'message': 'Product deleted successfully'}) 