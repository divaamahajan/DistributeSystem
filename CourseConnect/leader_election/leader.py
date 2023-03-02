"""Psudo Algo
each node has info about it's own ip, next node's ip and leader's ip

Leader election algorithm which follows below steps
step1: any node can initiate an election via the method election and passing None as as parameter and sends it's ip as election:ip to next node
step2: once a node receives a notification to initiate an election via election:ip msg, it calls method election which compares the current election:ip with its own ip, and forwards the bigger ip to next node in election:ip
step3: when incoming election:ip from election method == current(my own) ip. method elected leader is initiated. This method updates the local variable leader_ip and forwards elected leader ip to next node
step4: when a node received a msg elected leader ip, it calls method elected leader ito update the local variable leader_ip and forwards elected leader ip to next node
step5 if received a msg elected leader ip == current(my own) ip. algorithm stops
"""

import asyncio
import json
import websockets
import requests
from linkedlist import SortedCircularLinkedList as scll
class RingProtocolLeaderElection:
    def __init__(self, my_ip, next_ip):
        self.my_ip = self.get_public_ip()
        # self.my_ip = my_ip
        self.next_ip = next_ip
        self.leader_ip = None
        self.lock = asyncio.Lock()
        self.election_key = 'election'
        self.leader_elected_key = 'elected'
        self.allnodes_key = 'network'
        self.successor_key = 'successor'
        self.ring_nodes = None
    
    
    def get_public_ip(self):
        try: 
            url = 'https://api.ipify.org'
            response = requests.get(url)
            return response.text
        except Exception as e:
            print(f"\n\nError to get public Ip : {e}\n")
    

    async def initiate_election(self):
        async with websockets.connect(f"ws://{self.next_ip}") as websocket:
            msg = {"type": "election", "ip": self.my_ip}
            await websocket.send(json.dumps(msg))
            
    async def election(self, electing_ip):
        try:
            if electing_ip == self.my_ip:
                nodes = scll()
                nodes.add_node(self.my_ip)
                async with self.lock:
                    self.leader_ip = self.my_ip
                    elected_leader_msg = {self.leader_elected_key: self.my_ip, self.allnodes_key:nodes}
                    async with websockets.connect(f"ws://{self.next_ip}") as websocket:
                        await websocket.send(json.dumps(elected_leader_msg))
            else:
                if electing_ip > self.my_ip:
                    election_msg = {self.election_key: electing_ip}
                elif electing_ip is None or electing_ip < self.my_ip:
                    election_msg = {self.election_key: self.my_ip}
                async with websockets.connect(f"ws://{self.next_ip}") as websocket:
                    await websocket.send(json.dumps(election_msg))
        except Exception as e:
            print(f"\n\nException while election : {e}\n")
        
    async def elected_leader(self, leader_ip, nodes:scll()):
        try:
            nodes.add_node(self.my_ip)
            async with self.lock:
                if self.leader_ip == self.my_ip:
                    self.perform_leader_job(nodes)
                    return
                self.leader_ip = leader_ip
            elected_leader_msg =  {self.leader_elected_key: self.my_ip, self.allnodes_key:nodes}
            async with websockets.connect(f"ws://{self.next_ip}") as websocket:
                await websocket.send(json.dumps(elected_leader_msg))
        except Exception as e:
            print(f"\n\nException while updating elected leader: {e}\n")
        

    async def perform_leader_job(self, nodes:scll()):
        try:
            #updates nodes list
            self.ring_nodes = nodes        
            if self.ring_nodes.head is None:
                return
            node = self.ring_nodes.head
            while True:
                curr_ip = node.data
                next_ip = node.get_successor(curr_ip)
                update_successor_msg =  {self.successor_key: next_ip}
                async with websockets.connect(f"ws://{curr_ip}") as websocket:
                    await websocket.send(json.dumps(update_successor_msg))
                node = node.next
                if node == self.ring_nodes.head:
                    break
        except Exception as e:
            print(f"\n\nException performing leader's tasks: {e}\n")
        

    async def update_successor(self, successor_ip):
        self.next_ip = successor_ip
    
    async def listen(self):
        try:
            async with websockets.connect(f"ws://{self.my_ip}") as websocket:
                async for msg in websocket:
                    msg = json.loads(msg)
                    if self.election_key in msg.keys():
                        await self.election(msg[self.election_key])
                    elif self.leader_elected_key in msg.keys():
                        await self.elected_leader(msg[self.leader_elected_key],msg[self.allnodes_key] )
                    elif self.successor_key in msg.keys():
                        await self.update_successor(msg[self.successor_key])
        except Exception as e:
            print(f"\n\nException while listening to message : {e}\n")
        
