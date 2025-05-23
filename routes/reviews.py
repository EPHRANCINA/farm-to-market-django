from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.review import Review
from models.product import Product
from models.order import Order, OrderItem
from app import db

reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('/product/<int:product_id>', methods=['GET'])
def get_product_reviews(product_id):
    reviews = Review.query.filter_by(product_id=product_id).all()
    return jsonify([review.to_dict() for review in reviews]), 200

@reviews_bp.route('/product/<int:product_id>', methods=['POST'])
@jwt_required()
def create_review(product_id):
    user_id = get_jwt_identity()
    
    # Check if product exists
    product = Product.query.get_or_404(product_id)
    
    # Check if user has purchased the product
    has_purchased = Order.query.join(OrderItem).filter(
        Order.buyer_id == user_id,
        OrderItem.product_id == product_id,
        Order.status == 'delivered'
    ).first()
    
    if not has_purchased:
        return jsonify({'error': 'You can only review products you have purchased'}), 403
    
    # Check if user has already reviewed this product
    existing_review = Review.query.filter_by(
        user_id=user_id,
        product_id=product_id
    ).first()
    
    if existing_review:
        return jsonify({'error': 'You have already reviewed this product'}), 400
    
    data = request.get_json()
    
    if not 1 <= data['rating'] <= 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    
    review = Review(
        user_id=user_id,
        product_id=product_id,
        rating=data['rating'],
        comment=data.get('comment')
    )
    
    db.session.add(review)
    db.session.commit()
    
    return jsonify({
        'message': 'Review created successfully',
        'review': review.to_dict()
    }), 201

@reviews_bp.route('/<int:review_id>', methods=['PUT'])
@jwt_required()
def update_review(review_id):
    user_id = get_jwt_identity()
    review = Review.query.get_or_404(review_id)
    
    if review.user_id != user_id:
        return jsonify({'error': 'Unauthorized to update this review'}), 403
    
    data = request.get_json()
    
    if 'rating' in data:
        if not 1 <= data['rating'] <= 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        review.rating = data['rating']
    
    if 'comment' in data:
        review.comment = data['comment']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Review updated successfully',
        'review': review.to_dict()
    }), 200

@reviews_bp.route('/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    user_id = get_jwt_identity()
    review = Review.query.get_or_404(review_id)
    
    if review.user_id != user_id:
        return jsonify({'error': 'Unauthorized to delete this review'}), 403
    
    db.session.delete(review)
    db.session.commit()
    
    return jsonify({'message': 'Review deleted successfully'}), 200 