import pygame
import random

WIDTH, HEIGHT = 1280, 720

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ChunChunMaru")
clock = pygame.time.Clock()

class IController:
    def __init__(self):
        pass

    def get_move(self,keys):
        direction = pygame.math.Vector2(0, 0)

        if keys[pygame.K_w]: direction.y = -1
        if keys[pygame.K_s]: direction.y = 1
        if keys[pygame.K_a]: direction.x = -1
        if keys[pygame.K_d]: direction.x = 1

        return direction

class Player:
    def __init__(self,controller=IController()):
        self.controller=controller
        self.pos = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)
        self.radius = 20
        self.speed = 3
        self.color = (0, 0, 255)
    
    def move(self):
        keys = pygame.key.get_pressed()
        #direction = pygame.math.Vector2(0, 0)
        direction = self.controller.get_move(keys)

        if direction.length() > 0:
            direction = direction.normalize() * self.speed

        self.pos += direction
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)
    
    def check_food(self,food_list):

        for food in food_list:
            if(food.check_eated(self)):
                food_list.remove(food)
                food_list.append(Food())
            food.draw()

    def update(self):
        self.move()
        self.draw()

class Food:
    def __init__(self):
        self.x = random.randint(10, WIDTH - 10)
        self.y = random.randint(10, HEIGHT - 10)
        self.radius = 5
        self.color = (255, 0, 0)
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
    
    def check_eated(self,player):
        if (self.x - player.pos.x) ** 2 + (self.y - player.pos.y) ** 2 < (self.radius + player.radius*0.9) ** 2:
            player.radius+=0.5
            return True
        return False

    def update(self):
        self.draw()

class Field:
    def __init__(self,WIDTH, HEIGHT, FOOD_COUNT = 50):
        self.WIDTH=WIDTH
        self.HEIGHT=HEIGHT

        self.players_list = []
        self.food_list = [Food() for _ in range(FOOD_COUNT)]
        
    def update(self):
        for player in self.players_list:
            self.check_boundaries(player)
            player.check_food(self.food_list)
            player.update()
        

    def check_boundaries(self, player):
        player.pos.x = max(player.radius*0.9, min(self.WIDTH - player.radius*0.9, player.pos.x))
        player.pos.y = max(player.radius*0.9, min(self.HEIGHT - player.radius*0.9, player.pos.y))
        
if __name__ == "__main__":
    field = Field(WIDTH,HEIGHT)


    controllerWASD = ControllerWASD()
    controllerARROWS = ControllerARROWS()
    player1=Player(controller=controllerWASD)
    player2=Player(controller=controllerARROWS)

    player2.pos.x+=100
    player2.pos.y+=100

    field.players_list.append(player1)
    field.players_list.append(player2)

    running = True
    while running:
        screen.fill((255, 255, 255))

        field.update()
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        clock.tick(60)

    pygame.quit()
