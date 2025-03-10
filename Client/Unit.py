import math
import pygame

from GlobalConstants import score_to_speed


class Unit:
        def __init__(self, nickname: str, color: tuple, 
                     pos_x, pos_y, direction_x, direction_y, 
                     score, acceleration, collision_active_timer, division_ban_timer,
                     id):
            self.collision_active_timer_ = collision_active_timer
            self.division_ban_timer_ = division_ban_timer
            self.nickname = nickname
            self.pos_ = pygame.math.Vector2(pos_x, pos_y)
            self.direction_ = pygame.math.Vector2(direction_x, direction_y)
            self.score = score
            self.color_ = color
            self.acceleration = acceleration
            self.id_ = id

        def speed(self):
            return 20 / math.log(self.score) * self.acceleration
        
        def radius(self):
            return math.sqrt(self.score)

        async def move(self):
            direction = self.direction_

            if direction.length() > 0:
                direction = direction.normalize() * score_to_speed() *self.acceleration
            self.pos_ += direction

        def draw(self,screen):
            pygame.draw.circle(screen, self.color_, (int(self.pos_.x), int(self.pos_.y)), self.radius())
            font = pygame.font.Font(None, int(self.radius()*4/len(self.nickname))) 
            text_surface = font.render(self.nickname, True, (255, 255, 255))  
            text_rect = text_surface.get_rect(center=(int(self.pos_.x), int(self.pos_.y)))
            
            screen.blit(text_surface, text_rect)
        
        async def update(self):
            self.acceleration = max(self.acceleration - (1 / 10), 1)
            self.collision_active_timer_ = max(0,self.collision_active_timer_ - (1/60))
            self.division_ban_timer_ = max(0,self.division_ban_timer_ - (1/60))