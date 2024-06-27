from bson import ObjectId

class Entity:
    def __init__(self, name, factory_id):
        self.name = name
        self.factory_id = ObjectId(factory_id)  # Factory ID'yi ObjectId olarak sakla

    def to_dict(self):
        return {
            'name': self.name,
            'factory_id': self.factory_id
        }

