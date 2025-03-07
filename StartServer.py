import asyncio
import websockets
import json

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
    c = 0
    while True:
        c += 1
        message = {"message": f"Auto message {len(clients)}"}
        json_message = json.dumps(message)
        try:
            for client in clients:
                try:
                    await client.send(json_message)
                except websockets.exceptions.ConnectionClosed:
                    print("someone leaave")
        except:
            print("someone sdsdsdsddsd")
        await asyncio.sleep(1 / 60)

async def main():
    server = await websockets.serve(echo, "localhost", 8765)
    asyncio.create_task(send_auto_message())
    await server.wait_closed()

asyncio.run(main())
