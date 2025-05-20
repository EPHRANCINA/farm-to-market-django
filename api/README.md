# Farm to Market API

This is the API for the Farm to Market module of the AgroSmart mobile application. It provides endpoints for managing products, orders, messages, and user interactions between farmers and buyers.

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the api directory with the following variables:
```
DATABASE_URL=sqlite:///agro_smart.db
JWT_SECRET_KEY=your-secret-key-here
```

4. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

5. Run the API:
```bash
python app.py
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get access token

### Products
- `GET /api/products` - Get all products
- `GET /api/products/<id>` - Get product details
- `POST /api/products` - Create new product (requires authentication)
- `PUT /api/products/<id>` - Update product (requires authentication)
- `DELETE /api/products/<id>` - Delete product (requires authentication)

### Orders
- `GET /api/orders` - Get user's orders (requires authentication)
- `POST /api/orders` - Create new order (requires authentication)
- `PUT /api/orders/<id>` - Update order status (requires authentication)

### Messages
- `GET /api/messages` - Get user's messages (requires authentication)
- `POST /api/messages` - Send new message (requires authentication)
- `PUT /api/messages/<id>/read` - Mark message as read (requires authentication)

### Reviews
- `GET /api/products/<id>/reviews` - Get product reviews
- `POST /api/products/<id>/reviews` - Add product review (requires authentication)

## Authentication

Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:
```
Authorization: Bearer <your-access-token>
```

## Response Format

All responses are in JSON format with the following structure:
```json
{
    "status": "success/error",
    "data": {}, // Response data
    "message": "Optional message"
}
```

## Error Handling

The API uses standard HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

Error responses include a message explaining the error:
```json
{
    "error": "Error message"
}
``` 