class Factory:
    def __init__(self, name, location, capacity):
        self.name = name
        self.location = location
        self.capacity = capacity

    def to_dict(self):
        return {
            'name': self.name,
            'location': self.location,
            'capacity': self.capacity
        }
