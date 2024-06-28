from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app import mongo

def is_auth_for_factory(factory_id):
    username = get_jwt_identity()
    user = mongo.db.users.find_one({"username": username})
    if not user:
        return False, jsonify({"ok": False, "message": "User not found"}), 404
    user_factory_id = user.get('factory_id')
    if not user_factory_id or str(user_factory_id) != str(factory_id):
        return False, jsonify({"ok": False, "message": "Not Auth"}), 401
    return True, user