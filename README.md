# Flask MongoDB Application

This is a Flask application using MongoDB for data storage. The application implements various routes to manage factories, entities, and users, including authentication, authorization, and pagination functionalities.

## Prerequisites

- Python 3.7+
- MongoDB

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/kgnylm/flask-factory-case.git
   cd flask-factory-case

   ```

2. Install the required packages  
   pip/pip3 install -r requirements.txt

3. Run the application  
   python/python3 app.py

### .env file

SECRET_KEY=your-secret-key  
 JWT_SECRET_KEY=jwt-secret-key  
 MONGO_URI=mongodb://localhost:27017/case

## Routes

### Authentication and Authorization

POST /register: Register a new user.  
POST /adminregister: Register a new admin user.  
POST /login: Authenticate a user and get a JWT token.

### Factories

GET /factories: Get a active user's factory  
PUT /factories/<factory_id>: Update user's related factory  
DELETE /factories/<factory_id>: Delete user's related factory

### Entities

GET /entities: Get a list of entities user's related factory with pagination.  
POST /entities: Create a new entity of in user's related factory.  
PUT /entities/<entity_id>: Update a specific entity from user's related factory.  
DELETE /entities/<entity_id>: Delete a specific entity from user's related factory.

### Admin

POST /admin/factories: Create a new factory. (Admin only).  
GET /admin/factories: Get all factories. (Admin only).  
GET /admin/factories/<factory_id>: Get details of a specific factory. (Admin only).  
PUT /admin/factories/<factory_id>: Update a specific factory. (Admin only).  
DELETE /admin/factories/<factory_id>: Delete a specific factory. (Admin only).

POST /admin/entities: Create a new entity. (Admin only).  
GET /admin/entities: Get all entities with pagination (Admin only).  
GET /admin/entities/<entitiy_id>: Get a specific entity. (Admin only).  
PUT /admin/entities/<entitiy_id>: Update a specific entity. (Admin only).  
DELETE /admin/entities/<entitiy_id>: Delete a specific entity. (Admin only).

GET /admin/users: Get all users with pagination (Admin only).  
GET /admin/users/<user_id>: Get a specific user (Admin only).  
PUT /admin/users/<user_id>: Update a specific user (Admin only).  
DELETE /admin/users/<user_id>: Delete a specific user (Admin only).

### Pagination

Pagination is implemented using the paginate function in utils/pagination.py. The function takes a MongoDB query, filters, and pagination parameters (page and per_page) and returns the paginated result along with metadata.
