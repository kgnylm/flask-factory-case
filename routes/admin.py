from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from models.factory import Factory
from models.entity import Entity
from bson import ObjectId
from utils.is_admin import is_admin_user
from utils.pagination import paginate, get_pagination_params

bp = Blueprint('admin', __name__, url_prefix='/admin')

"""
Factory CRUD operations for admin
"""
@bp.route('/factories', methods=['POST'])
@jwt_required()
def create_factory():
    """
    Create a new factory. This route is only accessible by admin users.
    """
    data = request.get_json()

    try:
        # Check if the user is an admin
        is_admin, response = is_admin_user()
        if not is_admin:
            return response

        # Validate required fields
        if not data or not data.get('name') or not data.get('location') or not data.get('capacity'):
            return jsonify({"ok": False, "message": "Missing data"}), 400
        
        # Create a new factory object
        factory = Factory(name=data['name'], location=data['location'], capacity=data['capacity'])
        
        # Insert the new factory into the database
        mongo.db.factories.insert_one(factory.to_dict())
        
        return jsonify({"ok": True, "message": "Factory created successfully"}), 201

    except Exception as e:
        # Handle any unexpected errors
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500

@bp.route('/factories', methods=['GET'])
@jwt_required()
def get_factories():
    """
    Get a list of factories with pagination. This route is only accessible by admin users.
    """
    try:
        # Check if the user is an admin
        is_admin, response = is_admin_user()
        if not is_admin:
            return response

        # Get pagination parameters
        page, per_page = get_pagination_params()
        
        # Define the filter for the query (currently empty to get all factories)
        filter = {}
        query = mongo.db.factories.find(filter)
        
        # Apply pagination to the query
        pagination = paginate(query, filter, page, per_page)

        result = []
        # Iterate through the paginated factories
        for factory in pagination['items']:
            # Find entities related to the current factory
            entities = mongo.db.entities.find({"factory_id": factory['_id']})
            factory_entities = [entity['name'] for entity in entities]
            # Add factory details to the result list
            result.append({
                "name": factory['name'],
                "location": factory['location'],
                "capacity": factory['capacity'],
                "entities": factory_entities
            })

        return jsonify({
            "ok": True, 
            "data": result, 
            "pagination": {
                "total": pagination['total'],
                "page": pagination['page'],
                "per_page": pagination['per_page']
            }
        }), 200
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500

@bp.route('/factories/<factory_id>', methods=['GET'])
@jwt_required()
def get_factory(factory_id):
    """
    Get details of a specific factory by its ID. This route is only accessible by admin users.
    """
    try:
        # Check if the user is an admin
        is_admin, response = is_admin_user()
        if not is_admin:
            return response

        # Find the factory by ID
        factory = mongo.db.factories.find_one({"_id": ObjectId(factory_id)})
        if not factory:
            return jsonify({"ok": False, "message": "Factory not found"}), 404

        # Return the factory details
        return jsonify({
            "ok": True,
            "data": {
                "name": factory['name'],
                "location": factory['location'],
                "capacity": factory['capacity']
            }
        }), 200
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500

@bp.route('/factories/<factory_id>', methods=['PUT'])
@jwt_required()
def update_factory(factory_id):
    """
    Update a specific factory by its ID. This route is only accessible by admin users.
    """
    try:
        # Get the request data
        data = request.get_json()

        # Check if the user is an admin
        is_admin, response = is_admin_user()
        if not is_admin:
            return response

        # Find the factory by ID
        factory = mongo.db.factories.find_one({"_id": ObjectId(factory_id)})
        if not factory:
            return jsonify({"ok": False, "message": "Factory not found"}), 404

        # Update the factory with the new data
        mongo.db.factories.update_one({"_id": ObjectId(factory_id)}, {"$set": data})

        return jsonify({"ok": True, "message": "Factory updated successfully"}), 200
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500

@bp.route('/factories/<factory_id>', methods=['DELETE'])
@jwt_required()
def delete_factory(factory_id):
    """
    Delete a specific factory by its ID along with all related entities and users. 
    This route is only accessible by admin users.
    """
    try:
        # Check if the user is an admin
        is_admin, response = is_admin_user()
        if not is_admin:
            return response

        # Find the factory by ID
        factory = mongo.db.factories.find_one({"_id": ObjectId(factory_id)})
        if not factory:
            return jsonify({"ok": False, "message": "Factory not found"}), 404

        # Delete the factory
        mongo.db.factories.delete_one({"_id": ObjectId(factory_id)})

        # Delete all related entities
        entities = mongo.db.entities.find({"factory_id": ObjectId(factory_id)})
        for entity in entities:
            mongo.db.entities.delete_one({"_id": entity['_id']})

        # Update all related users to remove the factory reference
        users = mongo.db.users.find({"factory_id": ObjectId(factory_id)})
        for user in users:
            mongo.db.users.update_one({"_id": user['_id']}, {"$set": {"factory_id": None}})

        return jsonify({"ok": True, "message": "Factory and all related entities deleted successfully"}), 200
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500

"""
Entity CRUD operations for admin
"""

@bp.route('/entities', methods=['POST'])
@jwt_required()
def create_entity():
    """
    Create a new entity. This route is only accessible by admin users.
    """
    try:
        # Get the request data
        data = request.get_json()
        if not data or not data.get('name') or not data.get('factory_id'):
            return jsonify({"ok": False, "message": "Missing data"}), 400

        # Check if the user is an admin
        is_admin, response = is_admin_user()
        if not is_admin:
            return response

        # Find the factory by ID
        factory = mongo.db.factories.find_one({"_id": ObjectId(data['factory_id'])})
        if not factory:
            return jsonify({"ok": False, "message": "Factory not found"}), 404

        # Create the entity
        entity = Entity(name=data['name'], factory_id=data['factory_id'])
        mongo.db.entities.insert_one(entity.to_dict())

        return jsonify({"ok": True, "message": "Entity created successfully"}), 201
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500

@bp.route('/entities', methods=['GET'])
@jwt_required()
def get_entities():
    """
    Get a list of all entities with pagination. This route is only accessible by admin users.
    """
    try:
        # Check if the user is an admin
        is_admin, response = is_admin_user()
        if not is_admin:
            return response

        # Get pagination parameters
        page, per_page = get_pagination_params()

        # Define the filter for the query
        filter = {}

        # Execute the query with pagination
        query = mongo.db.entities.find(filter)
        pagination = paginate(query, filter, page, per_page)

        # Build the result list
        result = []
        for entity in pagination['items']:
            factory = mongo.db.factories.find_one({"_id": entity['factory_id']})
            if factory:
                result.append({"name": entity['name'], "factory": factory["name"]})

        # Return the result with pagination information
        return jsonify({"ok": True, "data": result, "pagination": {
            "total": pagination['total'],
            "page": pagination['page'],
            "per_page": pagination['per_page']
        }}), 200
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500

@bp.route('/entities/<entity_id>', methods=['GET'])
@jwt_required()
def get_entity(entity_id):
    """
    Get the details of a specific entity by its ID. This route is only accessible by admin users.
    """
    try:
        # Check if the user is an admin
        is_admin, response = is_admin_user()
        if not is_admin:
            return response

        # Find the entity by its ID
        entity = mongo.db.entities.find_one({"_id": ObjectId(entity_id)})
        if not entity:
            return jsonify({"ok": False, "message": "Entity not found"}), 404

        # Find the associated factory for the entity
        factory = mongo.db.factories.find_one({"_id": entity['factory_id']})
        if not factory:
            return jsonify({"ok": False, "message": "Factory not found"}), 404

        # Return the entity and its associated factory details
        return jsonify({"ok": True, "name": entity['name'], "factory": factory['name']}), 200
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500

@bp.route('/entities/<entity_id>', methods=['PUT'])
@jwt_required()
def update_entity(entity_id):
    """
    Update the details of a specific entity by its ID. This route is only accessible by admin users.
    """
    try:
        # Get the request data
        data = request.get_json()

        # Check if the user is an admin
        is_admin, response = is_admin_user()
        if not is_admin:
            return response

        # Find the entity by its ID
        entity = mongo.db.entities.find_one({"_id": ObjectId(entity_id)})
        if not entity:
            return jsonify({"ok": False, "message": "Entity not found"}), 404

        # If factory_id is provided in the data, convert it to ObjectId and validate it
        if 'factory_id' in data:
            try:
                data['factory_id'] = ObjectId(data['factory_id'])
            except Exception:
                return jsonify({"ok": False, "message": "Invalid factory_id format"}), 400

        # Update the entity with the provided data
        mongo.db.entities.update_one({"_id": ObjectId(entity_id)}, {"$set": data})
        return jsonify({"ok": True, "message": "Entity updated successfully"}), 200

    except Exception as e:
        # Handle any unexpected errors
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500

@bp.route('/entities/<entity_id>', methods=['DELETE'])
@jwt_required()
def delete_entity(entity_id):
    """
    Delete a specific entity by its ID. This route is only accessible by admin users.
    """
    try:
        # Check if the user is an admin
        is_admin, response = is_admin_user()
        if not is_admin:
            return response

        # Find the entity by its ID
        entity = mongo.db.entities.find_one({"_id": ObjectId(entity_id)})
        if not entity:
            return jsonify({"ok": False, "message": "Entity not found"}), 404

        # Delete the entity
        mongo.db.entities.delete_one({"_id": ObjectId(entity_id)})
        return jsonify({"ok": True, "message": "Entity deleted successfully"}), 200

    except Exception as e:
        # Handle any unexpected errors
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500

"""
User CRUD operations for admin
"""

@bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """
    Retrieve a paginated list of users. This route is only accessible by admin users.
    """
    try:
        # Check if the user is an admin
        is_admin, response = is_admin_user()
        if not is_admin:
            return response

        # Get pagination parameters from the request
        page, per_page = get_pagination_params()
        filter = {}
        
        # Execute the query with pagination
        query = mongo.db.users.find(filter)
        pagination = paginate(query, filter, page, per_page)

        result = []
        # Process each user in the paginated results
        for user in pagination['items']:
            factory = mongo.db.factories.find_one({"_id": user.get('factory_id')})
            result.append({
                "username": user['username'],
                "is_admin": user.get('is_admin', False),
                "factory": factory["name"] if factory else None
            })

        # Return the paginated list of users
        return jsonify({
            "ok": True, 
            "data": result, 
            "pagination": {
                "total": pagination['total'],
                "page": pagination['page'],
                "per_page": pagination['per_page']
            }
        }), 200
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500

@bp.route('/users/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """
    Retrieve details of a specific user by user_id. This route is only accessible by admin users.
    """
    try:
        # Check if the user is an admin
        is_admin, response = is_admin_user()
        if not is_admin:
            return response
        
        # Find the user by user_id
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"ok": False, "message": "User not found"}), 404
        
        # Find the factory associated with the user
        factory = mongo.db.factories.find_one({"_id": user.get('factory_id')})
        
        # Return the user details
        return jsonify({
            "ok": True,
            "username": user['username'],
            "is_admin": user.get('is_admin', False),
            "factory": factory["name"] if factory else None
        }), 200
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500

@bp.route('/users/<user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """
    Update details of a specific user by user_id. This route is only accessible by admin users.
    """
    try:
        # Get the JSON data from the request
        data = request.get_json()
        
        # Check if the user is an admin
        is_admin, response = is_admin_user()
        if not is_admin:
            return response
        
        # Find the user by user_id
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"ok": False, "message": "User not found"}), 404

        # Validate and convert factory_id if present in the data
        if 'factory_id' in data:
            try:
                data['factory_id'] = ObjectId(data['factory_id'])
            except:
                return jsonify({"ok": False, "message": "Invalid factory_id format"}), 400

        # Update the user with the new data
        mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": data})
        
        return jsonify({"ok": True, "message": "User updated successfully"}), 200
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500

@bp.route('/users/<user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """
    Delete a specific user by user_id. This route is only accessible by admin users.
    """
    try:
        # Check if the user is an admin
        is_admin, response = is_admin_user()
        if not is_admin:
            return response
        
        # Find the user by user_id
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"ok": False, "message": "User not found"}), 404
        
        # Delete the user
        mongo.db.users.delete_one({"_id": ObjectId(user_id)})
        
        return jsonify({"ok": True, "message": "User deleted successfully"}), 200
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500




