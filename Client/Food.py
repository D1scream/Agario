import math
import random
import pygame


class Food:
    def __init__(self, x: float = 1, y: float = 1, score: float = 5, color: tuple = (0,5,10)):
        self.x = x
        self.y = y
        self.score = score
        self.color = color
    
    def draw(self,screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.get_radius())
    
    def get_radius(self):
        return math.sqrt(self.score)*1.7