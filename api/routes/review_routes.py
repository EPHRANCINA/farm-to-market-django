from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.models import Review, Product, User, Order
from api.app import db
from sqlalchemy import func

bp = Blueprint('reviews', __name__, url_prefix='/api/products')

@bp.route('/<int:product_id>/reviews', methods=['GET'])
def get_product_reviews(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Get query parameters
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    # Base query
    query = Review.query.filter_by(product_id=product_id)
    
    # Apply sorting
    if sort_by == 'rating':
        query = query.order_by(
            Review.rating.desc() if sort_order == 'desc' else Review.rating.asc()
        )
    else:  # default sort by created_at
        query = query.order_by(
            Review.created_at.desc() if sort_order == 'desc' else Review.created_at.asc()
        )
    
    reviews = query.all()
    
    # Calculate average rating
    avg_rating = db.session.query(func.avg(Review.rating)).filter_by(product_id=product_id).scalar() or 0
    
    return jsonify({
        'product': {
            'id': product.id,
            'name': product.name,
            'average_rating': round(float(avg_rating), 2)
        },
        'reviews': [{
            'id': review.id,
            'rating': review.rating,
            'comment': review.comment,
            'user': {
                'id': review.user.id,
                'username': review.user.username
            },
            'created_at': review.created_at.isoformat()
        } for review in reviews]
    })

@bp.route('/<int:product_id>/reviews', methods=['POST'])
@jwt_required()
def create_review(product_id):
    current_user_id = get_jwt_identity()
    product = Product.query.get_or_404(product_id)
    
    # Check if user has purchased the product
    has_purchased = db.session.query(Order).filter_by(
        buyer_id=current_user_id,
        product_id=product_id,
        status='completed'
    ).first()
    
    if not has_purchased:
        return jsonify({'error': 'You must purchase the product before reviewing it'}), 403
    
    # Check if user has already reviewed this product
    existing_review = Review.query.filter_by(
        user_id=current_user_id,
        product_id=product_id
    ).first()
    
    if existing_review:
        return jsonify({'error': 'You have already reviewed this product'}), 400
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['rating']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate rating
    if not isinstance(data['rating'], int) or data['rating'] < 1 or data['rating'] > 5:
        return jsonify({'error': 'Rating must be an integer between 1 and 5'}), 400
    
    new_review = Review(
        user_id=current_user_id,
        product_id=product_id,
        rating=data['rating'],
        comment=data.get('comment', '')
    )
    
    db.session.add(new_review)
    db.session.commit()
    
    return jsonify({
        'message': 'Review created successfully',
        'review': {
            'id': new_review.id,
            'rating': new_review.rating,
            'comment': new_review.comment,
            'user': {
                'id': new_review.user.id,
                'username': new_review.user.username
            },
            'created_at': new_review.created_at.isoformat()
        }
    }), 201

@bp.route('/<int:product_id>/reviews/<int:review_id>', methods=['PUT'])
@jwt_required()
def update_review(product_id, review_id):
    current_user_id = get_jwt_identity()
    review = Review.query.get_or_404(review_id)
    
    # Check if review belongs to the user
    if review.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized to update this review'}), 403
    
    # Check if review belongs to the specified product
    if review.product_id != product_id:
        return jsonify({'error': 'Review does not belong to this product'}), 400
    
    data = request.get_json()
    
    # Update fields if provided
    if 'rating' in data:
        if not isinstance(data['rating'], int) or data['rating'] < 1 or data['rating'] > 5:
            return jsonify({'error': 'Rating must be an integer between 1 and 5'}), 400
        review.rating = data['rating']
    
    if 'comment' in data:
        review.comment = data['comment']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Review updated successfully',
        'review': {
            'id': review.id,
            'rating': review.rating,
            'comment': review.comment,
            'user': {
                'id': review.user.id,
                'username': review.user.username
            },
            'created_at': review.created_at.isoformat()
        }
    })

@bp.route('/<int:product_id>/reviews/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(product_id, review_id):
    current_user_id = get_jwt_identity()
    review = Review.query.get_or_404(review_id)
    
    # Check if review belongs to the user
    if review.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized to delete this review'}), 403
    
    # Check if review belongs to the specified product
    if review.product_id != product_id:
        return jsonify({'error': 'Review does not belong to this product'}), 400
    
    db.session.delete(review)
    db.session.commit()
    
    return jsonify({'message': 'Review deleted successfully'}) 