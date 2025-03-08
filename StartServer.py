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
    def __init__(self, websocket, nickname, color):
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
        #getMove
        direction = self.controller_.get_moving_vector(keys)

        if direction.length() > 0:
            direction = direction.normalize() * self.speed() 

        self.pos_ += direction
        
    def division(self):
        if self.score < 400 or self.division_ban_timer_!=0:
            return  

        part = Player(self.nickname, self.color_)
        
        part.score = self.score / 2
        self.score = self.score / 2

        #get direction from user
        direction = self.controller_.get_moving_vector(keys)

        if direction.length() == 0:
            direction = pygame.math.Vector2(1,1).normalize()

        part.pos_ = self.pos_ + direction * (self.radius() + part.radius() + 10)
 
        part.acceleration = 3  
        part.division_ban_timer_ = 0.1
        self.division_ban_timer_ = 0.1
        self.collision_active_timer_=1100000
        return part
    
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
            

    def do_division(self, player_list):
        new_part = self.division()
        if(new_part):
            player_list.append(new_part)

    def __str__(self):
        return self.nickname
    
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
        
    def check_boundaries(self, player):
        player.pos_.x = max(player.radius(), min(self.WIDTH_ - player.radius(), player.pos_.x))
        player.pos_.y = max(player.radius(), min(self.HEIGHT_ - player.radius(), player.pos_.y))

def CreateField(clients):
    field = Field(WIDTH,HEIGHT)
    for client in clients:
        player = Player(websocket=client, nickname="unknown", color = (0, 0, 255))
        field.players_list.append(player)
    return field

def StartGame():
    field = CreateField()
    running = True
    while running:
        if(len(field.players_list)==1):
            field = CreateField()
        field.update()
        SendData()
        clock.tick(60)
        
clients = set()

async def echo(websocket, path=""):
    clients.add(websocket)
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                print(f"Received: {data}")
                response = json.dumps({"status": "received", "message": data["message"]})
                await websocket.send(response)
                for client in clients:
                    if client != websocket:
                        await client.send(message)
            except json.JSONDecodeError:
                await websocket.send('Error: Invalid JSON')
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clients.remove(websocket)

async def send_auto_message():
    size=0
    while True:
        if(len(clients)!=size):
            size=len(clients)
            message = {"message": f"Auto message {len(clients)}"}
            json_message = json.dumps(message)
            try:
                for client in clients:
                    try:
                        await client.send(json_message)
                    except websockets.exceptions.ConnectionClosed:
                        print("someone leaave")
            except:
                print("someone EXITTTTTT")
        await asyncio.sleep(1 / 60)

async def main():
    server = await websockets.serve(echo, "localhost", 8765)
    asyncio.create_task(send_auto_message())
    StartGame(clients)
    await server.wait_closed()

asyncio.run(main())