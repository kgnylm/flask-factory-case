from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

class User:
    def __init__(self, username, password, factory_id):
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.factory_id = ObjectId(factory_id) 

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'username': self.username,
            'password_hash': self.password_hash,
            'factory_id': self.factory_id
        }
