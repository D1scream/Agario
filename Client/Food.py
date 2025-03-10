import pygame

from Client.ControlledUnit import Controlled_Unit


class Food:
    def __init__(self, x: float = 1, y: float = 1, radius: float = 5, color: tuple = (0,5,10)):
        self.x_ = x
        self.y_ = y
        self.radius_ = radius
        self.color_ = color
    
    def draw(self,screen):
        pygame.draw.circle(screen, self.color_, (self.x_, self.y_), self.radius_)
    
    def check_eated(self, player : Controlled_Unit):
        if (self.x_ - player.pos_.x) ** 2 + (self.y_ - player.pos_.y) ** 2 < (self.radius_ + player.radius()*0.9) ** 2:
            player.score+=50
            return True
        return False