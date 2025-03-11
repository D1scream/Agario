import asyncio
import random
import websockets
import json
import pygame

from Client.Food import Food
from Client.ControlledUnit import Controlled_Unit
from Client.Controller import Controller, Keyset
from Client.Unit import Unit
from Client.UserInterface import UserInterface
from Client.WebSocketClient import WebSocketClient
from GlobalConstants import FIELD_WIDTH, FIELD_HEIGHT, TICK_INTERVAL, WINDOW_WIDTH, WINDOW_HEIGHT

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
                player_unit = Controlled_Unit(controller=self.controller_, client=websocket)

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
                food.draw(screen)

            await unit.update()
            unit.draw(screen)
            
            
    def check_boundaries(self, unit : Unit):
        unit.pos_.x = max(unit.get_radius(), min(self.WIDTH_ - unit.get_radius(), unit.pos_.x))
        unit.pos_.y = max(unit.get_radius(), min(self.HEIGHT_ - unit.get_radius(), unit.pos_.y))

async def start_game(websocket):
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("ChunChunMaru Client")

    player_wasd_keyset = Keyset(
            key_up = pygame.K_w,
            key_down = pygame.K_s,
            key_left = pygame.K_a,
            key_right = pygame.K_d,
            key_division = pygame.K_SPACE
            )
    
    controllerWASD = Controller(player_wasd_keyset)
    field = Field(FIELD_WIDTH, FIELD_HEIGHT, controllerWASD )
    UI = UserInterface()
    running = True
    while running:
        screen.fill((255, 255, 255))
        async def DrawGame():
            await field.update(screen, websocket)
            UI.unit_list=field.unit_list
            UI.player_list = field.player_list
            UI.draw(screen)
            pygame.display.flip()

        asyncio.create_task(DrawGame())
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        await asyncio.sleep(TICK_INTERVAL)
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
