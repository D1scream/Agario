import pygame
from Client.Controller import Controller
from Client.Unit import Unit


class ControlledUnit(Unit):
    def __init__(self, controller: Controller, 
                 client, nickname: str="", 
                 color: tuple=(1,2,3), 
                 pos_x=0, pos_y=0,
                 direction_x=0, direction_y=1, 
                 collision_active_timer=1, 
                 division_ban_time=0, 
                 score=100, 
                 acceleration=1, 
                 id=-1):
        super().__init__(nickname=nickname, 
                         color=color, 
                         pos_x=pos_x, 
                         pos_y=pos_y, 
                         direction_x=direction_x, 
                         direction_y=direction_y,
                         collision_active_timer=collision_active_timer,
                         division_ban_timer=division_ban_time, 
                         score=score, 
                         acceleration=acceleration, 
                         id=id)
        self.controller_ = controller
        self.client = client

    async def move(self):
        
        direction = self.get_direction_from_keys()
        await self.send_direction(direction)
        self.direction_ = direction
        if direction.length() > 0:
            direction = direction.normalize() * self.speed() 
        self.pos += direction

    def get_direction_from_keys(self):
        keys = pygame.key.get_pressed()
        return self.controller_.get_moving_vector(keys)
    
    async def send_division(self):
        await self.client.custom_send_message({"direction": [self.direction_.x, self.direction_.y], "division": True})

    async def send_direction(self, direction):
        await self.client.custom_send_message( {"direction": [direction.x,direction.y], "division": False })

    async def division(self):
        if self.score >= 400 and self.division_ban_timer == 0:
            await self.send_division()

    async def check_division(self):
        keys = pygame.key.get_pressed()
        if(self.controller_.get_division(keys=keys)):
            await self.division()

    def __str__(self):
        return self.nickname
    
    async def update(self):
        await self.move()