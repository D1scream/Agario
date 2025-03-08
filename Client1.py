import asyncio
import asyncio
import websockets
import json

import pygame
import math


WIDTH, HEIGHT = 1280, 720


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

    async def SendDirection(self, direction):
        await client.custom_send_message( {"direction" : [direction.x,direction.y], "division": False })

    async def move(self):
        keys = pygame.key.get_pressed()
        direction = self.controller_.get_moving_vector(keys)

        await self.SendDirection(direction)

        if direction.length() > 0:
            direction = direction.normalize() * self.speed() 
        self.pos_ += direction

    async def send_division(self):
        await client.custom_send_message({"direction" : self.direction, "division" : True})
    def division(self):
        self.send_division()
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

    def draw(self,screen):
        pygame.draw.circle(screen, self.color_, (int(self.pos_.x), int(self.pos_.y)), self.radius())
    
    def check_food(self,food_list):
        for food in food_list:
            if(food.check_eated(self)):
                food_list.remove(food)
                #Добавить на сервере
                #food_list.append(Food())
            food.draw()

    def check_division(self, player_list):
        keys = pygame.key.get_pressed()
        if(self.controller_.get_division(keys = keys)):
            new_part = self.division()
            if(new_part):
                player_list.append(new_part)

    def __str__(self):
        return self.nickname
    
    async def update(self, screen):
        self.acceleration = max(self.acceleration - (1 / 10), 1)
        self.collision_active_timer_ = max(0,self.collision_active_timer_ - (1/60))
        self.division_ban_timer_ = max(0,self.division_ban_timer_ - (1/60))
        await self.move()

        self.draw(screen)


class Food:
    def __init__(self,x,y):
        self.x_ = x
        self.y_ = y
        self.radius_ = 5
        self.color_ = (255, 0, 0)
    
    def draw(self,screen):
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
        self.food_list = []
        
    async def update(self, screen):
        for player in self.players_list:
            self.check_boundaries(player)
            player.check_food(self.food_list)
            player.check_division(self.players_list)
            await player.update(screen)

    def check_boundaries(self, player):
        player.pos_.x = max(player.radius(), min(self.WIDTH_ - player.radius(), player.pos_.x))
        player.pos_.y = max(player.radius(), min(self.HEIGHT_ - player.radius(), player.pos_.y))


async def start_game():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("ChunChunMaru Client 1")
    clock = pygame.time.Clock()


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
        player1 = Player(controller = controllerWASD, nickname="Its my Life!", color = (0, 0, 255))
        field.players_list.append(player1)
        return field

    field = CreateField()
    running = True
    while running:
        
        screen.fill((255, 255, 255))

        await field.update(screen)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        clock.tick(60)
    pygame.quit()

class WebSocketClient:
    def __init__(self, uri):
        self.uri = uri
        self.websocket_ = None

    async def receive_messages(self):
        while True:
            print("get")
            try:
                print("get2")
                response = await self.websocket_.recv()
                print("get3")
                data = json.loads(response)
                players_field = data.get("player_list")
                food_list = data.get("food_list")
                print("Received players: ", len(players_field))
                print("Received food:", len(food_list))

            except Exception as e:
                print(f"Error receiving message: {e}")
                pass

    async def send_message(self, json_message):
        await client.websocket_.send(json_message)

    async def custom_send_message(self, message):
        json_message = json.dumps(message)
        await self.send_message( json_message)

    async def main(self):
        websocket = await websockets.connect(self.uri)
        self.websocket_ = websocket
        message = {"message": "Someone is HERE"}
        await self.custom_send_message( message)
        receive_task = asyncio.create_task(self.receive_messages())
        start_game_task = asyncio.create_task(start_game())
        await asyncio.gather(receive_task, start_game_task)

client = WebSocketClient("ws://localhost:8765")
asyncio.run(client.main())
