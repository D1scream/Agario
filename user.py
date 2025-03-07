import json

class User:
    def __init__(self, nickname):
        self.nickname=nickname
        self.connection = None

    def serialize(self):
        return json.dumps({"nickname": self.nickname})

    @classmethod
    def deserialize(cls, json_data: str):
        data = json.loads(json_data)
        return cls(nickname=data["nickname"])