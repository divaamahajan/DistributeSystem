"""Psudo Algo
each node has info about it's own ip, next node's ip and leader's ip

Leader election algorithm which follows below steps
step1: any node can initiate an election via the method election and passing None as as parameter and sends it's ip as election:ip to next node
step2: once a node receives a notification to initiate an election via election:ip msg, it calls method election which compares the current election:ip with its own ip, and forwards the bigger ip to next node in election:ip
step3: when incoming election:ip from election method == current(my own) ip. method elected leader is initiated. This method updates the local variable leader_ip and forwards elected leader ip to next node
step4: when a node received a msg elected leader ip, it calls method elected leader ito update the local variable leader_ip and forwards elected leader ip to next node
step5 if received a msg elected leader ip == current(my own) ip. algorithm stops
"""
import json
import httplib2
from . linkedlist import SortedCircularLinkedList as scll

class Leader:
    def __init__(self, leader_ip):
        self.leader_ip = leader_ip
        self.ring_nodes = None
        self.port = 9000

    def send_msg(self, destination_ip, msg):
        destination_ip = destination_ip + ":" + str(self.port)
        req = httplib2.Http()
        r, content = req.request(destination_ip, method="POST",body=json.dumps(msg))

    def update_leader(self,leader_ip):
        self.leader_ip = leader_ip

    def get_leader(self):
        return self.leader_ip 

    def update_ring_nodes(self,ring_nodes:list()):
        self.ring_nodes = scll()
        for node in ring_nodes: 
            self.ring_nodes.add_node(data=node)
    
    def update_successor_of_ring(self):
        try:
            if self.ring_nodes.head is None:
                return
            node = self.ring_nodes.head
            while True:
                curr_ip = node.data
                next_ip = node.get_successor(curr_ip)
                update_successor_msg =  {self.successor_key: next_ip}
                self.send_msg(destination_ip={curr_ip}, msg=update_successor_msg)
                node = node.next
                if node == self.ring_nodes.head:
                    break
        except Exception as e:
            print("\n\nException while updating successors of the ring : {e}\n")

    def failure_handling(self, failed_ip):
        try:
            pred_ip = self.ring_nodes.get_predecessor(failed_ip)
            succ_ip = self.ring_nodes.get_successor(failed_ip)
            self.ring_nodes.remove_node(failed_ip)
            update_successor_msg =  {self.successor_key: succ_ip}            
            self.send_msg(destination_ip={pred_ip}, msg=update_successor_msg)
        except Exception as e:
            print("\n\nException while failure handling : {e}\n")

class RingProtocolLeaderElection:
    def __init__(self, my_ip, next_ip):
        # self.my_ip = self.get_public_ip()
        self.my_ip = my_ip
        self.next_ip = next_ip
        self.leader = Leader(None, None)
        self.election_key = 'election'
        self.leader_elected_key = 'elected'
        self.allnodes_key = 'network'
        self.successor_key = 'successor'
        self.nodefail_key = 'nodefail'
        self.port = 9000
    
    def send_msg(self, destination_ip, msg):
        req = httplib2.Http()
        resp, content = req.request(destination_ip, method="POST",body=json.dumps(msg))
    

    def initiate_election(self):
        self.election(None)
            
    def election(self, electing_ip):
        try:
            if electing_ip == self.my_ip:
                nodes = list()
                nodes.append(self.my_ip)
                self.leader.update_leader(self.my_ip)
                elected_leader_msg = {self.leader_elected_key: self.my_ip, self.allnodes_key:nodes}
                self.send_msg(destination_ip={self.next_ip}, msg=elected_leader_msg)
            else:
                if electing_ip > self.my_ip:
                    election_msg = {self.election_key: electing_ip}
                elif electing_ip is None or electing_ip < self.my_ip:
                    election_msg = {self.election_key: self.my_ip}
                self.send_msg(destination_ip={self.next_ip}, msg=election_msg)
        except Exception as e:
            print(f"\n\nException while election : {e}\n")
        
    def elected_leader(self, leader_ip, nodes:list()):
        try:
            # nodes.add_node(self.my_ip)
            nodes.append(self.my_ip)
            if self.leader.get_leader() == self.my_ip:
                self.perform_leader_job(nodes)
                return
            self.leader.update_leader(leader_ip)
            elected_leader_msg =  {self.leader_elected_key: leader_ip, self.allnodes_key:nodes}
            self.send_msg(destination_ip={self.next_ip}, msg=elected_leader_msg)
            # with websockets.connect(f"ws://{self.next_ip}") as websocket:
            #     await websocket.send(json.dumps(elected_leader_msg))
        except Exception as e:
            print(f"\n\nException while updating elected leader: {e}\n")
        
    
    def perform_leader_job(self, nodes:list()):
        try:
            #updates nodes list
            self.leader.update_ring_nodes(nodes)
            self.leader.update_successor_of_ring()
        except Exception as e:
            print(f"\n\nException performing leader's tasks: {e}\n")
        

    def update_successor(self, successor_ip):
        self.next_ip = successor_ip
    
    def failure_handling(self, failed_ip):
        leader_ip = self.leader.get_leader() 
        if leader_ip == self.my_ip:
            self.leader.failure_handling(failed_ip)
        elif failed_ip == leader_ip:
            self.election(None)
        else:
            #inform leader
            node_fail_msg =  {self.nodefail_key: failed_ip}            
            self.send_msg(destination_ip={leader_ip}, msg=node_fail_msg)
