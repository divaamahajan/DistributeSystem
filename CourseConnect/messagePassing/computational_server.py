import socket
import pandas as pd
import asyncio
import websockets
import json

HOST = 'localhost'
portNo = 8010
PACKET_SIZE = 4086
async def receive_data(websocket, path):
    try:
        print("Handling client..")
        async for message in websocket:
            data = json.loads(message)
            print(f"\n\nReceived data: {data}")
    except Exception as e:
        print(f"Exception :{e}")
        print(f"\nClosing client connection... ")
        await websocket.close()

async def server():
    async with websockets.serve(receive_data, HOST, portNo):
        print(f"\n\nServer is listening for connection at {HOST}:{portNo}...\n")
        await asyncio.Future()  # run forever

asyncio.run(server())
