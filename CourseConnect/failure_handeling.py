import asyncio
from collections import OrderedDict as od

class Buffer:
    def __init__(self):
        self.id_json = od()
        self.lock = asyncio.Lock()

    async def add_to_buffer(self, id, json_obj):
        async with self.lock:
            self.id_json[id] = json_obj

    async def get_from_buffer(self, id):
        """if multiple coroutines are accessing the same instance of the Buffer class concurrently, 
        it is possible that one coroutine reads the id_json attribute while another coroutine is modifying it 
        This can cause data inconsistency issues raising a KeyError etc."""
        async with self.lock:
            return self.id_json[id]

    async def remove_from_buffer(self, id):
        async with self.lock:
            if id in self.id_json.keys():
                del self.id_json[id]
