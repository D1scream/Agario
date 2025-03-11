import json
import websockets

from Client.Food import Food
from Client.Unit import Unit

class WebSocketClient:
    def __init__(self, uri):
        self.uri = uri
        self.websocket = None
        self.units_list: list[Unit] = []
        self.food_list: list[Food] = []
        self.id = None

    async def connect(self):
        self.websocket = await websockets.connect(self.uri)

    async def receive_messages(self):
        while True:
            try:
                response = await self.websocket.recv()
                data = json.loads(response)
                from Models import PlayersListModel, FoodListModel
                
                if("player_id" in data):
                    self.id = int(data["player_id"])
                    print("my id is ", self.id)
                else:
                    
                    units = PlayersListModel.from_json(data["player_list"], Unit)
                    food_list = FoodListModel.from_json(data["food_list"], Food)
                    self.units_list = units.players_list
                    self.food_list = food_list.food_list
                    
            except Exception as e:
                print(f"Error receiving message: {e}")

    async def send_message(self, message):
        await self.websocket.send(json.dumps(message))

    async def custom_send_message(self, message):
        await self.send_message(message)