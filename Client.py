import asyncio
import asyncio
import websockets
import json

import pygame
import math

from GlobalConstants import WIDTH, HEIGHT
class WebSocketClient:
    def __init__(self, uri):
        self.uri = uri
        self.websocket_ = None
        self.units_list = []
        self.food_list = []

    async def connect(self):
        self.websocket_ = await websockets.connect(self.uri)

    async def receive_messages(self):
        while True:
            try:
                response = await self.websocket_.recv()
                data = json.loads(response)
                from Models import PlayersListModel, FoodListModel

                units = PlayersListModel.from_json(data["player_list"], Unit)
                food_list = FoodListModel.from_json(data["food_list"], Food)
                
                self.units_list = units.players_list_
                self.food_list = food_list.food_list_
                
                print("Received food:", len(self.food_list))
                print("Received player: ", len(self.units_list))
            except Exception as e:
                print(f"Error receiving message: {e}")

    async def send_message(self, json_message):
        await client.websocket_.send(json_message)

    async def custom_send_message(self, message):
        json_message = json.dumps(message)
        await self.send_message( json_message)

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
    

class Unit:
        def __init__(self, nickname: str, color: tuple, 
                     pos_x=WIDTH // 2, pos_y=HEIGHT // 2, direction_x = 1, direction_y = 1, 
                     score=1000, acceleration=1, collision_active_timer = 1, division_ban_timer = 0.01,
                     id = -1):
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
                direction = direction.normalize() * self.speed() 
            self.pos_ += direction

        def draw(self,screen):
            pygame.draw.circle(screen, self.color_, (int(self.pos_.x), int(self.pos_.y)), self.radius())
        
        def check_food(self,food_list, screen):
            for food in food_list:
                if(food.check_eated(self)):
                    food_list.remove(food)
                food.draw(screen)
        async def update(self, screen):
            self.acceleration = max(self.acceleration - (1 / 10), 1)
            self.collision_active_timer_ = max(0,self.collision_active_timer_ - (1/60))
            self.division_ban_timer_ = max(0,self.division_ban_timer_ - (1/60))

            self.draw(screen)
            
class Player(Unit):
    def __init__(self, controller: Controller, nickname: str, color: tuple, pos_x=WIDTH // 2, pos_y=HEIGHT // 2, score=1000, acceleration=1):
        super().__init__(nickname, color, pos_x, pos_y, score, acceleration)
        self.controller_ = controller

    async def move(self):

        keys = pygame.key.get_pressed()
        direction = self.controller_.get_moving_vector(keys)

        await self.SendDirection(direction)

        if direction.length() > 0:
            direction = direction.normalize() * self.speed() 
        self.pos_ += direction

    async def send_division(self):
        await client.custom_send_message({"direction" : self.direction, "division" : True})

    async def SendDirection(self, direction):
            await client.custom_send_message( {"direction" : [direction.x,direction.y], "division": False })

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
        #self.draw(screen)


class Food:
    def __init__(self, x: float = 1, y: float = 1, radius: float = 5, color: tuple = (0,5,10)):
        self.x_ = x
        self.y_ = y
        self.radius_ = radius
        self.color_ = color
    
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
        self.unit_list = []
        self.food_list = []
        
    async def update(self, screen, websocket : WebSocketClient):
        self.unit_list = websocket.units_list
        self.food_list = websocket.food_list
        for unit in self.unit_list:
            self.check_boundaries(unit)
            unit.check_food(self.food_list, screen)
            await unit.update(screen)

    def check_boundaries(self, unit):
        unit.pos_.x = max(unit.radius(), min(self.WIDTH_ - unit.radius(), unit.pos_.x))
        unit.pos_.y = max(unit.radius(), min(self.HEIGHT_ - unit.radius(), unit.pos_.y))

async def start_game(websocket):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("ChunChunMaru Client 1")
    clock = pygame.time.Clock()

    field = Field(WIDTH,HEIGHT)
    player_wasd_keyset = Keyset(
            key_up = pygame.K_w,
            key_down = pygame.K_s,
            key_left = pygame.K_a,
            key_right = pygame.K_d,
            key_division = pygame.K_SPACE
            )
    
    controllerWASD = Controller(player_wasd_keyset)
    player = Player(controller = controllerWASD, nickname="Its my Life!", color = (1, 2, 3))
    #await client.custom_send_message( {"new_player" : player.nickname})
    running = True
    while running:
        screen.fill((255, 255, 255))
        #print("frame ")
        await field.update(screen, websocket)
        await player.move()
        field.unit_list.append(player)
        #await player.check_division(field.unit_list)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        await asyncio.sleep(1/60)
    pygame.quit()

async def main(webclient : WebSocketClient):
    
    await webclient.connect()
    receive_task = asyncio.create_task(webclient.receive_messages())
    start_game_task = asyncio.create_task(start_game(webclient))
    await asyncio.gather(receive_task, start_game_task)

client = WebSocketClient("ws://localhost:8765")
asyncio.run(main(client))
