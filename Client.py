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
        self.id_ = None

    async def connect(self):
        self.websocket_ = await websockets.connect(self.uri)

    async def receive_messages(self):
        while True:
            try:
                response = await self.websocket_.recv()
                data = json.loads(response)
                from Models import PlayersListModel, FoodListModel
                
                if("player_id" in data):
                    self.id_ = int(data["player_id"])
                    print("my id is ", self.id_)
                else:
                    units = PlayersListModel.from_json(data["player_list"], Unit)
                    food_list = FoodListModel.from_json(data["food_list"], Food)
                    for p in units.players_list_:
                        pass
                    self.units_list = units.players_list_
                    self.food_list = food_list.food_list_
                    
                    # print("Received food:", len(self.food_list))
                    # print("Received player: ", len(self.units_list))
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
                direction = direction.normalize() * self.speed() 
            self.pos_ += direction

        def draw(self,screen):
            pygame.draw.circle(screen, self.color_, (int(self.pos_.x), int(self.pos_.y)), self.radius())
        
        async def update(self):
            self.acceleration = max(self.acceleration - (1 / 10), 1)
            self.collision_active_timer_ = max(0,self.collision_active_timer_ - (1/60))
            self.division_ban_timer_ = max(0,self.division_ban_timer_ - (1/60))

            

class Controlled_Unit(Unit):
    def __init__(self, controller: Controller, nickname: str="", color: tuple=(1,2,3), pos_x=0, pos_y=0,
                direction_x=0, direction_y=1, collision_active_timer=1, division_ban_time=0, score=100, acceleration=1, id=-1):
        super().__init__(nickname = nickname, color = color, pos_x = pos_x, pos_y = pos_y, direction_x=direction_x, direction_y=direction_y,
                        collision_active_timer = collision_active_timer, division_ban_timer=division_ban_time, score = score, acceleration = acceleration, id = id)
        self.controller_ = controller

    async def move(self):
        keys = pygame.key.get_pressed()
        direction = self.controller_.get_moving_vector(keys)

        await self.SendDirection(direction)

        if direction.length() > 0:
            direction = direction.normalize() * self.speed() 
        self.pos_ += direction

    async def send_division(self):
        await client.custom_send_message({"direction" : [self.direction_.x, self.direction_.y], "division" : True})

    async def SendDirection(self, direction):
            await client.custom_send_message( {"direction" : [direction.x,direction.y], "division": False })

    async def division(self):
        if self.score < 400 or self.division_ban_timer_!=0:
            return  
        await self.send_division()

    async def check_division(self):
        keys = pygame.key.get_pressed()
        if(self.controller_.get_division(keys = keys)):
            await self.division()

    def __str__(self):
        return self.nickname
    
    async def update(self):
        self.acceleration = max(self.acceleration - (1 / 10), 1)
        self.collision_active_timer_ = max(0,self.collision_active_timer_ - (1/60))
        self.division_ban_timer_ = max(0,self.division_ban_timer_ - (1/60))
        await self.move()


class Food:
    def __init__(self, x: float = 1, y: float = 1, radius: float = 5, color: tuple = (0,5,10)):
        self.x_ = x
        self.y_ = y
        self.radius_ = radius
        self.color_ = color
    
    def draw(self,screen):
        pygame.draw.circle(screen, self.color_, (self.x_, self.y_), self.radius_)
    
    def check_eated(self, player : Controlled_Unit):
        if (self.x_ - player.pos_.x) ** 2 + (self.y_ - player.pos_.y) ** 2 < (self.radius_ + player.radius()*0.9) ** 2:
            player.score+=50
            return True
        return False

class Field:
    def __init__(self, WIDTH, HEIGHT, controller : Controller):
        self.WIDTH_=WIDTH
        self.HEIGHT_=HEIGHT
        self.unit_list = []
        self.food_list = []
        self.player_list = []
        self.controller_ = controller
        
    async def update(self, screen, websocket : WebSocketClient):
        self.unit_list = websocket.units_list
        self.food_list = websocket.food_list
        self.player_list = []
        for unit in self.unit_list:
            unit : Unit = unit
            if (unit.id_ == websocket.id_): 
                player_unit = Controlled_Unit(controller=self.controller_)

                player_unit.nickname = unit.nickname
                player_unit.color_ = unit.color_
                player_unit.pos_.x = unit.pos_.x
                player_unit.pos_.y = unit.pos_.y
                player_unit.direction_.x = unit.direction_.x
                player_unit.direction_.y = unit.direction_.y
                player_unit.score = unit.score
                player_unit.acceleration = unit.acceleration
                player_unit.id_ = unit.id_

                self.player_list.append(player_unit)
                await player_unit.move()
                await player_unit.check_division()
                

            self.check_boundaries(unit)
            for food in self.food_list:
                if(food.check_eated(unit)):
                    self.food_list.remove(food)
                food.draw(screen)
            await unit.update()
            unit.draw(screen)
            

    def check_boundaries(self, unit):
        unit.pos_.x = max(unit.radius(), min(self.WIDTH_ - unit.radius(), unit.pos_.x))
        unit.pos_.y = max(unit.radius(), min(self.HEIGHT_ - unit.radius(), unit.pos_.y))

async def start_game(websocket):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("ChunChunMaru Client 1")
    clock = pygame.time.Clock()

    player_wasd_keyset = Keyset(
            key_up = pygame.K_w,
            key_down = pygame.K_s,
            key_left = pygame.K_a,
            key_right = pygame.K_d,
            key_division = pygame.K_SPACE
            )
    
    controllerWASD = Controller(player_wasd_keyset)
    #player = Player(controller = controllerWASD, nickname="Its my Life!", color = (1, 2, 3), pos_x=0, pos_y=0, 
                    # direction_x=1, direction_y=1,collision_active_timer=0, division_ban_time=0, 
                    # score=100,acceleration=1,id=-1)

    field = Field(WIDTH,HEIGHT, controllerWASD )
    
    #await client.custom_send_message( {"new_player" : player.nickname})
    running = True
    while running:
        screen.fill((255, 255, 255))
        #field.unit_list.append(player)
        await field.update(screen, websocket)
        #await player.move()
        
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
