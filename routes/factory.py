from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import mongo
from models.factory import Factory

bp = Blueprint('factory', __name__, url_prefix='/factories')

@bp.route('/', methods=['POST'])
def create_factory():
    data = request.get_json()
    factory = Factory(name=data['name'], location=data['location'], capacity=data['capacity'])
    mongo.db.factories.insert_one(factory.to_dict())
    return jsonify({"message": "Factory created successfully"}), 201

@bp.route('/', methods=['GET'])
@jwt_required()
def get_factories():
    factories = mongo.db.factories.find()
    result = []
    for factory in factories:
        result.append({"name": factory['name'], "location": factory['location'], "capacity": factory['capacity']})
    return jsonify(result)
