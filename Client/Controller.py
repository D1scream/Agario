import pygame


class Keyset():
    def __init__(self, key_up , key_down, key_left, key_right, key_division):
        self.action_up_ = key_up
        self.action_down_ = key_down
        self.action_left_ = key_left
        self.action_right_ = key_right
        self.action_division_ = key_division

class Controller:
    def __init__(self, keyset : Keyset):
        self.keyset_ = keyset

    def get_moving_vector(self,keys):
        direction = pygame.math.Vector2(0, 0)

        if keys[self.keyset_.action_up_]: direction.y = -1
        if keys[self.keyset_.action_down_]: direction.y = 1
        if keys[self.keyset_.action_left_]: direction.x = -1
        if keys[self.keyset_.action_right_]: direction.x = 1

        return direction
    
    def get_division(self, keys):
        return keys[self.keyset_.action_division_]