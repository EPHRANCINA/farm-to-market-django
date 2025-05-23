from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.product import Product
from models.user import User
from app import db

products_bp = Blueprint('products', __name__)

@products_bp.route('/', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([product.to_dict() for product in products]), 200

@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict()), 200

@products_bp.route('/', methods=['POST'])
@jwt_required()
def create_product():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role != 'farmer':
        return jsonify({'error': 'Only farmers can create products'}), 403
    
    data = request.get_json()
    product = Product(
        name=data['name'],
        description=data.get('description'),
        price=data['price'],
        quantity=data['quantity'],
        unit=data['unit'],
        category=data.get('category'),
        image_url=data.get('image_url'),
        seller_id=user_id
    )
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify({
        'message': 'Product created successfully',
        'product': product.to_dict()
    }), 201

@products_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    user_id = get_jwt_identity()
    product = Product.query.get_or_404(product_id)
    
    if product.seller_id != user_id:
        return jsonify({'error': 'Unauthorized to update this product'}), 403
    
    data = request.get_json()
    
    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    if 'price' in data:
        product.price = data['price']
    if 'quantity' in data:
        product.quantity = data['quantity']
    if 'unit' in data:
        product.unit = data['unit']
    if 'category' in data:
        product.category = data['category']
    if 'image_url' in data:
        product.image_url = data['image_url']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Product updated successfully',
        'product': product.to_dict()
    }), 200

@products_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    user_id = get_jwt_identity()
    product = Product.query.get_or_404(product_id)
    
    if product.seller_id != user_id:
        return jsonify({'error': 'Unauthorized to delete this product'}), 403
    
    db.session.delete(product)
    db.session.commit()
    
    return jsonify({'message': 'Product deleted successfully'}), 200

@products_bp.route('/search', methods=['GET'])
def search_products():
    query = request.args.get('q', '')
    category = request.args.get('category')
    
    products_query = Product.query
    
    if query:
        products_query = products_query.filter(
            Product.name.ilike(f'%{query}%') |
            Product.description.ilike(f'%{query}%')
        )
    
    if category:
        products_query = products_query.filter_by(category=category)
    
    products = products_query.all()
    return jsonify([product.to_dict() for product in products]), 200 