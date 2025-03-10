import asyncio
import websockets
import json
import pygame
import random

from Models import FoodListModel, PlayersListModel
from Server.Food import Food
from Server.Player import Unit
from GlobalConstants import WIDTH, HEIGHT


class PlayerManager:
    def __init__(self):
        self.clients_players_dict = {}
        self.id_players_dict = {}
        self.client_nickname_dict = {}

    def add_new_player(self, client):
        free_id = self.get_free_player_id()
        nickname = self.client_nickname_dict.get(client, "unknown")
        player = Unit(nickname=nickname, color=self.generate_random_color(), id=free_id)

        margin = 50
        player.pos_ = pygame.math.Vector2(
            random.randint(margin, WIDTH - margin),
            random.randint(margin, HEIGHT - margin)
        )

        # Добавляем игрока в id_players_dict
        self.id_players_dict.setdefault(free_id, []).append(player)

        # Добавляем клиента в clients_players_dict
        self.clients_players_dict[client] = free_id

        return player

    def generate_random_color(self, max_sum=600):
        while True:
            color = (random.randint(50, 150), random.randint(50, 150), random.randint(50, 150))
            if sum(color) <= max_sum:
                return color

    def get_free_player_id(self):
        # Ищем свободный ID
        return next(i for i in range(1, 10000) if i not in self.id_players_dict)

    async def remove_player(self, websocket):
        # Удаляем игрока из всех связанных с ним данных
        player_id = self.clients_players_dict.pop(websocket, None)
        if player_id:
            self.id_players_dict.pop(player_id, None)

    def get_player_id(self, websocket):
        return self.clients_players_dict.get(websocket)

    def get_players_by_id(self, player_id):
        return self.id_players_dict.get(player_id, [])


class Field:
    def __init__(self, WIDTH, HEIGHT, FOOD_COUNT=100, player_manager=None):
        self.WIDTH_ = WIDTH
        self.HEIGHT_ = HEIGHT
        self.food_list = [Food() for _ in range(FOOD_COUNT)]
        self.player_manager = player_manager if player_manager else PlayerManager()

    def update(self, players_list):
        # Обновляем игроков по ID
        players_list = sorted(players_list.items(), key=lambda item: item[1])
        players_list.sort(key=lambda player: player.score)
        players_list = [p for p in players_list if p.id_ in self.player_manager.id_players_dict]

        for player in players_list:
            self.check_boundaries(player)
            self.check_food(player)
            self.check_collisions(player, players_list)
            player.update()

    def check_food(self, player: Unit):
        for food in self.food_list:
            if food.check_eated(player):
                self.food_list.remove(food)
                self.food_list.append(Food())

    def check_collisions(self, player, players_list):
        for other_player in players_list:
            if player.check_player_eat(other_player):
                player.score += other_player.score
                players_list.remove(other_player)
                self.player_manager.id_players_dict[other_player.id_].remove(other_player)

            if player.division_flag:
                player.division_flag = False
                if len(self.player_manager.id_players_dict[player.id_]) < 16:
                    part = player.division(players_list)
                    if part:
                        self.player_manager.id_players_dict[part.id_].append(part)

    def check_boundaries(self, player):
        player.pos_.x = max(player.radius(), min(self.WIDTH_ - player.radius(), player.pos_.x))
        player.pos_.y = max(player.radius(), min(self.HEIGHT_ - player.radius(), player.pos_.y))

    async def check_game_over(self):
        disconnected_players = [pid for pid in self.player_manager.id_players_dict if not self.player_manager.id_players_dict[pid]]
        for player_id in disconnected_players:
            client = next((k for k, v in self.player_manager.clients_players_dict.items() if v == player_id), None)
            if client:
                await send_message(client, {"game_over": True})
                print("game over sent to", player_id)

            self.player_manager.id_players_dict.pop(player_id)
            await self.add_new_player(client)

    async def check_new_clients(self):
        new_clients = [c for c in clients if c not in self.player_manager.clients_players_dict]
        for client in new_clients:
            await self.add_new_player(client)

    async def add_new_player(self, client):
        player = self.player_manager.add_new_player(client)
        await send_message(client, {"player_id": player.id_})


async def create_field(clients):
    player_manager = PlayerManager()
    field = Field(WIDTH, HEIGHT, player_manager=player_manager)
    await asyncio.gather(
        *(field.player_manager.add_new_player(client) for client in clients)
    )
    
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
        *(send_message(client, message) for client in clients)
    )


async def send_game_state(field: Field):
    players_data = PlayersListModel(field.player_manager.id_players_dict)
    food_data = FoodListModel(field.food_list)
    data = {"player_list": players_data.to_json(), "food_list": food_data.to_json()}

    await field.check_new_clients()
    await field.check_game_over()
    field.update(field.player_manager.id_players_dict)
    await send_message_to_all(data)


async def start_game():
    print("Game Started")
    field = await create_field(clients)
    running = True
    while running:
        await send_game_state(field)
        await asyncio.sleep(1 / 60)


async def remove_player(websocket):
    clients.discard(websocket)

    player_id = client_manager.clients_players_dict.pop(websocket, None)
    if player_id:
        client_manager.id_players_dict.pop(player_id, None)


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

                if "new_player" in data:
                    client_nickname_dict[websocket] = data["new_player"]
                    print(f"{data['new_player']} joined to circle party")

                elif "direction" in data and "division" in data:  # Потом разделить на два сигнала
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
