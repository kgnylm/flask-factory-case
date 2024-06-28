from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from models.factory import Factory
from models.entity import Entity
from bson import ObjectId
from utils.is_admin import is_admin_user

bp = Blueprint('admin', __name__, url_prefix='/admin')
"""
Factory CRUD operations for admin
"""
@bp.route('/factories', methods=['POST'])
@jwt_required()
def create_factory():
    data = request.get_json()

    is_admin, response = is_admin_user()
    if not is_admin:
        return response
    
    factory = Factory(name=data['name'], location=data['location'], capacity=data['capacity'])
    mongo.db.factories.insert_one(factory.to_dict())
    return jsonify({"ok": True,
                    "message": "Factory created successfully"}), 201

@bp.route('/factories', methods=['GET'])
@jwt_required()
def get_factories():
    is_admin, response = is_admin_user()
    if not is_admin:
        return response
    factories = mongo.db.factories.find()
    result = []
    for factory in factories:
        result.append({"name": factory['name'], "location": factory['location'], "capacity": factory['capacity']})
    return jsonify({"ok":True,
                   "data": result})

@bp.route('/factories/<factory_id>', methods=['GET'])
@jwt_required()
def get_factory(factory_id):
    is_admin, response = is_admin_user()
    if not is_admin:
        return response
    factory = mongo.db.factories.find_one({"_id": ObjectId(factory_id)})
    if not factory:
        return jsonify({"ok":False,
                        "message": "Factory not found"}), 404
    return jsonify({"ok":True,
                    "data": {"name": factory['name'], "location": factory['location'], "capacity": factory['capacity']}}),200

@bp.route('/factories/<factory_id>', methods=['PUT'])
@jwt_required()
def update_factory(factory_id):
    data = request.get_json()
    is_admin, response = is_admin_user()
    if not is_admin:
        return response
    factory = mongo.db.factories.find_one({"_id": ObjectId(factory_id)})
    if not factory:
        return jsonify({"ok":False,
                        "message": "Factory not found"}), 404
    
    
    mongo.db.factories.update_one({"_id": ObjectId(factory_id)}, {"$set": data})
    return jsonify({"ok":True,
                    "message": "Factory updated successfully"}), 200

@bp.route('/factories/<factory_id>', methods=['DELETE'])
@jwt_required()
def delete_factory(factory_id):
    is_admin, response = is_admin_user()
    if not is_admin:
        return response
    factory = mongo.db.factories.find_one({"_id": ObjectId(factory_id)})
    if not factory:
        return jsonify({"ok":False,
                        "message": "Factory not found"}), 404
    
    
    mongo.db.factories.delete_one({"_id": ObjectId(factory_id)})
    entities = mongo.db.entities.find({"factory_id": ObjectId(factory_id)})
    for entity in entities:
        mongo.db.entities.delete_one({"_id": entity['_id']})
    users = mongo.db.users.find({"factory_id": ObjectId(factory_id)})
    for user in users:
        mongo.db.users.update_one({"_id": user['_id']}, {"$set": {"factory_id": None}})
    return jsonify({"ok":True,
                    "message": "Factory deleted successfully"}), 200

"""
Entity CRUD operations for admin
"""

@bp.route('/entities', methods=['POST'])
@jwt_required()
def create_entity():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('factory_id'):
        return jsonify({"ok":False,
                        "message": "Missing data"}), 400
    
    is_admin, response = is_admin_user()
    if not is_admin:
        return response
    factory = mongo.db.factories.find_one({"_id": ObjectId(data['factory_id'])})
    if not factory:
        return jsonify({"ok":False,
                        "message": "Factory not found"}), 404
    entity = Entity(name=data['name'], factory_id=data['factory_id'])
    mongo.db.entities.insert_one(entity.to_dict())
    return jsonify({"ok":True,
                    "message": "Entity created successfully"}), 201

@bp.route('/entities', methods=['GET'])
@jwt_required()
def get_entities():
    is_admin, response = is_admin_user()
    if not is_admin:
        return response
    entities = mongo.db.entities.find()
    result = []
    for entity in entities:
        factory = mongo.db.factories.find_one({"_id": entity['factory_id']})
        if factory:
            result.append({"name": entity['name'], "factory": factory["name"]})
    return jsonify({"ok":True,
                    "data":result}), 200

@bp.route('/entities/<entity_id>', methods=['GET'])
@jwt_required()
def get_entity(entity_id):
    is_admin, response = is_admin_user()
    if not is_admin:
        return response
    entity = mongo.db.entities.find_one({"_id": ObjectId(entity_id)})
    if not entity:
        return jsonify({"ok":False,
                        "message": "Entity not found"}), 404
    
    
    factory = mongo.db.factories.find_one({"_id": entity['factory_id']})
    return jsonify({"name": entity['name'], "factory": factory['name']}), 200

@bp.route('/entities/<entity_id>', methods=['PUT'])
@jwt_required()
def update_entity(entity_id):
    data = request.get_json()
    is_admin, response = is_admin_user()
    if not is_admin:
        return response
    entity = mongo.db.entities.find_one({"_id": ObjectId(entity_id)})
    if not entity:
        return jsonify({"ok":False,
                        "message": "Entity not found"}), 404
    if 'factory_id' in data:
        try:
            data['factory_id'] = ObjectId(data['factory_id'])
        except:
            return jsonify({"ok":False,
                            "message": "Invalid factory_id format"}), 400
    mongo.db.entities.update_one({"_id": ObjectId(entity_id)}, {"$set": data})
    return jsonify({"ok":True,
                    "message": "Entity updated successfully"}), 200

@bp.route('/entities/<entity_id>', methods=['DELETE'])
@jwt_required()
def delete_entity(entity_id):
    is_admin, response = is_admin_user()
    if not is_admin:
        return response
    entity = mongo.db.entities.find_one({"_id": ObjectId(entity_id)})
    if not entity:
        return jsonify({"ok":False,
                        "message": "Entity not found"}), 404
    mongo.db.entities.delete_one({"_id": ObjectId(entity_id)})
    return jsonify({"ok":True,
                    "message": "Entity deleted successfully"}), 200

"""
User CRUD operations for admin
"""

@bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    is_admin, response = is_admin_user()
    if not is_admin:
        return response
    
    users = mongo.db.users.find()
    result = []
    for user in users:
        factory = mongo.db.factories.find_one({"_id": user.get('factory_id')})
        result.append({
            "username": user['username'],
            "is_admin": user.get('is_admin', False),
            "factory": factory["name"] if factory else None
        })
    return jsonify({"ok":True,
                    "data":result}), 200

@bp.route('/users/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    is_admin, response = is_admin_user()
    if not is_admin:
        return response
    
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"ok":False,
                        "message": "User not found"}), 404
    factory = mongo.db.factories.find_one({"_id": user.get('factory_id')})
    return jsonify({
        "ok": True,
        "username": user['username'],
        "is_admin": user.get('is_admin', False),
        "factory": factory["name"] if factory else None
    }), 200

@bp.route('/users/<user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    data = request.get_json()
    is_admin, response = is_admin_user()
    if not is_admin:
        return response
    
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"ok":False,
                        "message": "User not found"}), 404

    if 'factory_id' in data:
        try:
            data['factory_id'] = ObjectId(data['factory_id'])
        except:
            return jsonify({"ok":False,
                            "message": "Invalid factory_id format"}), 400

    mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": data})
    return jsonify({"ok":True,
                    "message": "User updated successfully"}), 200

@bp.route('/users/<user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    is_admin, response = is_admin_user()
    if not is_admin:
        return response
    
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"ok":False,
                        "message": "User not found"}), 404
    mongo.db.users.delete_one({"_id": ObjectId(user_id)})
    return jsonify({"ok":True,
                    "message": "User deleted successfully"}), 200


