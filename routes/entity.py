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
        return jsonify({"message": "Missing data"}), 400
    
    username = get_jwt_identity()
    user = mongo.db.users.find_one({"username": username})
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    user_factory_id = user.get('factory_id')
    if not user_factory_id or user_factory_id != ObjectId(data['factory_id']):
        return jsonify({"ok": False, "message": "Not Auth"}), 401
    entity = Entity(name=data['name'], factory_id=data['factory_id'])
    mongo.db.entities.insert_one(entity.to_dict())
    return jsonify({"message": "Entity created successfully"}), 201

@bp.route('/', methods=['GET'])
@jwt_required()
def get_entities():
    entities = mongo.db.entities.find()
    result = []
    for entity in entities:
        result.append({"name": entity['name'], "factory": entity['factory']})
    return jsonify(result)

@bp.route('/<entity_id>', methods=['GET'])
@jwt_required()
def get_entity(entity_id):
    entity = mongo.db.entities.find_one({"_id": ObjectId(entity_id)})
    if not entity:
        return jsonify({"message": "Entity not found"}), 404
    
    username = get_jwt_identity()
    user = mongo.db.users.find_one({"username": username})
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    user_factory_id = user.get('factory_id')
    if not user_factory_id or user_factory_id != entity['factory_id']:
        return jsonify({"ok": False, "message": "Not Auth"}), 401
    return jsonify({"name": entity['name']})
