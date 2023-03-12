import asyncio
import websockets
import json
import pandas as pd
import os


HOST, PORT = "localhost", 8000

async def send_data(message):
    uri = f"ws://{HOST}:{PORT}"
    for row in message:
        async with websockets.connect(uri) as websocket:
            await websocket.send(json.dumps(row))       
            print("Sent the below message:\n", pd.DataFrame([row]).set_index('requestID').transpose())
        
path = os.getcwd()
json_filepath = os.path.join(path, "CourseConnect", "userInput.json")
with open(json_filepath) as json_file:
    data = (json.load(json_file))

asyncio.get_event_loop().run_until_complete(send_data(data))