import asyncio
import websockets
import json
from Models import FoodListModel,PlayersListModel
import pygame
import random

from Server.Food import Food
from Server.Player import Unit
from GlobalConstants import WIDTH, HEIGHT



pygame.init()
clock = pygame.time.Clock()


class Field:
    def __init__(self, WIDTH, HEIGHT, FOOD_COUNT = 100):
        self.WIDTH_=WIDTH
        self.HEIGHT_=HEIGHT
        self.players_list = []
        self.food_list = [Food() for _ in range(FOOD_COUNT)]
    
    def check_food(self, player:Unit):
        for food in self.food_list:
            if(food.check_eated(player)):
                self.food_list.remove(food)
                self.food_list.append(Food())


    def update(self):
        self.players_list.sort(key=lambda player: player.score)

        self.players_list = [player for player in self.players_list if player.id_ in id_players_dict]

        
        #print(len(self.players_list), len(id_players_dict))
        for player in self.players_list:
            player : Unit = player
            #print()
            self.check_boundaries(player)
            self.check_food(player)

            for other_player in self.players_list:
                other_player : Unit = other_player

                if(player.check_player_eat(other_player)):
                    player.score += other_player.score
                    print(other_player.id_, " have eat ", player.id_)
                    self.players_list.remove(other_player)
                    id_players_dict[other_player.id_].remove(other_player)

            if(player.division_flag):
                player.division_flag = False
                if len(id_players_dict[player.id_])<16:
                    part = player.division(self.players_list)
                
                    if(part):
                        id_players_dict[part.id_].append(part)
                        print("divided",part.id_)
            player.update()

            
    async def check_game_over(self):
        for player_id in list(id_players_dict.keys()):  
            if len(id_players_dict[player_id]) == 0:
                client = next((k for k, v in clients_players_dict.items() if v == player_id), None)
                if client:
                    await send_message(client, {"game_over": True}) 
                    print("game over sent to", player_id)
                
                id_players_dict.pop(player_id) 
                await self.add_new_player(client)

    async def check_new_clients(self):
        for nc in clients:
            if nc not in clients_players_dict:
                await self.add_new_player(nc)
                
    def check_boundaries(self, player):
        player.pos_.x = max(player.radius(), min(self.WIDTH_ - player.radius(), player.pos_.x))
        player.pos_.y = max(player.radius(), min(self.HEIGHT_ - player.radius(), player.pos_.y))

    async def add_new_player(self, client):
        free_id = 1
        while True:
            is_free_id = True
            for pl in self.players_list:
                if pl.id_ == free_id:
                    free_id+=1
                    is_free_id=False
                    break
            if(is_free_id):
                print("free id is ", free_id)
                break

        def generate_random_color(max_sum=600):
            while True:
                color = (random.randint(50, 150), random.randint(50, 150), random.randint(50, 150))
                if sum(color) <= max_sum:
                    return color
        if(client in client_nickname_dict):
            nickname = client_nickname_dict[client]
        else:
            nickname = "uknown"
        player = Unit( nickname=nickname, color = generate_random_color(600) ,id = free_id)
        margin = 50
        player.pos_ = pygame.math.Vector2(
                random.randint(margin, WIDTH - margin),
                random.randint(margin, HEIGHT - margin)
            )
        self.players_list.append(player)

        if free_id not in id_players_dict:
            id_players_dict[free_id] = []

        id_players_dict[free_id].append(player)

        clients_players_dict[client] = player.id_
        await send_message(client, {"player_id": player.id_})
        print("id sended", int(player.id_))
        return player.id_
        
clients_players_dict = {}
async def create_field(clients):
    field = Field(WIDTH,HEIGHT)
    for client in clients:
        await field.add_new_player(client)
        
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
                remove_player(client)
    except Exception as e:
        print(f"Error in send {e}")
    #await asyncio.sleep(1 / 60)
async def send_game_state(field : Field):
    while True:
        # if len(field.players_list) == 1:
        #     field = await create_field(clients)
        
        players_data = PlayersListModel(field.players_list)
        food_data = FoodListModel(field.food_list)
        data = {"player_list": players_data.to_json(), "food_list": food_data.to_json()}

        await field.check_new_clients()
        await field.check_game_over()
        #print(players_data.to_json())
        field.update()
        await send_message_to_all(data)
        await asyncio.sleep(1/60)
        

clients = set()

async def start_game():
    print("Game Started")
    field = await create_field(clients)
    running = True
    while running:
        await send_game_state(field)
        
async def remove_player(websocket):
    if websocket in clients:
        clients.remove(websocket)
    
    if websocket in clients_players_dict:
        id_players_dict.pop(int(clients_players_dict[websocket]), None)
        clients_players_dict.pop(websocket, None)
    
        print("client removed")
        

id_players_dict = {}
client_nickname_dict = {}
async def echo(websocket, path=""):
    clients.add(websocket)
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                #print(data)
                if("new_player" in data):
                    new_player_nickname = data.get("new_player")
                    client_nickname_dict[websocket] = new_player_nickname
                    print(new_player_nickname, " joined to circle party")
                else:
                    try:
                        direction = data.get("direction") 
                        division = data.get("division")
                        if websocket in clients_players_dict:
                            player_id = int(clients_players_dict[websocket])
                            for player in id_players_dict[player_id]:
                                player.load_data(direction, division)
                        else:
                            print(f"{websocket} WebSocket not found in clients_players_dict")
                            
                    except Exception as e:
                        print(f"Error: {e}")
                
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