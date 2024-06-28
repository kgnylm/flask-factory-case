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
    data = request.get_json()

    try:
        is_admin, response = is_admin_user()
        if not is_admin:
            return response

        if not data or not data.get('name') or not data.get('location') or not data.get('capacity'):
            return jsonify({"ok": False, "message": "Missing data"}), 400
        
        factory = Factory(name=data['name'], location=data['location'], capacity=data['capacity'])
        mongo.db.factories.insert_one(factory.to_dict())
        return jsonify({"ok": True, "message": "Factory created successfully"}), 201

    except Exception as e:
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500

@bp.route('/factories', methods=['GET'])
@jwt_required()
def get_factories():
    try:
        is_admin, response = is_admin_user()
        if not is_admin:
            return response

        page, per_page = get_pagination_params()
        filter = {}
        query = mongo.db.factories.find(filter)
        pagination = paginate(query, filter, page, per_page)

        result = []
        for factory in pagination['items']:
            entities = mongo.db.entities.find({"factory_id": factory['_id']})
            factory_entities = [entity['name'] for entity in entities]
            result.append({
                "name": factory['name'],
                "location": factory['location'],
                "capacity": factory['capacity'],
                "entities": factory_entities
            })

        return jsonify({"ok": True, "data": result, "pagination": {
            "total": pagination['total'],
            "page": pagination['page'],
            "per_page": pagination['per_page']
        }}), 200
    except Exception as e:
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500


@bp.route('/factories/<factory_id>', methods=['GET'])
@jwt_required()
def get_factory(factory_id):
    try:
        is_admin, response = is_admin_user()
        if not is_admin:
            return response
        factory = mongo.db.factories.find_one({"_id": ObjectId(factory_id)})
        if not factory:
            return jsonify({"ok": False, "message": "Factory not found"}), 404
        return jsonify({"ok": True, "data": {"name": factory['name'], "location": factory['location'], "capacity": factory['capacity']}}), 200
    except Exception as e:
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500


@bp.route('/factories/<factory_id>', methods=['PUT'])
@jwt_required()
def update_factory(factory_id):
    try:
        data = request.get_json()
        is_admin, response = is_admin_user()
        if not is_admin:
            return response
        factory = mongo.db.factories.find_one({"_id": ObjectId(factory_id)})
        if not factory:
            return jsonify({"ok": False, "message": "Factory not found"}), 404

        mongo.db.factories.update_one({"_id": ObjectId(factory_id)}, {"$set": data})
        return jsonify({"ok": True, "message": "Factory updated successfully"}), 200
    except Exception as e:
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500


@bp.route('/factories/<factory_id>', methods=['DELETE'])
@jwt_required()
def delete_factory(factory_id):
    try:
        is_admin, response = is_admin_user()
        if not is_admin:
            return response
        factory = mongo.db.factories.find_one({"_id": ObjectId(factory_id)})
        if not factory:
            return jsonify({"ok": False, "message": "Factory not found"}), 404

        mongo.db.factories.delete_one({"_id": ObjectId(factory_id)})
        entities = mongo.db.entities.find({"factory_id": ObjectId(factory_id)})
        for entity in entities:
            mongo.db.entities.delete_one({"_id": entity['_id']})
        users = mongo.db.users.find({"factory_id": ObjectId(factory_id)})
        for user in users:
            mongo.db.users.update_one({"_id": user['_id']}, {"$set": {"factory_id": None}})
        return jsonify({"ok": True, "message": "Factory deleted successfully"}), 200
    except Exception as e:
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500


"""
Entity CRUD operations for admin
"""

@bp.route('/entities', methods=['POST'])
@jwt_required()
def create_entity():
    try:
        data = request.get_json()
        if not data or not data.get('name') or not data.get('factory_id'):
            return jsonify({"ok": False, "message": "Missing data"}), 400

        is_admin, response = is_admin_user()
        if not is_admin:
            return response
        factory = mongo.db.factories.find_one({"_id": ObjectId(data['factory_id'])})
        if not factory:
            return jsonify({"ok": False, "message": "Factory not found"}), 404
        entity = Entity(name=data['name'], factory_id=data['factory_id'])
        mongo.db.entities.insert_one(entity.to_dict())
        return jsonify({"ok": True, "message": "Entity created successfully"}), 201
    except Exception as e:
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500


@bp.route('/entities', methods=['GET'])
@jwt_required()
def get_entities():
    try:
        is_admin, response = is_admin_user()
        if not is_admin:
            return response
        
        page, per_page = get_pagination_params()
        filter = {}
        query = mongo.db.entities.find(filter)
        pagination = paginate(query, filter, page, per_page)

        result = []
        for entity in pagination['items']:
            factory = mongo.db.factories.find_one({"_id": entity['factory_id']})
            if factory:
                result.append({"name": entity['name'], "factory": factory["name"]})
        return jsonify({"ok": True, "data": result, "pagination": {
            "total": pagination['total'],
            "page": pagination['page'],
            "per_page": pagination['per_page']
        }}), 200
    except Exception as e:
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500



@bp.route('/entities/<entity_id>', methods=['GET'])
@jwt_required()
def get_entity(entity_id):
    try:
        is_admin, response = is_admin_user()
        if not is_admin:
            return response
        entity = mongo.db.entities.find_one({"_id": ObjectId(entity_id)})
        if not entity:
            return jsonify({"ok": False, "message": "Entity not found"}), 404

        factory = mongo.db.factories.find_one({"_id": entity['factory_id']})
        return jsonify({"name": entity['name'], "factory": factory['name']}), 200
    except Exception as e:
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500


@bp.route('/entities/<entity_id>', methods=['PUT'])
@jwt_required()
def update_entity(entity_id):
    try:
        data = request.get_json()
        is_admin, response = is_admin_user()
        if not is_admin:
            return response
        entity = mongo.db.entities.find_one({"_id": ObjectId(entity_id)})
        if not entity:
            return jsonify({"ok": False, "message": "Entity not found"}), 404
        if 'factory_id' in data:
            try:
                data['factory_id'] = ObjectId(data['factory_id'])
            except:
                return jsonify({"ok": False, "message": "Invalid factory_id format"}), 400
        mongo.db.entities.update_one({"_id": ObjectId(entity_id)}, {"$set": data})
        return jsonify({"ok": True, "message": "Entity updated successfully"}), 200
    except Exception as e:
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500


@bp.route('/entities/<entity_id>', methods=['DELETE'])
@jwt_required()
def delete_entity(entity_id):
    try:
        is_admin, response = is_admin_user()
        if not is_admin:
            return response
        entity = mongo.db.entities.find_one({"_id": ObjectId(entity_id)})
        if not entity:
            return jsonify({"ok": False, "message": "Entity not found"}), 404
        mongo.db.entities.delete_one({"_id": ObjectId(entity_id)})
        return jsonify({"ok": True, "message": "Entity deleted successfully"}), 200
    except Exception as e:
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500


"""
User CRUD operations for admin
"""

@bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    try:
        is_admin, response = is_admin_user()
        if not is_admin:
            return response
        
        page, per_page = get_pagination_params()
        filter = {}
        query = mongo.db.users.find(filter)
        pagination = paginate(query, filter, page, per_page)

        result = []
        for user in pagination['items']:
            factory = mongo.db.factories.find_one({"_id": user.get('factory_id')})
            result.append({
                "username": user['username'],
                "is_admin": user.get('is_admin', False),
                "factory": factory["name"] if factory else None
            })
        return jsonify({"ok": True, "data": result, "pagination": {
            "total": pagination['total'],
            "page": pagination['page'],
            "per_page": pagination['per_page']
        }}), 200
    except Exception as e:
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500



@bp.route('/users/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    try:
        is_admin, response = is_admin_user()
        if not is_admin:
            return response
        
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"ok": False, "message": "User not found"}), 404
        factory = mongo.db.factories.find_one({"_id": user.get('factory_id')})
        return jsonify({
            "ok": True,
            "username": user['username'],
            "is_admin": user.get('is_admin', False),
            "factory": factory["name"] if factory else None
        }), 200
    except Exception as e:
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500


@bp.route('/users/<user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    try:
        data = request.get_json()
        is_admin, response = is_admin_user()
        if not is_admin:
            return response
        
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"ok": False, "message": "User not found"}), 404

        if 'factory_id' in data:
            try:
                data['factory_id'] = ObjectId(data['factory_id'])
            except:
                return jsonify({"ok": False, "message": "Invalid factory_id format"}), 400

        mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": data})
        return jsonify({"ok": True, "message": "User updated successfully"}), 200
    except Exception as e:
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500


@bp.route('/users/<user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    try:
        is_admin, response = is_admin_user()
        if not is_admin:
            return response
        
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"ok": False, "message": "User not found"}), 404
        mongo.db.users.delete_one({"_id": ObjectId(user_id)})
        return jsonify({"ok": True, "message": "User deleted successfully"}), 200
    except Exception as e:
        return jsonify({"ok": False, "message": "An error occurred: " + str(e)}), 500



