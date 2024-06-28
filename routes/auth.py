from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from app import mongo
from models.user import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password') or not data.get('factory_id'):
        return jsonify({"ok":False,
                        "message": "Missing data"}), 400

    existing_user = mongo.db.users.find_one({"username": data['username']})
    if existing_user:
        return jsonify({"ok":False,
                        "message": "User already exists"}), 400
    factory = mongo.db.factories.find_one({"_id": data['factory_id']})
    if not factory:
        return jsonify({"ok":False,
                        "message": "Factory not found"}), 404

    hashed_password = generate_password_hash(data['password'])
    user = User(username=data['username'], password=data['password'], factory_id=data['factory_id'])
    mongo.db.users.insert_one(user.to_dict())
    return jsonify({"ok":True,
                    "message": "User registered successfully"}), 201

@bp.route('/adminregister', methods=['POST'])
def adminregister():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"ok":False,
                        "message": "Missing data"}), 400

    existing_user = mongo.db.users.find_one({"username": data['username']})
    if existing_user:
        return jsonify({"ok":False,
                        "message": "User already exists"}), 400

    hashed_password = generate_password_hash(data['password'])
    user = User(username=data['username'], password=data['password'], factory_id=None, is_admin=True)
    mongo.db.users.insert_one(user.to_dict())
    return jsonify({"ok":True,
                    "message": "User registered successfully"}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"ok":False,
                        "message": "Missing data"}), 400

    user_data = mongo.db.users.find_one({"username": data['username']})
    if user_data and check_password_hash(user_data['password_hash'], data['password']):
        access_token = create_access_token(identity=data['username'], expires_delta=timedelta(minutes=70000000))

        return jsonify({"ok":True, 
                        "access_token": access_token}), 200
    return jsonify({"ok":False,
                    "message": "Invalid credentials"}), 401


