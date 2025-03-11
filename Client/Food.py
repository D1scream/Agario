import math
import random
import pygame


class Food:
    def __init__(self, x: float = 1, y: float = 1, score: float = 5, color: tuple = (0,5,10)):
        self.x_ = x
        self.y_ = y
        self.score_ = score
        self.color_ = color
    
    def draw(self,screen):
        pygame.draw.circle(screen, self.color_, (self.x_, self.y_), self.get_radius())
    
    def get_radius(self):
        return math.sqrt(self.score_)*1.7