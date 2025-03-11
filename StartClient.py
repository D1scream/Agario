import asyncio
import random
import websockets
import json
import pygame

from Client.Food import Food
from Client.ControlledUnit import ControlledUnit
from Client.Controller import Controller, Keyset
from Client.Unit import Unit
from Client.UserInterface import UserInterface
from Client.WebSocketClient import WebSocketClient
from GlobalConstants import FIELD_WIDTH, FIELD_HEIGHT, TICK_INTERVAL, WINDOW_WIDTH, WINDOW_HEIGHT

class Field:
    def __init__(self, WIDTH, HEIGHT, controller: Controller):
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.unit_list = []
        self.food_list = []
        self.player_list = []
        self.controller = controller
        
    async def update(self, screen, websocket: WebSocketClient):
        self.unit_list: list[Unit] = websocket.units_list
        self.food_list: list[Food] = websocket.food_list
        self.player_list: list[ControlledUnit] = []
        for unit in self.unit_list:
            if (unit.id == websocket.id): 
                player_unit = ControlledUnit(controller=self.controller, client=websocket)

                player_unit.nickname = unit.nickname
                player_unit.color = unit.color
                player_unit.pos.x = unit.pos.x
                player_unit.pos.y = unit.pos.y
                player_unit.direction.x = unit.direction.x
                player_unit.direction.y = unit.direction.y
                player_unit.score = unit.score
                player_unit.acceleration = unit.acceleration
                player_unit.id = unit.id

                self.player_list.append(player_unit)
                await player_unit.move()
                await player_unit.check_division()
                
            self.check_boundaries(unit)
            for food in self.food_list:
                food.draw(screen)

            await unit.update()
            unit.draw(screen)
            
            
    def check_boundaries(self, unit: Unit):
        unit.pos.x = max(unit.get_radius(), min(self.WIDTH - unit.get_radius(), unit.pos.x))
        unit.pos.y = max(unit.get_radius(), min(self.HEIGHT - unit.get_radius(), unit.pos.y))

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

async def main(webclient: WebSocketClient):
    await webclient.connect()

    some_cool_nickname = f"Umgumpuk {random.randint(10,99)}"
    await webclient.custom_send_message( {"new_player": some_cool_nickname})

    receive_task = asyncio.create_task(webclient.receive_messages())
    start_game_task = asyncio.create_task(start_game(webclient))

    await asyncio.gather(receive_task, start_game_task)

client = WebSocketClient("ws://localhost:8765")
asyncio.run(main(client))
