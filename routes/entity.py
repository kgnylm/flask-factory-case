from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from models.entity import Entity
from bson import ObjectId
from utils.pagination import paginate, get_pagination_params
from models.entity import Entity

bp = Blueprint('entity', __name__, url_prefix='/entities')

@bp.route('/', methods=['POST'])
@jwt_required()
def create_entity():
    """
    Create a new entity for the authenticated user's factory.
    """
    try:
        data = request.get_json()

        # Check if the request data contains both name and factory_id
        if not data or not data.get('name') or not data.get('factory_id'):
            return jsonify({"ok": False, "message": "Missing data"}), 400

        # Get the current authenticated user's username
        username = get_jwt_identity()
        user = mongo.db.users.find_one({"username": username})

        # Check if the user exists in the database
        if not user:
            return jsonify({"ok": False, "message": "User not found"}), 404

        # Verify the user's factory ID matches the provided factory ID
        user_factory_id = user.get('factory_id')
        if not user_factory_id or user_factory_id != ObjectId(data['factory_id']):
            return jsonify({"ok": False, "message": "Not Auth"}), 401

        # Create a new entity and insert it into the database
        entity = Entity(name=data['name'], factory_id=data['factory_id'])
        mongo.db.entities.insert_one(entity.to_dict())
        return jsonify({"ok": True, "message": "Entity created successfully"}), 201
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500

@bp.route('/', methods=['GET'])
@jwt_required()
def get_entity():
    """
    Get entities for the authenticated user's factory with pagination.
    """
    try:
        # Get the current authenticated user's username
        username = get_jwt_identity()
        user = mongo.db.users.find_one({"username": username})

        # Check if the user exists in the database
        if not user:
            return jsonify({"ok": False, "message": "User not found"}), 404

        # Get the user's factory ID
        user_factory_id = user.get('factory_id')

        # Get pagination parameters from the request
        page, per_page = get_pagination_params()
        filter = {"factory_id": user_factory_id}

        # Query the entities collection with pagination
        query = mongo.db.entities.find(filter)
        pagination = paginate(query, filter, page, per_page)

        # Get the factory details
        factory = mongo.db.factories.find_one({"_id": user_factory_id})
        
        # Prepare the result list with entity and factory details
        result = []
        for entity in pagination['items']:
            result.append({"name": entity['name'], "factory": factory['name']})

        # Return the paginated entities along with pagination metadata
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

@bp.route('/<entity_id>', methods=['PUT'])
@jwt_required()
def update_entity(entity_id):
    """
    Update a specific entity's details.
    """
    try:
        # Get the current authenticated user's username
        username = get_jwt_identity()
        user = mongo.db.users.find_one({"username": username})

        # Check if the user exists in the database
        if not user:
            return jsonify({"ok": False, "message": "User not found"}), 404
        
        # Get the user's factory ID
        user_factory_id = user.get('factory_id')

        # Find the entity to be updated
        entity = mongo.db.entities.find_one({"_id": ObjectId(entity_id)})
        if not entity:
            return jsonify({"ok": False, "message": "Entity not found"}), 404

        # Check if the user is authorized to update this entity
        if not user_factory_id or user_factory_id != entity['factory_id']:
            return jsonify({"ok": False, "message": "Not Auth"}), 401

        # Get the updated data from the request
        data = request.get_json()
        
        # Validate and convert factory_id if present in the updated data
        if 'factory_id' in data:
            try:
                data['factory_id'] = ObjectId(data['factory_id'])
            except:
                return jsonify({"ok": False, "message": "Invalid factory_id format"}), 400
        
        # Update the entity in the database
        mongo.db.entities.update_one({"_id": ObjectId(entity_id)}, {"$set": data})
        return jsonify({"ok": True, "message": "Entity updated successfully"}), 200
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500

@bp.route('/<entity_id>', methods=['DELETE'])
@jwt_required()
def delete_entity(entity_id):
    """
    Delete a specific entity.
    """
    try:
        # Get the current authenticated user's username
        username = get_jwt_identity()
        user = mongo.db.users.find_one({"username": username})

        # Check if the user exists in the database
        if not user:
            return jsonify({"ok": False, "message": "User not found"}), 404
        
        # Get the user's factory ID
        user_factory_id = user.get('factory_id')

        # Find the entity to be deleted
        entity = mongo.db.entities.find_one({"_id": ObjectId(entity_id)})
        if not entity:
            return jsonify({"ok": False, "message": "Entity not found"}), 404

        # Check if the user is authorized to delete this entity
        if not user_factory_id or user_factory_id != entity['factory_id']:
            return jsonify({"ok": False, "message": "Not Auth"}), 401

        # Delete the entity from the database
        mongo.db.entities.delete_one({"_id": ObjectId(entity_id)})

        return jsonify({"ok": True, "message": "Entity deleted successfully"}), 200
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500
