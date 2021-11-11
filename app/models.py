
class Event:
    def __init__(self, **kwargs):
        self.id  = kwargs.get('id')
        self.name = kwargs.get('name')
