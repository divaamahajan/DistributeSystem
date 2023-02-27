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
            print(f"Received data: {data}")
        # clientRequest = await websocket.recv()
        # print("Check clientRequest data....")
        # if not clientRequest:  
        #     print(f"\nNo request recieved.")
        #     raise Exception
        # df = pd.read_json(clientRequest)  
        # print(f"Below message received:\n {clientRequest}")
    except Exception as e:
        print(f"Exception :{e}")
        print(f"\nClosing client connection... ")
        await websocket.close()

async def server():
    async with websockets.serve(receive_data, HOST, portNo):
        print(f"Server is listening for connection at {HOST}:{portNo}...\n")
        await asyncio.Future()  # run forever

asyncio.run(server())
