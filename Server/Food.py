import json
import math
import random
from GlobalConstants import FIELD_WIDTH, FIELD_HEIGHT, generate_random_color
class Food:
    def __init__(self):
        self.x_ = random.randint(10, FIELD_WIDTH - 10)
        self.y_ = random.randint(10, FIELD_HEIGHT - 10)
        self.score_ = random.randint(10,15)

        self.color_ = generate_random_color(min_sum=200,max_sum=600)
    
    @property
    def __dict__(self):
        return {
            "x": self.x_,
            "y": self.y_,
            "score": self.score_,
            "color": list(self.color_)
        }
    def get_json(self):
        return json.dumps(self.__dict__)