from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app import mongo

def is_admin_user():
    username = get_jwt_identity()
    user = mongo.db.users.find_one({"username": username})
    if not user:
        return False, jsonify({"ok": False, "message": "User not found"}), 404
    if not user.get('is_admin'):
        return False, jsonify({"ok": False, "message": "Not Auth"}), 401
    return True, user
