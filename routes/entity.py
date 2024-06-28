from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from models.entity import Entity
from bson import ObjectId

from models.entity import Entity

bp = Blueprint('entity', __name__, url_prefix='/entities')

@bp.route('/', methods=['POST'])
@jwt_required()
def create_entity():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('factory_id'):
        return jsonify({"ok":False,
                        "message": "Missing data"}), 400
    
    username = get_jwt_identity()
    user = mongo.db.users.find_one({"username": username})
    if not user:
        return jsonify({"ok":False,
                        "message": "User not found"}), 404
    
    user_factory_id = user.get('factory_id')
    if not user_factory_id or user_factory_id != ObjectId(data['factory_id']):
        return jsonify({"ok": False, "message": "Not Auth"}), 401
    entity = Entity(name=data['name'], factory_id=data['factory_id'])
    mongo.db.entities.insert_one(entity.to_dict())
    return jsonify({"ok":True,
                    "message": "Entity created successfully"}), 201


@bp.route('/', methods=['GET'])
@jwt_required()
def get_entity():
    username = get_jwt_identity()
    user = mongo.db.users.find_one({"username": username})
    if not user:
        return jsonify({"ok":False,
                        "message": "User not found"}), 404
    user_factory_id = user.get('factory_id')
    entities = mongo.db.entities.find({"factory_id": user_factory_id})
    factory = mongo.db.factories.find_one({"_id": user_factory_id})
    result = []
    for entity in entities:
        result.append({"name": entity['name'], "factory": factory['name']})
    return jsonify({"ok":True,
                    "data":result})


@bp.route('/<entity_id>', methods=['PUT'])
@jwt_required()
def update_entity(entity_id):
    username = get_jwt_identity()
    user = mongo.db.users.find_one({"username": username})
    if not user:
        return jsonify({"ok":False,
                        "message": "User not found"}), 404
    user_factory_id = user.get('factory_id')

    entity = mongo.db.entities.find_one({"_id": ObjectId(entity_id)})
    if not entity:
        return jsonify({"ok":False,
                        "message": "Entity not found"}), 404
    if not user_factory_id or user_factory_id != entity['factory_id']:
        return jsonify({"ok":False,
                        "message": "Not Auth"}), 401
    
    data =request.get_json()
    if 'factory_id' in data:
        try:
            data['factory_id'] = ObjectId(data['factory_id'])
        except:
            return jsonify({"ok":False,
                            "message": "Invalid factory_id format"}), 400
    mongo.db.entities.update_one({"_id": ObjectId(entity_id)}, {"$set": data})
    return jsonify({"ok":True,
                    "message": "Entity updated successfully"}), 200

@bp.route('/<entity_id>', methods=['DELETE'])
@jwt_required()
def delete_entity(entity_id):
    username = get_jwt_identity()
    user = mongo.db.users.find_one({"username": username})
    if not user:
        return jsonify({"ok":False,
                        "message": "User not found"}), 404
    user_factory_id = user.get('factory_id')

    entity = mongo.db.entities.find_one({"_id": ObjectId(entity_id)})
    if not entity:
        return jsonify({"ok":False,
                        "message": "Entity not found"}), 404
    if not user_factory_id or user_factory_id != entity['factory_id']:
        return jsonify({"ok":False,
                        "message": "Not Auth"}), 401
    
    mongo.db.entities.delete_one({"_id": ObjectId(entity_id)})

    return jsonify({"ok":True,
                    "message": "Entity deleted successfully"}), 200
    

