from flask import Flask
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

mongo = PyMongo(app)
jwt = JWTManager(app)

def create_app():
    from routes.auth import bp as auth_bp
    from routes.factory import bp as factory_bp
    from routes.entity import bp as entity_bp
    from routes.admin import bp as admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(factory_bp)
    app.register_blueprint(entity_bp)
    app.register_blueprint(admin_bp)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)