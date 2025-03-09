import asyncio
import websockets
import json
from Models import FoodListModel,PlayersListModel
import pygame
import random
import math

from Food import Food
from Player import Player
from GlobalConstants import WIDTH, HEIGHT

pygame.init()
clock = pygame.time.Clock()


class Field:
    def __init__(self, WIDTH, HEIGHT, FOOD_COUNT = 50):
        self.WIDTH_=WIDTH
        self.HEIGHT_=HEIGHT
        self.players_list = []
        self.food_list = [Food() for _ in range(FOOD_COUNT)]
    
    def check_food(self, player:Player):
        for food in self.food_list:
            if(food.check_eated(player)):
                self.food_list.remove(food)
                self.food_list.append(Food())


    def update(self):
        self.players_list.sort(key=lambda player: player.score)
        disconnected_players = [player for player in self.players_list if player not in clients_players_dict.values()]

        for player in disconnected_players:
            self.players_list.remove(player)
            print(f"Removed disconnected player: {player.nickname}")

        for player in self.players_list:
            self.check_boundaries(player)
            self.check_food(player)
            player.check_player_eat(self.players_list)
            player.update()

    def check_new_clients(self):
        for nc in clients:
            if nc not in clients_players_dict:
                self.add_new_player(nc)
                print(f"nc {nc}")
        
    def check_boundaries(self, player):
        player.pos_.x = max(player.radius(), min(self.WIDTH_ - player.radius(), player.pos_.x))
        player.pos_.y = max(player.radius(), min(self.HEIGHT_ - player.radius(), player.pos_.y))

    def add_new_player(self, client):
        player = Player( nickname="unknown", color = (0, 0, 255))
        self.players_list.append(player)
        clients_players_dict[client] = player


clients_players_dict = {}
async def create_field(clients):
    field = Field(WIDTH,HEIGHT)
    for client in clients:
        field.add_new_player(client)
    return field


async def send_message(websocket, message):
    json_message = json.dumps(message)
    try:
        #print(f"sended {json_message}")
        await websocket.send(json_message)
        #print(f"sended {json_message}")
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected bubububu")

async def send_message_to_all(message):
    json_message = json.dumps(message)
    try:
        for client in list(clients):
            try:
                #print(f"sended {json_message}")
                await client.send(json_message)
                #print(f"sended {json_message}")
            except websockets.exceptions.ConnectionClosed:
                print("Client disconnected And now SomeOneHaveToBeDeleted")
                clients.discard(client)
                clients_players_dict.pop(client, None)
                print("SomeOne Was Deleted")
    except Exception as e:
        print(f"Error in send {e}")
    #await asyncio.sleep(1 / 60)

async def send_game_state(field):
    while True:
        # if len(field.players_list) == 1:
        #     field = await create_field(clients)
        
        players_data = PlayersListModel(field.players_list)
        food_data = FoodListModel(field.food_list)
        data = {"player_list": players_data.to_json(), "food_list": food_data.to_json()}

        field.check_new_clients()
        print(players_data.to_json())
        field.update()
        await send_message_to_all(data)
        print()
        await asyncio.sleep(1/60)
        

clients = set()

async def start_game():
    print("Game Started")
    field = await create_field(clients)
    running = True
    while running:
        await send_game_state(field)
        
async def remove_player(websocket):
    """Удаление игрока при отключении"""
    if websocket in clients:
        clients.remove(websocket)
    
    if websocket in clients_players_dict:
        clients_players_dict.pop(websocket, None)
        


async def echo(websocket, path=""):
    clients.add(websocket)
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                 # Проверяем, есть ли поле 'getPlayerId' в данных
                if "getPlayerId" in data:
                    # Проверяем, что websocket есть в clients_players_dict
                    if websocket in clients_players_dict:
                        # Отправляем ID игрока
                        player = clients_players_dict[websocket]
                        await send_message(websocket, {"player_id": player.id_})
                    else:
                        print(f"WebSocket {websocket} не найден в clients_players_dict.")
                #print(data)
                try:
                    direction = data.get("direction") 
                    division = data.get("division")
                    if websocket in clients_players_dict:
                        clients_players_dict[websocket].load_data(direction, division)
                    else:
                        print(f"{websocket} WebSocket not found in clients_players_dict")
                        pass
                        
                except Exception as e:
                    print(f"{e} Error")
                
            except json.JSONDecodeError:
                await websocket.send('Error: Invalid JSON')
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
        await remove_player(websocket)


async def main():
    asyncio.create_task(start_game()) 
    server = await websockets.serve(echo, "localhost", 8765)
    await server.wait_closed()

asyncio.run(main())