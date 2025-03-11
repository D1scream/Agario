import json
from GlobalConstants import FIELD_HEIGHT, FIELD_WIDTH
from Server.Player import Unit
from Server.Food import Food
class FoodListModel:
    def __init__(self, food_list: list[Food]):
        self.food_list = food_list

    def to_json(self):
        return json.dumps([food.__dict__ for food in self.food_list])

    @classmethod
    def from_json(cls, json_str: str, food_class):
        data = json.loads(json_str)
        foods = []
        for food_data in data:
            foods.append(food_class(**food_data))
        return cls(foods)

class PlayersListModel:
    def __init__(self, players_list: list[Unit]):
        self.players_list = players_list

    def to_json(self):
        return json.dumps([player.__dict__ for player in self.players_list])

    @classmethod
    def from_json(cls, json_str: str, player_class):
        data = json.loads(json_str)
        players = []
        for player_data in data:
            players.append(player_class(**player_data))
        return cls(players)
    
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