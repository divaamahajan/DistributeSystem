import asyncio
from collections import OrderedDict as od
from queue import Queue
class Buffer:
    def __init__(self):
        self.id_json = od()
        self.lock = asyncio.Lock()

    async def add_to_buffer(self, id, json_obj):
        async with self.lock:
            self.id_json[id] = json_obj

    async def get_all_from_buffer(self):
        """if multiple coroutines are accessing the same instance of the Buffer class concurrently, 
        it is possible that one coroutine reads the id_json attribute while another coroutine is modifying it 
        This can cause data inconsistency issues raising a KeyError etc."""        
        pubQueue, subQueue = Queue(), Queue()
        async with self.lock:   
            for id, obj in self.id_json.items():
                if id[-1] == 'P': pubQueue.put(self.id_json[id])
                elif id[-1] == 'S': subQueue.put(self.id_json[id])
            return (pubQueue,subQueue)

    async def remove_from_buffer(self, id):
        async with self.lock:
            if id in self.id_json.keys():
                del self.id_json[id]

