import asyncio
from WebSocketClient import WebSocketClient

client = WebSocketClient("ws://localhost:8765",nickname="second")
asyncio.run(client.main())
print("Client One started")