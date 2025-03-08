import numpy as np
import pygame
import random
import math

WIDTH, HEIGHT = 1280, 720

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ChunChunMaru")
clock = pygame.time.Clock()
MASS_FOR_EAT_PLAYER = 0.8
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

    def set_keyset(self, keyset : Keyset):
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

class Player:
    def __init__(self, controller, nickname, color):
        self.parts = []
        self.collision_active_timer_ = 0
        self.nickname = nickname
        self.controller_ = controller
        self.pos_ = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)
        self.radius_ = 20
        self.color_ = color
        self.acceleration = 1

    def speed(self):
        print(math.log(self.radius_**2))
        return 30 / math.log(self.radius_**2) * self.acceleration

    def move(self):
        
        keys = pygame.key.get_pressed()
        direction = self.controller_.get_moving_vector(keys)

        if direction.length() > 0:
            direction = direction.normalize() * self.speed()

        self.pos_ += direction
    
    def division(self, player_list):
        if self.radius_ < 20 or self.divide_ban!=0:
            return  

        part = Player(self.controller_, self.nickname, self.color_)
        
        part.radius_ = math.sqrt(self.radius_ ** 2 / 2)
        self.radius_ = math.sqrt(self.radius_ ** 2 / 2)

        keys = pygame.key.get_pressed()
        direction = self.controller_.get_moving_vector(keys)

        if direction.length() == 0:
            direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()

        part.pos_ = self.pos_ + direction * (self.radius_ + part.radius_ + 5)

        part.acceleration = 3  

        self.parts.append(part)
        part.parts.append(self)

        self.collision_active_timer_=1100000
        player_list.append(part)

    def draw(self):
        pygame.draw.circle(screen, self.color_, (int(self.pos_.x), int(self.pos_.y)), self.radius_)
    
    def check_food(self,food_list):
        for food in food_list:
            if(food.check_eated(self)):
                food_list.remove(food)
                food_list.append(Food())
            food.draw()

    def check_player_eat(self, player_list):
        for player in player_list:
            if(self.radius_** 2 * MASS_FOR_EAT_PLAYER > player.radius_ ** 2):
                distance = ((self.pos_.x - player.pos_.x)**2 + (self.pos_.y - player.pos_.y)**2)**0.5
                if(distance < self.radius_*0.8):
                    player.eated(self,player_list)

    def check_division(self, player_list):
        keys = pygame.key.get_pressed()
        if(self.controller_.get_division(keys = keys)):
            self.division(player_list)

    def check_collision(self):
        if(self.collision_active_timer_!=0):
            for part in self.parts:
                distance = ((self.pos_.x - part.pos_.x)**2 + (self.pos_.y - part.pos_.y)**2)**0.5
                if(distance<=self.radius_+part.radius_):
                    return True
                return False

    def resolve_collision(self, other_circle):
        # Вектор от центра одного круга к другому
        normal = other_circle.pos - self.pos
        normal_length = normal.length()

        # Нормализуем вектор нормали
        normal.normalize_ip()

        # Отражение скорости вдоль нормали
        relative_velocity = self.speed - other_circle.speed
        speed_along_normal = relative_velocity.dot(normal)

        # Если скорость вдоль нормали отрицательная (круги приближаются), выполняем отражение
        if speed_along_normal < 0:
            return

        # Массируем момент столкновения
        restitution = 1  # Коэффициент восстановления (1 — идеальный отскок)
            # Скорости отражаются относительно нормали
        impulse = 2 * speed_along_normal / (self.radius + other_circle.radius)
        self.speed -= impulse * other_circle.radius * normal
        other_circle.speed += impulse * self.radius * normal

    def eated(self, player, player_list):
        print(f"Dead by {player}" )
        player.radius_ += self.radius_**0.5
        player_list.remove(self)

    def __str__(self):
        return self.nickname
    
    def update(self):
        self.acceleration = max(self.acceleration - (1 / 10), 1)
        self.collision_active_timer_ = max(0,self.collision_active_timer_ - (1/60))
        self.move()
        self.draw()

class Food:
    def __init__(self):
        self.x_ = random.randint(10, WIDTH - 10)
        self.y_ = random.randint(10, HEIGHT - 10)
        self.radius_ = 5
        self.color_ = (255, 0, 0)
    
    def draw(self):
        pygame.draw.circle(screen, self.color_, (self.x_, self.y_), self.radius_)
    
    def check_eated(self, player : Player):
        if (self.x_ - player.pos_.x) ** 2 + (self.y_ - player.pos_.y) ** 2 < (self.radius_ + player.radius_*0.9) ** 2:
            player.radius_+=0.5
            return True
        return False
    
    def update(self):
        self.draw()

class Field:
    def __init__(self, WIDTH, HEIGHT, FOOD_COUNT = 50):
        self.WIDTH_=WIDTH
        self.HEIGHT_=HEIGHT

        self.players_list = []
        self.food_list = [Food() for _ in range(FOOD_COUNT)]
        
    def update(self):
        field.players_list.sort(key=lambda player: player.radius_)
        for player in self.players_list:
            self.check_boundaries(player)
            player.check_food(self.food_list)
            player.check_player_eat(self.players_list)
            player.check_division(self.players_list)
            player.update()
        
    def check_boundaries(self, player):
        player.pos_.x = max(player.radius_, min(self.WIDTH_ - player.radius_, player.pos_.x))
        player.pos_.y = max(player.radius_, min(self.HEIGHT_ - player.radius_, player.pos_.y))

def CreateField():
    field = Field(WIDTH,HEIGHT)
    player_wasd_keyset = Keyset(
        key_up = pygame.K_w,
        key_down = pygame.K_s,
        key_left = pygame.K_a,
        key_right = pygame.K_d,
        key_division = pygame.K_SPACE
        )
    
    player_arrows_keyset = Keyset(
        key_up = pygame.K_UP,
        key_down = pygame.K_DOWN,
        key_left = pygame.K_LEFT,
        key_right = pygame.K_RIGHT,
        key_division = pygame.K_RSHIFT
        )
    
    controllerWASD = Controller(player_wasd_keyset)
    controllerARROWS = Controller(player_arrows_keyset)
    player1 = Player(controller = controllerWASD, nickname="PLayerWASD", color = (0, 0, 255))
    player2 = Player(controller = controllerARROWS, nickname="PLayerARROWS", color = (0, 128, 128))

    player2.pos_.x += 100
    player2.pos_.y += 100

    field.players_list.append(player1)
    field.players_list.append(player2)
    return field

if __name__ == "__main__":
    # for i in map(lambda x: x/10.0, range(10, 200, 1)):  
    #     l = []
    #     for j in map(lambda x: x/10.0, range(10, 200, 1)):
    #         if (i ** 2 * MASS_FOR_EAT_PLAYER > j ** 2):
    #             l.append((i, j))
    #     if len(l) > 1:
    #         print(l[0], l[-1])
    #     l.clear()
    # exit()
    
    field = CreateField()
    running = True
    while running:
        
        if(len(field.players_list)==1):
            field = CreateField()
        screen.fill((255, 255, 255))

        field.update()
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        clock.tick(60)

    pygame.quit()
