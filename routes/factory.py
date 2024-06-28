from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from bson import ObjectId
from utils.is_auth import is_auth_for_factory

bp = Blueprint('factory', __name__, url_prefix='/factories')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_factories():
    """
    Get factories associated with the authenticated user.
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

        # Find factories and entities associated with the user's factory ID
        factories = mongo.db.factories.find({"_id": user_factory_id})
        entities = mongo.db.entities.find({"factory_id": user_factory_id})

        result = []

        # Construct the result list with factory details and their associated entities
        for factory in factories:
            factory_entities = [entity['name'] for entity in entities if entity['factory_id'] == factory['_id']]
            result.append({
                "name": factory['name'],
                "location": factory['location'],
                "capacity": factory['capacity'],
                "entities": factory_entities
            })

        return jsonify({"ok": True, "data": result}), 200
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500

@bp.route('/<factory_id>', methods=['PUT'])
@jwt_required()
def update_factory(factory_id):
    """
    Update details of a specific factory.
    """
    try:
        # Get the JSON data from the request
        data = request.get_json()

        # Check if the authenticated user has permission to update the factory
        is_auth, response = is_auth_for_factory(factory_id)
        if not is_auth:
            return response
        
        # Find the factory in the database
        factory = mongo.db.factories.find_one({"_id": ObjectId(factory_id)})
        if not factory:
            return jsonify({"ok": False, "message": "Factory not found"}), 404
        
        # Update the factory with the new data
        mongo.db.factories.update_one({"_id": ObjectId(factory_id)}, {"$set": data})
        return jsonify({"ok": True, "message": "Factory updated successfully"}), 200
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500

@bp.route('/<factory_id>', methods=['DELETE'])
@jwt_required()
def delete_factory(factory_id):
    """
    Delete a specific factory and all related entities.
    """
    try:
        # Find the factory in the database
        factory = mongo.db.factories.find_one({"_id": ObjectId(factory_id)})
        if not factory:
            return jsonify({"ok": False, "message": "Factory not found"}), 404

        # Check if the authenticated user has permission to delete the factory
        is_auth, response = is_auth_for_factory(factory_id)
        if not is_auth:
            return response

        # Delete the factory
        mongo.db.factories.delete_one({"_id": ObjectId(factory_id)})
        
        # Delete all entities related to the factory
        entities = mongo.db.entities.find({"factory_id": ObjectId(factory_id)})
        for entity in entities:
            mongo.db.entities.delete_one({"_id": entity['_id']})

        # Update all users related to the factory
        users = mongo.db.users.find({"factory_id": ObjectId(factory_id)})
        for user in users:
            mongo.db.users.update_one({"_id": user['_id']}, {"$set": {"factory_id": None}})

        return jsonify({"ok": True, "message": "Factory and all related entities deleted successfully"}), 200
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500
