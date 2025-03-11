import math
import pygame



class Unit:
        def __init__(self, nickname: str, color: tuple, 
                     pos_x, pos_y, direction_x, direction_y, 
                     score, acceleration, collision_active_timer, division_ban_timer,
                     id):
            self.collision_active_timer_ = collision_active_timer
            self.division_ban_timer_ = division_ban_timer
            self.nickname_ = nickname
            self.pos_ = pygame.math.Vector2(pos_x, pos_y)
            self.direction_ = pygame.math.Vector2(direction_x, direction_y)
            self.score_ = score
            self.color_ = color
            self.acceleration_ = acceleration
            self.id_ = id

        def speed(self):
            return 20 / math.log(self.score_) * self.acceleration_
        
        def get_radius(self):
            return math.sqrt(self.score_)

        def speed(self):
            return 20 / math.log(self.score_) * self.acceleration_

        async def move(self):
            direction = self.direction_

            if direction.length() > 0:
                direction = direction.normalize() * self.speed() *self.acceleration_
            self.pos_ += direction

        def draw(self,screen):
            pygame.draw.circle(screen, self.color_, (int(self.pos_.x), int(self.pos_.y)), self.get_radius())
            font = pygame.font.Font(None, int(self.get_radius()*4/len(self.nickname_))) 
            text_surface = font.render(self.nickname_, True, (255, 255, 255))  
            text_rect = text_surface.get_rect(center=(int(self.pos_.x), int(self.pos_.y)))
            
            screen.blit(text_surface, text_rect)
        
        async def update(self):
            self.acceleration_ = max(self.acceleration_ - (1 / 10), 1)
            self.collision_active_timer_ = max(0,self.collision_active_timer_ - (1/60))
            self.division_ban_timer_ = max(0,self.division_ban_timer_ - (1/60))