# Farm to Market API

A RESTful API for the Farm to Market module of the AgroSmart project. This API enables farmers to list their products and buyers to purchase them, with features for order management, reviews, and user authentication.

## Features

- User authentication (farmers and buyers)
- Product management (CRUD operations)
- Order management
- Review system
- Search functionality
- Role-based access control

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get access token
- `GET /api/auth/me` - Get current user info
- `PUT /api/auth/update` - Update user profile

### Products

- `GET /api/products` - List all products
- `GET /api/products/<id>` - Get product details
- `POST /api/products` - Create new product (farmers only)
- `PUT /api/products/<id>` - Update product (owner only)
- `DELETE /api/products/<id>` - Delete product (owner only)
- `GET /api/products/search` - Search products

### Orders

- `GET /api/orders` - List user's orders
- `GET /api/orders/<id>` - Get order details
- `POST /api/orders` - Create new order (buyers only)
- `PUT /api/orders/<id>/status` - Update order status (farmers only)

### Reviews

- `GET /api/reviews/product/<id>` - Get product reviews
- `POST /api/reviews/product/<id>` - Create review (buyers only)
- `PUT /api/reviews/<id>` - Update review (owner only)
- `DELETE /api/reviews/<id>` - Delete review (owner only)

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with the following variables:
   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key
   JWT_SECRET_KEY=your-jwt-secret-key
   DATABASE_URL=sqlite:///agro_smart.db
   ```
5. Initialize the database:
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```
6. Run the application:
   ```bash
   flask run
   ```

## Deployment

The API is configured for deployment on Railway. The necessary files are:
- `requirements.txt` - Python dependencies
- `Procfile` - Process type declaration
- `runtime.txt` - Python runtime version

## Security

- JWT-based authentication
- Password hashing
- Role-based access control
- Input validation
- CORS enabled

## Error Handling

The API uses standard HTTP status codes and returns JSON responses with error messages when something goes wrong.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 