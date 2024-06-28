from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from app import mongo
from models.user import User
from bson import ObjectId

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user. This endpoint requires a username, password, and factory_id.
    """
    try:
        data = request.get_json()

        # Check if the request data contains username, password, and factory_id
        if not data or not data.get('username') or not data.get('password') or not data.get('factory_id'):
            return jsonify({"ok":False,
                            "message": "Missing data"}), 400
        
        # Check if the user already exists
        existing_user = mongo.db.users.find_one({"username": data['username']})
        if existing_user:
            return jsonify({"ok":False,      
                            "message": "User already exists"}), 400
        
        # Convert factory_id to ObjectId and check if the factory exists
        factory = mongo.db.factories.find_one({"_id": ObjectId(data['factory_id'])})
        if not factory:
            return jsonify({"ok":False,
                            "message": "Factory not found"}), 404

        # Hash the password and create a new user
        user = User(username=data['username'], password=data['password'], factory_id=data['factory_id'])
        mongo.db.users.insert_one(user.to_dict())
        return jsonify({"ok":True,
                        "message": "User registered successfully"}), 201
    
    except Exception as e:
        return jsonify({"ok":False,
                        "message": "An error occurred: " + str(e)}), 500

@bp.route('/adminregister', methods=['POST'])
def adminregister():
    """
    Register a new admin user. This endpoint requires a username and password.
    """
    try:
        data = request.get_json()

        # Check if the request data contains username and password
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({"ok":False,
                            "message": "Missing data"}), 400

        # Check if the user already exists
        existing_user = mongo.db.users.find_one({"username": data['username']})
        if existing_user:
            return jsonify({"ok":False,
                            "message": "User already exists"}), 400

        # Hash the password and create a new admin user
        user = User(username=data['username'], password=data['password'], factory_id=None, is_admin=True)
        mongo.db.users.insert_one(user.to_dict())

        return jsonify({"ok":True,
                        "message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"ok":False,
                        "message": "An error occurred: " + str(e)}), 500

@bp.route('/login', methods=['POST'])
def login():
    """
    Log in a user. This endpoint requires a username and password.
    """
    try:
        data = request.get_json()

        # Check if the request data contains username and password
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({"ok":False,
                            "message": "Missing data"}), 400

        # Find the user in the database
        user_data = mongo.db.users.find_one({"username": data['username']})

        # Check if the user exists and the password is correct
        if user_data and check_password_hash(user_data['password_hash'], data['password']):
            access_token = create_access_token(identity=data['username'])

            return jsonify({"ok":True, 
                            "access_token": access_token}), 200
        
        return jsonify({"ok":False,
                        "message": "Invalid credentials"}), 401
    
    except Exception as e:
        return jsonify({"ok":False,
                        "message": "An error occurred: " + str(e)}), 500


