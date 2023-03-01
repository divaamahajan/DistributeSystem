import asyncio
import json
import queue
import threading
import websockets
import pandas as pd
from buffer import Buffer

LISTEN_PORT = 8000
FORWARD_PORT = 8010
LISTENING_HOST = 'localhost'
forwarding_host = 'localhost'
PUBCOLS = ['name', 'uname', 'startQuarter', 'term', 'planned']
SUBCOLS = ['uname', 'subscribe']
RQST_KEY = 'requestID'
ACK_KEY = 'ACK'
LDR_KEY = 'LDR'
SUB_KEY = 'subscribe'
pubQueue, subQueue = queue.Queue(), queue.Queue()
lock = threading.Lock()
buffer = Buffer()

def is_json(json_str):
    try:
        json.loads(json_str)
        return True
    except json.JSONDecodeError:
        return False
    
async def set_forwarding_host(host):
    with lock:
        forwarding_host = host

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
            elif not is_json(clientRequest):
                print(f"\nInvalid request Type.")
                raise Exception
            else:
                request_map = json.loads(clientRequest)
                print(f"Below message received:\n{clientRequest}\n")
            
            if ACK_KEY in request_map.keys():
                #delete from buffer
                buffer.remove_from_buffer(request_map[ACK_KEY])
            elif LDR_KEY in request_map.keys():
                #update forwarding host
                print(f"\nHost IP updated:{request_map[LDR_KEY]} to forward the request to Computation Server's Port {FORWARD_PORT}....")
                set_forwarding_host(request_map[LDR_KEY])
            elif RQST_KEY in request_map.keys():
                print(f"\nExecuting Sender thread to forward the request to Computation Server's Port {FORWARD_PORT}....")
                send = asyncio.create_task(forwardData(request_map))
                sending_tasks.append(send)
                await send
                print(f"\nSender task execution complete")
            else:
                print(f"\nUnknown request received")
                raise Exception

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


async def forwardData(received_hashmap):
    try:
        pub_dict,sub_dict = dict(), dict()
        # create a list to keep track of all the threads
        tasks = []
        # list element is taken for referencing objects as return
        pub_dict[RQST_KEY] = str(received_hashmap[RQST_KEY])+"_P"
        pub_dict = {k: v for (k, v) in received_hashmap.items() if k in PUBCOLS and v is not None}
        if SUB_KEY in received_hashmap and received_hashmap[SUB_KEY] is not [] :# add only if user has subscribed
            sub_dict[RQST_KEY] = str(received_hashmap[RQST_KEY])+"_S"
            sub_dict = {k: v for (k, v) in received_hashmap.items() if k in SUBCOLS and v is not None}

        # start publishing Queue thread
        if pub_dict: # Only add to pub Queue if there is data to send
            tasks.append(asyncio.create_task(writeJsonToQueue("Pub", pub_dict)))

        if sub_dict: # Only add to sub Queue if there is data to send
            tasks.append(asyncio.create_task(writeJsonToQueue("Sub", sub_dict)))
      
        tasks.append(asyncio.create_task(sendDatafromQueue()))      
        await asyncio.gather(*tasks)
    except Exception as e:
        print(f"\nError in forwarding data: {e}")


async def writeJsonToQueue(qName, hashmap):
    json_obj = json.dumps(hashmap)
    # put each row of JSON object into the queue
    with lock:
        if qName == 'Pub':
            pubQueue.put(json_obj)
        elif qName =='Sub':
            subQueue.put(json_obj)
        print(f"\nBelow object added to {qName} queue\n\t {json_obj} ")

async def sendDatafromQueue():
    async with websockets.connect(f"ws://{forwarding_host}:{FORWARD_PORT}") as websocket:
        while pubQueue:
            obj = ''
            with lock:
                obj = pubQueue.get() 
                await websocket.send(obj)
                buffer.add_to_buffer(id=(json.loads(obj))[RQST_KEY],json_obj=obj)                
                # await websocket.send(json.dumps(obj))
                # await asyncio.sleep(1)  # wait 1 second between each row
        while subQueue and not pubQueue:
            obj = ''
            with lock:
                obj = subQueue.get()
                await websocket.send(obj)
                buffer.add_to_buffer(id=(json.loads(obj))[RQST_KEY],json_obj=obj)       
                # await asyncio.sleep(1)  # wait 1 second between each row

async def add_buffer_to_queue():   
    pq, sq = buffer.get_all_from_buffer()
    # add elements of queue1 to queue2
    while not pq.empty():
        with lock:
            pubQueue.put(pq.get())
    while not sq.empty():
        with lock:
            subQueue.put(pq.get())
            
async def startServer():
    '''Here, we use asyncio and websockets modules to create a WebSocket server. 
    The async with block creates a server instance that listens on the specified host and port, 
    and calls the clientHandling coroutine to handle incoming connections.'''
    print("Starting server...")
    async with websockets.serve(clientHandling, LISTENING_HOST, LISTEN_PORT):
        print(f"Server started on {LISTENING_HOST}:{LISTEN_PORT}")
        await asyncio.Future()# keep the coroutine alive forever

if __name__ == '__main__':
    # asyncio.run(websockets.serve(main, HOST, FORWARD_PORT))    
    asyncio.run(startServer())



