from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.models import Message, User
from api.app import db
from sqlalchemy import or_

bp = Blueprint('messages', __name__, url_prefix='/api/messages')

@bp.route('', methods=['GET'])
@jwt_required()
def get_messages():
    current_user_id = get_jwt_identity()
    
    # Get query parameters
    conversation_with = request.args.get('with')
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    
    # Base query - get messages where user is either sender or receiver
    query = Message.query.filter(
        or_(
            Message.sender_id == current_user_id,
            Message.receiver_id == current_user_id
        )
    )
    
    # Filter by conversation partner if specified
    if conversation_with:
        query = query.filter(
            or_(
                and_(Message.sender_id == current_user_id, Message.receiver_id == conversation_with),
                and_(Message.sender_id == conversation_with, Message.receiver_id == current_user_id)
            )
        )
    
    # Filter unread messages if requested
    if unread_only:
        query = query.filter(Message.receiver_id == current_user_id, Message.is_read == False)
    
    messages = query.order_by(Message.created_at.desc()).all()
    
    return jsonify({
        'messages': [{
            'id': message.id,
            'content': message.content,
            'is_read': message.is_read,
            'sender': {
                'id': message.sender.id,
                'username': message.sender.username
            },
            'receiver': {
                'id': message.receiver.id,
                'username': message.receiver.username
            },
            'created_at': message.created_at.isoformat()
        } for message in messages]
    })

@bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    current_user_id = get_jwt_identity()
    
    # Get all unique users the current user has conversed with
    conversations = db.session.query(
        User.id,
        User.username,
        Message.created_at.label('last_message_time')
    ).join(
        Message,
        or_(
            and_(Message.sender_id == current_user_id, Message.receiver_id == User.id),
            and_(Message.sender_id == User.id, Message.receiver_id == current_user_id)
        )
    ).filter(User.id != current_user_id).distinct().all()
    
    return jsonify({
        'conversations': [{
            'user': {
                'id': conv.id,
                'username': conv.username
            },
            'last_message_time': conv.last_message_time.isoformat()
        } for conv in conversations]
    })

@bp.route('', methods=['POST'])
@jwt_required()
def send_message():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['receiver_id', 'content']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if receiver exists
    receiver = User.query.get_or_404(data['receiver_id'])
    
    new_message = Message(
        sender_id=current_user_id,
        receiver_id=receiver.id,
        content=data['content']
    )
    
    db.session.add(new_message)
    db.session.commit()
    
    return jsonify({
        'message': 'Message sent successfully',
        'data': {
            'id': new_message.id,
            'content': new_message.content,
            'sender': {
                'id': new_message.sender.id,
                'username': new_message.sender.username
            },
            'receiver': {
                'id': new_message.receiver.id,
                'username': new_message.receiver.username
            },
            'created_at': new_message.created_at.isoformat()
        }
    }), 201

@bp.route('/<int:message_id>/read', methods=['PUT'])
@jwt_required()
def mark_as_read(message_id):
    current_user_id = get_jwt_identity()
    message = Message.query.get_or_404(message_id)
    
    # Check if user is the receiver
    if message.receiver_id != current_user_id:
        return jsonify({'error': 'Unauthorized to mark this message as read'}), 403
    
    message.is_read = True
    db.session.commit()
    
    return jsonify({
        'message': 'Message marked as read',
        'data': {
            'id': message.id,
            'is_read': message.is_read
        }
    })

@bp.route('/unread/count', methods=['GET'])
@jwt_required()
def get_unread_count():
    current_user_id = get_jwt_identity()
    
    count = Message.query.filter_by(
        receiver_id=current_user_id,
        is_read=False
    ).count()
    
    return jsonify({
        'unread_count': count
    }) 