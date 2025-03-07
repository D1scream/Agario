import asyncio
import websockets
import json

class WebSocketClient:
    def __init__(self, uri,nickname):
        self.uri = uri
        self.nickname=nickname

    async def receive_messages(self, websocket):
        while True:
            response = await websocket.recv()
            print(f"Received from server: {response}")

    async def send_message(self, websocket, json_message):
        await websocket.send(json_message)

    async def custom_send_message(self, message):
        async with websockets.connect(self.uri) as websocket:
            message = {"message": f"{message}"}
            json_message = json.dumps(message)
            await self.send_message(websocket, json_message)

    async def main(self):
        async with websockets.connect(self.uri) as websocket:
            await asyncio.gather(
                self.receive_messages(websocket),
                self.custom_send_message(f"{self.nickname} IS HERE")
            )