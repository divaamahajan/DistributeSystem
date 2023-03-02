import asyncio
import json
import websockets
from buffer import Buffer


class Server:
    def __init__(self):
        self.listening_port = 8000
        self.forwarding_port = 8010
        self.listening_host = 'localhost'
        self.forwarding_host = 'localhost'
        self.pub_cols = ['name', 'uname', 'startQuarter', 'term', 'planned']
        self.sub_cols = ['uname', 'subscribe']
        self.rqst_key = 'requestID'
        self.ack_key = 'ACK'
        self.ldr_key = 'LDR'
        self.sub_key = 'subscribe'
        self.pub_queue = asyncio.Queue()
        self.sub_queue = asyncio.Queue()
        self.buffer = Buffer()
        self.lock = asyncio.Lock()

    def is_json(self,json_str):
        try:
            json.loads(json_str)
            return True
        except json.JSONDecodeError:
            return False
        
    async def set_forwarding_host(self, host):
        async with self.lock:
            self.forwarding_host = host

    async def client_handling(self, websocket: websockets.WebSocketServerProtocol, path: str):
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
                elif not self.is_json(clientRequest):
                    print(f"\nInvalid request Type.")
                    raise Exception
                else:
                    request_map = json.loads(clientRequest)
                    print(f"Below message received:\n{clientRequest}\n")

                if self.ack_key in request_map.keys():
                    #delete from buffer
                    self.buffer.remove_from_buffer(request_map[self.ack_key])
                elif self.ldr_key in request_map.keys():
                    #update forwarding host
                    print(f"\nHost IP updated:{request_map[self.ldr_key]} to forward the request to Computation Server's Port {self.forwarding_port}....")
                    await self.set_forwarding_host(request_map[self.ldr_key])
                elif self.rqst_key in request_map.keys():
                    print(f"\nExecuting Sender thread to forward the request to Computation Server's Port {self.forwarding_port}....")
                    send = asyncio.create_task(self.forwardData(request_map))
                    sending_tasks.append(send)
                    await send
                    print(f"\nSender task execution complete")
                else:
                    print(f"\nUnknown request received")
                    raise Exception
                
            except websockets.exceptions.ConnectionClosedError as e:
                print(f"\nclosing handshake didn’t complete properly. {e}\n")

            except websockets.exceptions.ConnectionClosedOK as e:
                # print(f"\n connection terminated properly. {e}\n")
                pass

            except Exception as e:
                print(f"\nException in client handling: {e}\nClosing client socket...\n")
                await websocket.close()
                break
            finally:
                # wait for sending tasks to finish
                await asyncio.gather(*sending_tasks)
                sending_tasks.clear()
                # print(f"\nClosing client socket...")
                await websocket.close()


    async def add_buffer_to_queues(self):   
        pq, sq = self.buffer.get_all_from_buffer()
        # add elements of queue1 to queue2
        while not pq.empty():
            with self.lock:
                await self.pub_queue.put(pq.get())
        while not sq.empty():
            with self.lock:
                await self.sub_queue.put(sq.get())

    async def forwardData(self,received_hashmap):
        try:
            pub_dict,sub_dict = dict(), dict()
            # create a list to keep track of all the threads
            tasks = []
            # list element is taken for referencing objects as return
            pub_dict[self.rqst_key] = str(received_hashmap[self.rqst_key])+"_P"
            pub_dict = {k: v for (k, v) in received_hashmap.items() if k in self.pub_cols and v is not None}
            if self.sub_key in received_hashmap and received_hashmap[self.sub_key] is not [] :# add only if user has subscribed
                sub_dict[self.rqst_key] = str(received_hashmap[self.rqst_key])+"_S"
                sub_dict = {k: v for (k, v) in received_hashmap.items() if k in self.sub_cols and v is not None}

            # start publishing Queue thread
            if pub_dict: # Only add to pub Queue if there is data to send
                tasks.append(asyncio.create_task(self.writeJsonToQueue("Pub", pub_dict)))

            if sub_dict: # Only add to sub Queue if there is data to send
                tasks.append(asyncio.create_task(self.writeJsonToQueue("Sub", sub_dict)))
        
            tasks.append(asyncio.create_task(self.sendDatafromQueue()))      
            await asyncio.gather(*tasks)
        except Exception as e:
            print(f"\nError in forwarding data: {e}")


    async def writeJsonToQueue(self, qName, hashmap):
        json_obj = json.dumps(hashmap)
        # put each row of JSON object into the queue
        async with self.lock:
            if qName == 'Pub':
                await self.pub_queue.put(json_obj)
            elif qName =='Sub':
                await self.sub_queue.put(json_obj)
            print(f"\nBelow object added to {qName} queue\n\t {json_obj} ")



    async def sendDatafromQueue(self):
        try:
            async with websockets.connect(f"ws://{self.forwarding_host}:{self.forwarding_port}") as websocket:
                while not self.pub_queue.empty():
                    obj = ''
                    async with self.lock:
                        if not self.pub_queue.empty():
                            obj = await self.pub_queue.get()
                    #sending data from the queue to the computation server
                    await websocket.send(obj)
                    self.buffer.add_to_buffer(id=(json.loads(obj))[self.rqst_key],json_obj=obj)         
                while not self.sub_queue.empty() and self.pub_queue.empty():
                    obj = ''
                    async with self.lock:
                        if not self.sub_queue.empty():
                            obj = self.sub_queue.get()
                    #sending data from the queue to the computation server
                    await websocket.send(obj)
                    self.buffer.add_to_buffer(id=(json.loads(obj))[self.rqst_key],json_obj=obj)          
        except Exception as e:
            print(f"sending error: {e}")                
    
    async def startServer(self):
        '''Here, we use asyncio and websockets modules to create a WebSocket server. 
        The async with block creates a server instance that listens on the specified host and port, 
        and calls the clientHandling coroutine to handle incoming connections.'''
        print("Starting server...")
        async with websockets.serve(self.client_handling, self.listening_host, self.listening_port):
            print(f"Server started on {self.listening_host}:{self.listening_port}")
            await asyncio.Future()# keep the coroutine alive forever

if __name__ == '__main__':
    sv = Server()
    asyncio.run(sv.startServer())