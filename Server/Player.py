import math
import pygame

from GlobalConstants import FIELD_WIDTH, FIELD_HEIGHT, MASS_FOR_EAT_PLAYER
class Unit:
    def __init__(self, nickname, color, id):
        self.direction_ = pygame.math.Vector2(0, 0)
        self.collision_active_timer_ = 1
        self.division_ban_timer_ = 0.01
        self.nickname = nickname
        self.pos_ = pygame.math.Vector2(FIELD_WIDTH // 2, FIELD_HEIGHT // 2)
        self.score = 1000
        self.color_ = color
        self.acceleration = 1
        self.id_ = id
        self.division_flag = False

    def speed(self):
        return 20 / math.log(self.score) * self.acceleration
    
    def radius(self):
        return math.sqrt(self.score)

    def move(self):
        direction = self.direction_
        if direction.length() > 0:
            direction = direction.normalize() * self.speed() 

        self.pos_ += direction
        
    def division(self, player_list):
        if self.score < 400 or self.division_ban_timer_!=0:
            return  
        part = Unit(self.nickname, self.color_, id = self.id_)
        
        part.score = self.score / 2
        self.score = self.score / 2
        direction = self.direction_
        if direction.length() == 0:
            direction = pygame.math.Vector2(1,1).normalize()

        part.pos_ = self.pos_ + direction * (self.radius() + part.radius() + 10)
 
        part.acceleration = 3  
        part.division_ban_timer_ = 1
        self.division_ban_timer_ = 1
        self.collision_active_timer_=1100000
        player_list.append(part)
        return part
    

    def check_player_eat(self, player):
        mass_to_eat = MASS_FOR_EAT_PLAYER
        if(player != self and player.id_==self.id_):
            mass_to_eat = 1
        if(self.score * mass_to_eat > player.score ):
            distance = ((self.pos_.x - player.pos_.x)**2 + (self.pos_.y - player.pos_.y)**2)**0.5
            if(distance < self.radius()*0.8):
                return True
        return False
                
            
    def __str__(self):
        return self.nickname
    
    @property
    def __dict__(self):
        return {
            "direction_x": self.direction_.x,
            "direction_y": self.direction_.y,
            "collision_active_timer": self.collision_active_timer_,
            "division_ban_timer": self.division_ban_timer_,
            "nickname": self.nickname,
            "pos_x": self.pos_.x,
            "pos_y": self.pos_.y,
            "score": self.score,
            "color": list(self.color_),
            "acceleration": self.acceleration,
            "id": self.id_
        }
    
    def load_data(self, direction, division):
        self.direction_ = pygame.math.Vector2(direction[0],direction[1])
        if(not self.division_flag):
            self.division_flag = division

    def update(self):
        self.acceleration = max(self.acceleration - (1 / 10), 1)
        self.collision_active_timer_ = max(0,self.collision_active_timer_ - (1/60))
        self.division_ban_timer_ = max(0,self.division_ban_timer_ - (1/60))
        self.move()
        