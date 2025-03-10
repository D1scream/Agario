import asyncio
import random
import websockets
import json

import pygame
import math

from Client.Food import Food
from Client.ControlledUnit import Controlled_Unit
from Client.Controller import Controller, Keyset
from Client.Unit import Unit
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
                    self.units_list = units.players_list_
                    self.food_list = food_list.food_list_
                    
                    # print("Received food:", len(self.food_list))
                    # print("Received player: ", len(self.units_list))
            except Exception as e:
                print(f"Error receiving message: {e}")

    async def send_message(self, message):
        await self.websocket_.send(json.dumps(message))

    async def custom_send_message(self, message):
        await self.send_message(message)

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
            if (unit.id_ == websocket.id_): 
                player_unit = Controlled_Unit(controller=self.controller_,client=websocket)

                player_unit.nickname_ = unit.nickname_
                player_unit.color_ = unit.color_
                player_unit.pos_.x = unit.pos_.x
                player_unit.pos_.y = unit.pos_.y
                player_unit.direction_.x = unit.direction_.x
                player_unit.direction_.y = unit.direction_.y
                player_unit.score_ = unit.score_
                player_unit.acceleration = unit.acceleration_
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
    pygame.display.set_caption("ChunChunMaru Client")

    player_wasd_keyset = Keyset(
            key_up = pygame.K_w,
            key_down = pygame.K_s,
            key_left = pygame.K_a,
            key_right = pygame.K_d,
            key_division = pygame.K_SPACE
            )
    
    controllerWASD = Controller(player_wasd_keyset)
    field = Field(WIDTH,HEIGHT, controllerWASD )
    
    running = True
    while running:
        screen.fill((255, 255, 255))
        await field.update(screen, websocket)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        await asyncio.sleep(1/60)
    pygame.quit()

async def main(webclient : WebSocketClient):
    await webclient.connect()

    some_cool_nickname = f"Umgumpuk {random.randint(10,99)}"
    await webclient.custom_send_message( {"new_player" : some_cool_nickname})

    receive_task = asyncio.create_task(webclient.receive_messages())
    start_game_task = asyncio.create_task(start_game(webclient))

    await asyncio.gather(receive_task, start_game_task)

client = WebSocketClient("ws://localhost:8765")
asyncio.run(main(client))
