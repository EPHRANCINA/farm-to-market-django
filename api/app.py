from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///agro_smart.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Import models and routes
from api.models import User, Product, Order, Message, Review
from api.routes import auth_routes, product_routes, order_routes, message_routes, review_routes

# Register blueprints
app.register_blueprint(auth_routes.bp)
app.register_blueprint(product_routes.bp)
app.register_blueprint(order_routes.bp)
app.register_blueprint(message_routes.bp)
app.register_blueprint(review_routes.bp)

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Farm to Market API is running'
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000))) 