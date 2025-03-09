import json
from GlobalConstants import HEIGHT, WIDTH
from Player import Player
from Food import Food
class FoodListModel:
    def __init__(self, food_list: list[Food]):
        self.food_list_ = food_list

    def to_json(self):
        return json.dumps([food.__dict__ for food in self.food_list_])

    @classmethod
    def from_json(cls, json_str: str, food_class):
        data = json.loads(json_str)
        foods = []
        for food_data in data:
            foods.append(food_class(**food_data))
        return cls(foods)

class PlayersListModel:
    def __init__(self, players_list: list[Player]):
        self.players_list_ = players_list

    def to_json(self):
        return json.dumps([player.__dict__ for player in self.players_list_])

    @classmethod
    def from_json(cls, json_str: str, player_class):
        data = json.loads(json_str)
        players = []
        for player_data in data:
            players.append(player_class(**player_data))
        return cls(players)