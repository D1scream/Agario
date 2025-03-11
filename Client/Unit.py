import math
import pygame



class Unit:
        def __init__(self, nickname: str, color: tuple, 
                     pos_x, pos_y, direction_x, direction_y, 
                     score, acceleration, collision_active_timer, division_ban_timer,
                     id):
            self.collision_active_timer = collision_active_timer
            self.division_ban_timer = division_ban_timer
            self.nickname = nickname
            self.pos = pygame.math.Vector2(pos_x, pos_y)
            self.direction = pygame.math.Vector2(direction_x, direction_y)
            self.score = score
            self.color = color
            self.acceleration = acceleration
            self.id = id

        def speed(self):
            return 20 / math.log(self.score) * self.acceleration
        
        def get_radius(self):
            return math.sqrt(self.score)

        def speed(self):
            return 20 / math.log(self.score) * self.acceleration

        async def move(self):
            direction = self.direction

            if direction.length() > 0:
                direction = direction.normalize() * self.speed() *self.acceleration
            self.pos += direction

        def draw(self,screen):
            pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), self.get_radius())
            font = pygame.font.Font(None, int(self.get_radius() * 4 / len(self.nickname))) 
            text_surface = font.render(self.nickname, True, (255, 255, 255))  
            text_rect = text_surface.get_rect(center=(int(self.pos.x), int(self.pos.y)))
            
            screen.blit(text_surface, text_rect)
        
        async def update(self):
            self.acceleration = max(self.acceleration - (1 / 10), 1)