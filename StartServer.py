import asyncio
import websockets
import json

import pygame
import random
import math


WIDTH, HEIGHT = 1280, 720

pygame.init()
clock = pygame.time.Clock()
MASS_FOR_EAT_PLAYER = 0.8
    
class Player:
    def __init__(self, nickname, color):
        self.direction_ = (0,0)
        self.collision_active_timer_ = 1
        self.division_ban_timer_ = 0.01
        self.nickname = nickname
        self.pos_ = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)
        self.score = 1000
        self.color_ = color
        self.acceleration = 1

    def speed(self):
        return 20 / math.log(self.score) * self.acceleration
    
    def radius(self):
        return math.sqrt(self.score)

    def move(self):
        direction = self.direction_
        if direction.length() > 0:
            direction = direction.normalize() * self.speed() 

        self.pos_ += direction
        
    def division(self, player_list):
        if self.score < 400 or self.division_ban_timer_!=0:
            return  
        part = Player(self.nickname, self.color_)
        
        part.score = self.score / 2
        self.score = self.score / 2
        direction = self.direction_
        if direction.length() == 0:
            direction = pygame.math.Vector2(1,1).normalize()

        part.pos_ = self.pos_ + direction * (self.radius() + part.radius() + 10)
 
        part.acceleration = 3  
        part.division_ban_timer_ = 0.1
        self.division_ban_timer_ = 0.1
        self.collision_active_timer_=1100000
        player_list.append(part)
    
    def check_food(self,food_list):
        for food in food_list:
            if(food.check_eated(self)):
                food_list.remove(food)
                food_list.append(Food())

    def check_player_eat(self, player_list):
        for player in player_list:
            mass_to_eat = MASS_FOR_EAT_PLAYER
            if(player != self and player.nickname==self.nickname):
                mass_to_eat = 1
            if(self.score * mass_to_eat > player.score ):
                distance = ((self.pos_.x - player.pos_.x)**2 + (self.pos_.y - player.pos_.y)**2)**0.5
                if(distance < self.radius()*0.8):
                    self.score += player.score
                    player_list.remove(player)
            
    def __str__(self):
        return self.nickname
    
    def __dict__(self):
        return {
            "direction": self.direction_,
            "collision_active_timer": self.collision_active_timer_,
            "division_ban_timer": self.division_ban_timer_,
            "nickname": self.nickname,
            "pos_x": self.pos_.x,
            "pos_y": self.pos_.y,
            "score": self.score,
            "color": list(self.color_),
            "acceleration": self.acceleration
        }


    def load_data(self, direction, division):
        self.direction_ = direction
        if(division):
            self.division()
            
    def update(self):
        self.acceleration = max(self.acceleration - (1 / 10), 1)
        self.collision_active_timer_ = max(0,self.collision_active_timer_ - (1/60))
        self.division_ban_timer_ = max(0,self.division_ban_timer_ - (1/60))
        
        self.move()
    

class Food:
    def __init__(self):
        self.x_ = random.randint(10, WIDTH - 10)
        self.y_ = random.randint(10, HEIGHT - 10)
        self.radius_ = 5
        self.color_ = (255, 0, 0)
    
    def check_eated(self, player : Player):
        if (self.x_ - player.pos_.x) ** 2 + (self.y_ - player.pos_.y) ** 2 < (self.radius_ + player.radius()*0.9) ** 2:
            player.score+=50
            return True
        return False

    @property
    def __dict__(self):
        return {
            "x": self.x_,
            "y": self.y_,
            "radius": self.radius_,
            "color": list(self.color_)
        }

class Field:
    def __init__(self, WIDTH, HEIGHT, FOOD_COUNT = 50):
        self.WIDTH_=WIDTH
        self.HEIGHT_=HEIGHT

        self.players_list = []
        self.food_list = [Food() for _ in range(FOOD_COUNT)]
        
    def update(self):
        self.players_list.sort(key=lambda player: player.score)
        for player in self.players_list:
            self.check_boundaries(player)
            player.check_food(self.food_list)
            player.check_player_eat(self.players_list)
            player.check_division(self.players_list)
            player.update()

    def check_new_clients(self):
        for nc in clients:
            if nc not in clients_players_dict:
                self.add_new_player(nc)
        
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


async def send_message(message):
    json_message = json.dumps(message)
    try:
        for client in list(clients):
            try:
                #print(f"sended {json_message}")
                await client.send(json_message)
            except websockets.exceptions.ConnectionClosed:
                print("Client disconnected")
                clients.discard(client)
                clients_players_dict.pop(client, None)
    except:
        print("Error in send")
    #await asyncio.sleep(1 / 60)

async def send_game_state(field):
    while True:
        if len(field.players_list) == 1:
            field = await create_field(clients)
        field.update()
        food_data = [food.__dict__ for food in field.food_list]
        players_data = [player.__dict__ for player in field.players_list]
        data = {"player_list": players_data, "food_list": food_data}

        await send_message(data)
        await asyncio.sleep(1/60)

clients = set()

def check_new_players(field : Field):
    for client in clients:
        if client not in clients_players_dict:
            field.add_new_player(client)


def start_game():
    field = create_field(clients)
    running = False
    while running:
        if(len(field.players_list)==1):
            field = create_field(clients)
        field.update()
        send_game_state(player_list = field.players_list, food_list = field.food_list)
        check_new_players(field)
        clock.tick(60)

async def echo(websocket, path=""):
    clients.add(websocket)
    check_new_players
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
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
                
                #print(f"Received: {data}")
            except json.JSONDecodeError:
                await websocket.send('Error: Invalid JSON')
    except websockets.exceptions.ConnectionClosed:
        print("connection closed")
        pass
    finally:
        clients.discard(websocket)
        clients_players_dict.pop(websocket, None)

async def main():
    field = await create_field(clients)
    asyncio.create_task(send_game_state(field)) 
    server = await websockets.serve(echo, "localhost", 8765)
    await server.wait_closed()

asyncio.run(main())