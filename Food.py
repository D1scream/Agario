import json
import random
from Player import Unit
from GlobalConstants import WIDTH, HEIGHT
class Food:
    def __init__(self):
        self.x_ = random.randint(10, WIDTH - 10)
        self.y_ = random.randint(10, HEIGHT - 10)
        self.radius_ = 5
        self.color_ = (255, 0, 0)
    
    def check_eated(self, player : Unit):
        if (self.x_ - player.pos_.x) ** 2 + (self.y_ - player.pos_.y) ** 2 < (self.radius_ + player.radius()*0.9) ** 2:
            player.score+=50
            return True
        return False

    @property
    def __dict__(self):
        return {
            "x": self.x_,
            "y": self.y_,
            "radius": self.radius_,
            "color": list(self.color_)
        }
    def get_json(self):
        return json.dumps(self.__dict__)