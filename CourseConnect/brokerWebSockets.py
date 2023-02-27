import asyncio
import json
import queue
import threading
import websockets
import pandas as pd

LISTEN_PORT = 8000
FORWARD_PORT = 8010
HOST = 'localhost'
PUBCOLS = ['uname', 'startQuarter', 'term', 'planned']
SUBCOLS = ['uname', 'subscribe']

pubQueue, subQueue = queue.Queue(), queue.Queue()
lock = threading.Lock()

async def sendDatafromQueue(pubQ, subQ):
    async with websockets.connect(f"ws://{HOST}:{FORWARD_PORT}") as websocket:
        while not pubQ.empty():
            with lock:
                obj = pubQ.get()
                await websocket.send(json.dumps(obj))
                await asyncio.sleep(1)  # wait 1 second between each row
        while pubQ.empty() and not subQ.empty():
            with lock:
                obj = subQ.get()
                await websocket.send(json.dumps(obj))
                await asyncio.sleep(1)  # wait 1 second between each row

async def send_data(port, data):
    async with websockets.connect(f"ws://{HOST}:{port}") as websocket:
        await websocket.send(data)


async def clientHandling(websocket, path):
    print("Handeling the Client")
    sending_tasks = []
    while True:
        try:
            # Receive request (packet) from client and decode
            clientRequest = await websocket.recv()
            # If no request received from client close connection and break
            if not clientRequest:
                print(f"\nNo request received.")
                raise Exception
            df = pd.read_json(clientRequest)
            print(f"Below message received:\n {df}")

            print(f"\nExecuting Sender thread to forward the request to Computation Server's Port {FORWARD_PORT}....")
            send = asyncio.create_task(forwardData(clientRequest))
            sending_tasks.append(send)
            await send
            print(f"\nSender task execution complete")


        except Exception as e:
            print(f"\nClosing client handling: {e}\nClosing client socket...\n")
            await websocket.close()
            break
        finally:
            # wait for sending tasks to finish
            await asyncio.gather(*sending_tasks)
            sending_tasks.clear()
            print(f"\nClosing client socket...")
            await websocket.close()


async def writeJsonToQueue(qName, json_obj, qList: queue.Queue()):
    data_queue = qList[0]
    # put each row of JSON object into the queue
    with lock:
        data_queue.put(json_obj)
        print(f"\nBelow object added to {qName} queue\n\t {json_obj} ")

async def forwardData(receivedJson):
    try:
        # create a list to keep track of all the threads
        tasks = []
        json_list = json.loads(receivedJson)
        # list element is taken for referencing objects as return
        pubList, subList = [queue.Queue()], [queue.Queue()]

        for row in json_list:
            pub_dict = {k: v for (k, v) in row.items() if k in PUBCOLS and v is not None}
            if row.get('subscribe') is not None:  # add only if user has subscribed      
                sub_dict = {k: v for (k, v) in row.items() if k in SUBCOLS and v is not None}
            # start publishing Queue thread
            if pub_dict: # Only add to pubList if there is data to send
                tasks.append(asyncio.create_task(writeJsonToQueue("Pub", json.dumps(pub_dict), pubList)))

            if sub_dict: # Only add to subList if there is data to send
                tasks.append(asyncio.create_task(writeJsonToQueue("Sub", json.dumps(pub_dict), pubList)))

        pubQueue, subQueue = pubList[0], subList[0]
        if pubQueue:
            print("\nBelow is the data of PubQ:\n\t")
            print(*list(pubQueue.queue), sep='\t\n')
        if subQueue:
            print("\n\nBelow is the data of SubQ:\n\t")
            print(*list(subQueue.queue), sep='\t\n')
        # sendThread = threading.Thread(target= sendDatafromQueue, args=(pubQueue, subQueue,))          
        tasks.append(asyncio.create_task(sendDatafromQueue(pubQueue, subQueue)))      
        await asyncio.gather(*tasks)
    except Exception as e:
        print(f"\nError in forwarding data: {e}")

async def startServer():
    '''Here, we use asyncio and websockets modules to create a WebSocket server. 
    The async with block creates a server instance that listens on the specified host and port, 
    and calls the clientHandling coroutine to handle incoming connections.'''
    print("Starting server...")
    async with websockets.serve(clientHandling, HOST, LISTEN_PORT):
        print(f"Server started on {HOST}:{LISTEN_PORT}")
        await asyncio.Future()# keep the coroutine alive forever

if __name__ == '__main__':
    # asyncio.run(websockets.serve(main, HOST, FORWARD_PORT))    
    asyncio.run(startServer())



