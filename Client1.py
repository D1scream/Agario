# import asyncio
# from WebSocketClient import WebSocketClient

# client = WebSocketClient("ws://localhost:8765",nickname="second")
# asyncio.run(client.main())
# print("Client One started")


import pygame
import random
import math

WIDTH, HEIGHT = 1280, 720

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ChunChunMaru Client 1")
clock = pygame.time.Clock()
#MASS_FOR_EAT_PLAYER = 0.8
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
        self.collision_active_timer_ = 1
        self.division_ban_timer_ = 0.01
        self.nickname = nickname
        self.controller_ = controller
        self.pos_ = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)
        self.score = 1000
        self.color_ = color
        self.acceleration = 1

    def speed(self):
        return 20 / math.log(self.score) * self.acceleration
    
    def radius(self):
        return math.sqrt(self.score)

    def move(self):
        keys = pygame.key.get_pressed()
        direction = self.controller_.get_moving_vector(keys)

        if direction.length() > 0:
            direction = direction.normalize() * self.speed() 
        #send to websocket direction
        self.pos_ += direction

    def division(self):
        if self.score < 400 or self.division_ban_timer_!=0:
            return  

        part = Player(self.controller_, self.nickname, self.color_)
        
        part.score = self.score / 2
        self.score = self.score / 2

        keys = pygame.key.get_pressed()
        direction = self.controller_.get_moving_vector(keys)

        if direction.length() == 0:
            direction = pygame.math.Vector2(1,1).normalize()

        part.pos_ = self.pos_ + direction * (self.radius() + part.radius() + 10)
 
        part.acceleration = 3  
        part.division_ban_timer_ = 0.1
        self.division_ban_timer_ = 0.1
        self.collision_active_timer_=1100000
        return part

    def draw(self):
        pygame.draw.circle(screen, self.color_, (int(self.pos_.x), int(self.pos_.y)), self.radius())
    
    def check_food(self,food_list):
        for food in food_list:
            if(food.check_eated(self)):
                food_list.remove(food)
                #Добавить на сервере
                #food_list.append(Food())
            food.draw()

    # def check_player_eat(self, player_list):
    #     for player in player_list:
    #         mass_to_eat = MASS_FOR_EAT_PLAYER
    #         if(player != self and player.nickname==self.nickname):
    #             mass_to_eat = 1
    #         if(self.score * mass_to_eat > player.score ):
    #             distance = ((self.pos_.x - player.pos_.x)**2 + (self.pos_.y - player.pos_.y)**2)**0.5
    #             if(distance < self.radius()*0.8):
    #                 print(f"Dead by {self}" )
    #                 self.score += player.score
    #                 player_list.remove(player)
            

    def check_division(self, player_list):
        keys = pygame.key.get_pressed()
        if(self.controller_.get_division(keys = keys)):
            #Send_message
            new_part = self.division()
            if(new_part):
                player_list.append(new_part)

    def __str__(self):
        return self.nickname
    
    def update(self):
        #Вот тут пиздец 
        self.acceleration = max(self.acceleration - (1 / 10), 1)
        self.collision_active_timer_ = max(0,self.collision_active_timer_ - (1/60))
        self.division_ban_timer_ = max(0,self.division_ban_timer_ - (1/60))
        self.move()
        self.draw()

class Food:
    def __init__(self,x,y):
        self.x_ = x
        self.y_ = y
        self.radius_ = 5
        self.color_ = (255, 0, 0)
    
    def draw(self):
        pygame.draw.circle(screen, self.color_, (self.x_, self.y_), self.radius_)
    
    def check_eated(self, player : Player):
        if (self.x_ - player.pos_.x) ** 2 + (self.y_ - player.pos_.y) ** 2 < (self.radius_ + player.radius()*0.9) ** 2:
            player.score+=50
            return True
        return False

class Field:
    def __init__(self, WIDTH, HEIGHT):
        self.WIDTH_=WIDTH
        self.HEIGHT_=HEIGHT
        #Получить данные из вебсокета
        self.players_list = []
        self.food_list = [Food() for _ in range(FOOD_COUNT)]
        
    def update(self):
        # field.players_list.sort(key=lambda player: player.score)
        for player in self.players_list:
            self.check_boundaries(player)
            player.check_food(self.food_list)
            player.check_player_eat(self.players_list)
            player.check_division(self.players_list)
            player.update()
        
    def check_boundaries(self, player):
        player.pos_.x = max(player.radius(), min(self.WIDTH_ - player.radius(), player.pos_.x))
        player.pos_.y = max(player.radius(), min(self.HEIGHT_ - player.radius(), player.pos_.y))

def CreateField():
    field = Field(WIDTH,HEIGHT)
    player_wasd_keyset = Keyset(
        key_up = pygame.K_w,
        key_down = pygame.K_s,
        key_left = pygame.K_a,
        key_right = pygame.K_d,
        key_division = pygame.K_SPACE
        )
    
    controllerWASD = Controller(player_wasd_keyset)
    #send message for create user
    #get player Data
    player1 = Player(controller = controllerWASD, nickname="Its my Life!", color = (0, 0, 255))
    field.players_list.append(player1)
    return field

if __name__ == "__main__":
    field = CreateField()
    running = True
    while running:
        
        # if(len(field.players_list)==1):
        #     field = CreateField()
        screen.fill((255, 255, 255))

        field.update()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        clock.tick(60)
    pygame.quit()
