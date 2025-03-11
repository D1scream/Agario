import math
import pygame

from GlobalConstants import FIELD_WIDTH, FIELD_HEIGHT, MASS_FOR_EAT_PLAYER
class Unit:
    def __init__(self, nickname, color, id):
        self.direction = pygame.math.Vector2(0, 0)
        self.collision_active_timer = 1
        self.division_ban_timer = 0.01
        self.nickname = nickname
        self.pos = pygame.math.Vector2(FIELD_WIDTH // 2, FIELD_HEIGHT // 2)
        self.score = 1000
        self.color = color
        self.acceleration = 1
        self.id = id
        self.division_flag = False

    def get_speed(self):
        return 20 / math.log(self.score) * self.acceleration
    
    def get_radius(self):
        return math.sqrt(self.score)

    def move(self):
        direction = self.direction
        if direction.length() > 0:
            direction = direction.normalize() * self.get_speed() 

        self.pos += direction
        
    def division(self, player_list):
        if self.score < 400 or self.division_ban_timer!=0:
            return  
        
        part = Unit(self.nickname, self.color, id=self.id)
        
        part.score = self.score / 2
        self.score = self.score / 2
        direction = self.direction
        if direction.length() == 0:
            direction = pygame.math.Vector2(1, 1).normalize()

        part.pos = self.pos + direction * (self.get_radius() + part.get_radius() + 10)
 
        part.acceleration = 3  
        part.division_ban_timer = 1
        self.division_ban_timer = 1
        self.collision_active_timer = 1100000
        player_list.append(part)
        return part
    
    def check_player_eat(self, player: 'Unit'):
        score_to_eat = MASS_FOR_EAT_PLAYER
        if(player != self and player.id==self.id):
            score_to_eat = 1
        if(self.score * score_to_eat > player.score ):
            distance = ((self.pos.x - player.pos.x)**2 + (self.pos.y - player.pos.y)**2)**0.5
            if(distance < self.get_radius()*0.8):
                return True
        return False
            
    def __str__(self):
        return self.nickname
    
    @property
    def __dict__(self):
        return {
            "direction_x": self.direction.x,
            "direction_y": self.direction.y,
            "collision_active_timer": self.collision_active_timer,
            "division_ban_timer": self.division_ban_timer,
            "nickname": self.nickname,
            "pos_x": self.pos.x,
            "pos_y": self.pos.y,
            "score": self.score,
            "color": list(self.color),
            "acceleration": self.acceleration,
            "id": self.id
        }
    
    def load_data(self, direction, division):
        self.direction = pygame.math.Vector2(direction[0], direction[1])
        if(not self.division_flag):
            self.division_flag = division

    def update(self):
        self.acceleration = max(self.acceleration - (1 / 10), 1)
        self.collision_active_timer = max(0, self.collision_active_timer - (1/60))
        self.division_ban_timer = max(0, self.division_ban_timer - (1/60))
        self.move()
        