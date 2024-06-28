from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from bson import ObjectId
from utils.is_auth import is_auth_for_factory

bp = Blueprint('factory', __name__, url_prefix='/factories')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_factories():
    username = get_jwt_identity()
    user = mongo.db.users.find_one({"username": username})
    if not user:
        return jsonify({"ok":False,
                        "message": "User not found"}), 404
    user_factory_id = user.get('factory_id')
    factories = mongo.db.factories.find({"_id": user_factory_id})
    entities = mongo.db.entities.find({"factory_id": user_factory_id})

    result = []

    for factory in factories:
        result.append({"name": factory['name'], "location": factory['location'], "capacity": factory['capacity'], "entities": [ entity['name'] for entity in entities ]})
    return jsonify({"ok":True,
                    "data": result}), 200


@bp.route('/<factory_id>', methods=['PUT'])
@jwt_required()
def update_factory(factory_id):
    data = request.get_json()
    is_auth, response = is_auth_for_factory(factory_id)
    if not is_auth:
        return response
    
    factory = mongo.db.factories.find_one({"_id": ObjectId(factory_id)})
    if not factory:
        return jsonify({"ok": False,
                        "message": "Factory not found"}), 404
    
    mongo.db.factories.update_one({"_id": ObjectId(factory_id)}, {"$set": data})
    return jsonify({"ok": True,
                    "message": "Factory updated successfully"}), 200
@bp.route('/<factory_id>', methods=['DELETE'])
@jwt_required()
def delete_factory(factory_id):
    factory = mongo.db.factories.find_one({"_id": ObjectId(factory_id)})
    if not factory:
        return jsonify({"ok": False,
                        "message": "Factory not found"}), 404

    is_auth, response = is_auth_for_factory(factory_id)
    if not is_auth:
        return response

    mongo.db.factories.delete_one({"_id": ObjectId(factory_id)})
    entities = mongo.db.entities.find({"factory_id": ObjectId(factory_id)})
    for entity in entities:
        mongo.db.entities.delete_one({"_id": entity['_id']})
    users = mongo.db.users.find({"factory_id": ObjectId(factory_id)})
    for user in users:
        mongo.db.users.update_one({"_id": user['_id']}, {"$set": {"factory_id": None}})

    return jsonify({"ok": True,
                    "message": "Factory and all related entities deleted successfully"}), 200
