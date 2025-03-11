import asyncio
import websockets
import json
import pygame
import random

from Models import FoodListModel, PlayersListModel
from Server.Food import Food
from Server.Player import Unit
from GlobalConstants import FIELD_WIDTH, FIELD_HEIGHT, TICK_INTERVAL, generate_random_color


class Field:
    def __init__(self, WIDTH, HEIGHT, FOOD_COUNT=100):
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.players_list: list[Unit] = []
        self.food_list = [Food() for _ in range(FOOD_COUNT)]
    
    def update(self):
        self.players_list.sort(key=lambda player: player.score)
        self.players_list: list[Unit]= [p for p in self.players_list if p.id in id_players_dict]

        for player in self.players_list:
            self.check_boundaries(player)
            self.start_eat_food(player)

            for other_player in self.players_list:
                if(player.check_player_eat(other_player)):
                    player.score += other_player.score
                    self.players_list.remove(other_player)
                    id_players_dict[other_player.id].remove(other_player)

            if(player.division_flag):
                player.division_flag = False
                if len(id_players_dict[player.id]) < 16:
                    part = player.division(self.players_list)
                    if part:
                        id_players_dict[part.id].append(part)

            player.update()

    def start_eat_food(self, player : Unit): 
        for food in self.food_list:
            distance = (food.x - player.pos.x) ** 2 + (food.y - player.pos.y) ** 2
            if distance < player.get_radius() ** 2:
                player.score += food.score
                self.food_list.remove(food)
                self.food_list.append(Food())

    async def check_game_over(self):
        disconnected_players = [pid for pid in id_players_dict if not id_players_dict[pid]]
        for player_id in disconnected_players:
            client = next((k for k, v in clients_players_dict.items() if v == player_id), None)
            if client:
                await send_message(client, {"game_over": True}) 
                print("game over sent to", player_id)
            
            id_players_dict.pop(player_id) 
            await self.add_new_player(client)

    async def check_new_clients(self):
        new_clients = [c for c in clients if c not in clients_players_dict]
        for client in new_clients:
            await self.add_new_player(client)
                
    def check_boundaries(self, player: Unit):
        player.pos.x = max(player.get_radius(), min(self.WIDTH - player.get_radius(), player.pos.x))
        player.pos.y = max(player.get_radius(), min(self.HEIGHT - player.get_radius(), player.pos.y))

    async def add_new_player(self, client):
        free_id = next(i for i in range(1, 10000) if i not in id_players_dict)
    
        nickname = client_nickname_dict.get(client, "unknown")
        player = Unit( nickname=nickname, color=generate_random_color(min_sum=50, max_sum=600), id=free_id)

        margin = 50
        player.pos = pygame.math.Vector2(
                random.randint(margin, FIELD_WIDTH - margin),
                random.randint(margin, FIELD_HEIGHT - margin))
        
        self.players_list.append(player)
        id_players_dict.setdefault(free_id, []).append(player)

        clients_players_dict[client] = player.id
        await send_message(client, {"player_id": player.id})
        

async def create_field(clients):
    foodCount = int(FIELD_HEIGHT * FIELD_WIDTH / 50 ** 2)
    field = Field(FIELD_WIDTH, FIELD_HEIGHT, foodCount)
    await asyncio.gather(
        *(field.add_new_player(client) for client in clients))
        
    return field

async def send_message(websocket, message):
    try:
        await websocket.send(json.dumps(message))
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
        return False
    return True

async def send_message_to_all(message):
    await asyncio.gather(
        *(send_message(client, message) for client in clients))
           
async def send_game_state(field : Field):
    players_data = PlayersListModel(field.players_list)
    food_data = FoodListModel(field.food_list)
    data = {"player_list" : players_data.to_json(), "food_list": food_data.to_json()}

    await field.check_new_clients()
    await field.check_game_over()
    field.update()
    await send_message_to_all(data)
    
async def start_game():
    print("Server Started")
    field = await create_field(clients)
    running = True
    while running:
        asyncio.create_task(send_game_state(field))
        #await send_game_state(field)
        await asyncio.sleep(TICK_INTERVAL)
        
async def remove_player(websocket):
    clients.discard(websocket)

    player_id = clients_players_dict.pop(websocket, None)
    if player_id:
        id_players_dict.pop(player_id, None)

clients_players_dict = {}
clients = set()
id_players_dict = {}
client_nickname_dict = {}


async def echo(websocket, path=""):
    clients.add(websocket)
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)

                if("new_player" in data):
                    client_nickname_dict[websocket] = data["new_player"]
                    print(f"{data["new_player"]} joined to circle party")

                elif("direction" in data and "division" in data): # Потом разделить на два сигнала 
                    player_id = clients_players_dict.get(websocket)
                    if player_id and player_id in id_players_dict:
                        for player in id_players_dict[player_id]:
                            player.load_data(data["direction"], data["division"])

                else:
                    print("Wrong JSON", data)
                    # Выбросить исключение и отправить игроку
                
            except Exception as e:
                await websocket.send(json.dumps({"error": str(e)}))

    except websockets.exceptions.ConnectionClosed:
        print(f"{client_nickname_dict.get(websocket, 'Unknown player')} disconnected")
        await remove_player(websocket)

async def main():
    asyncio.create_task(start_game()) 
    server = await websockets.serve(echo, "localhost", 8765)
    await server.wait_closed()

asyncio.run(main())