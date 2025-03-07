
import asyncio
from WebSocketClient import WebSocketClient


client = WebSocketClient("ws://localhost:8765",nickname="first")
asyncio.run(client.main())
