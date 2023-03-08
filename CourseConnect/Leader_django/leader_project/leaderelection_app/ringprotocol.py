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
ELECTION_KEY = 'election'
LEADER_ELECTED_KEY = 'elected'
ALL_NODES_KEY = 'network'
SUCCESSOR_KEY = 'successor'
NODEFAIL_KEY = 'nodefail'
LEADERFAIL_KEY = 'leaderfailed'
LDR_UPD_KEY = 'LDR'
BROKER_IP = 'host'
BROKER_PORT = 8000
PORT = 9000

class Leader:
    def __init__(self, leader_ip):
        self.leader_ip = leader_ip
        self.ring_nodes = None
        PORT = 9000

    def send_msg(self, destination_ip, msg):
        if ":" not in destination_ip:
            destination_ip += ":" + str(PORT)
        req = httplib2.Http()
        r, content = req.request(destination_ip, method="POST",body=json.dumps(msg))

    def update_leader(self,leader_ip):
        self.leader_ip = leader_ip

    def get_leader(self):
        return self.leader_ip 

    def update_ring_nodes(self,ring_nodes:list()):
        self.ring_nodes = None
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
                next_successor_ip = node.get_successor(next_ip)     
                update_successor_msg =  {SUCCESSOR_KEY: [next_ip,next_successor_ip]}
                self.send_msg(destination_ip={curr_ip}, msg=update_successor_msg)
                node = node.next
                if node == self.ring_nodes.head:
                    break
        except Exception as e:
            print("\n\nException while updating successors of the ring : {e}\n")

    def failure_handling(self, failed_ip):
        try:
            pred_ip = self.ring_nodes.get_predecessor(failed_ip) #to change its next 2 successor
            succ_ip = self.ring_nodes.get_successor(failed_ip)          # new successor 1 
            next_successor_ip = self.ring_nodes.get_successor(succ_ip)  # new successor 2
            self.ring_nodes.remove_node(failed_ip)                      # remove the failed node from the ring
            update_successor_msg =  {SUCCESSOR_KEY: [succ_ip,next_successor_ip]}            
            self.send_msg(destination_ip={pred_ip}, msg=update_successor_msg)
        except Exception as e:
            print("\n\nException while failure handling : {e}\n")

    def update_broker(self):
        update_broker_msg = {LDR_UPD_KEY:self.get_leader()}
        address = f"{BROKER_IP}:{str(BROKER_PORT)}"
        self.send_msg(destination_ip = address, msg=update_broker_msg)

class RingProtocolLeaderElection:
    def __init__(self, my_ip, next_ip):
        self.my_ip = my_ip
        self.next_ip = next_ip
        self.next_successsor_ip = None #2nd successor for backup
        self.leader = Leader(None, None)
    
    def send_msg(self, destination_ip, msg):
        req = httplib2.Http()
        resp, content = req.request(destination_ip, method="POST",body=json.dumps(msg))
    
    #initiate election
    def initiate_election(self):
        self.election(None)
            
    #election process, sending their electing nominee
    def election(self, electing_ip):
        #Algorithm stops and shares elected_leader when my_ip = electing nominee 
        try:
            if electing_ip == self.my_ip:               # my_ip = max_ip = leader
                nodes = list()                          # collect all nodes in the ring
                nodes.append(self.my_ip)                # add my_ip first as head of the list
                self.leader.update_leader(self.my_ip)   # update my leader in leader class 
                elected_leader_msg = {LEADER_ELECTED_KEY: self.my_ip, self.ALL_NODES_KEY:nodes} 
                                                        #send msg to next node about elected_leader
                self.send_msg(destination_ip={self.next_ip}, msg=elected_leader_msg)
            else:                               #add the max_ip to electing msg and pass to next_ip
                self.leader.update_leader(None) #clear the current leader, untin new leader is elected
                if electing_ip > self.my_ip:
                    election_msg = {ELECTION_KEY: electing_ip}
                                                # electing_ip = None : my_ip has initiated the election
                elif electing_ip is None or electing_ip < self.my_ip:
                    election_msg = {ELECTION_KEY: self.my_ip}
                self.send_msg(destination_ip={self.next_ip}, msg=election_msg)
        except Exception as e:
            print(f"\n\nException while election : {e}\n")
        
    # Nodes sharing and updating their elected leader   
    def elected_leader(self, leader_ip, nodes:list()):
        #Algorithm stops and performs leader's job when my_ip = leader 
        try:
            if self.leader.get_leader() == self.my_ip: # If my_ip = leader, 
                self.perform_leader_job(nodes)         # perform job and
                return                                 # stop algorithm
            nodes.append(self.my_ip)                # Add my_ip to list of all nodes in ring
            self.leader.update_leader(leader_ip)    # Update my leader and share new leader msg to next
            elected_leader_msg =  {LEADER_ELECTED_KEY: leader_ip, self.ALL_NODES_KEY:nodes}
            self.send_msg(destination_ip={self.next_ip}, msg=elected_leader_msg)
        except Exception as e:
            print(f"\n\nException while updating elected leader: {e}\n")
        
    # if I am leader, my leader object will perform its tasks
    def perform_leader_job(self, nodes:list()):
        try:
            self.leader.update_ring_nodes(nodes)    #create linked list from list of Ip's in ring
            self.leader.update_successor_of_ring()  #update Next_ip of all Nodes
            self.leader.update_broker()
        except Exception as e:
            print(f"\n\nException performing leader's tasks: {e}\n")
        
    # Update next 2 successors
    def update_successor(self, ip_list:list()):
        next_ip, next_successor_ip = ip_list[0], ip_list[1]
        self.next_ip = next_ip
        self.next_successsor_ip = next_successor_ip
    
    #local failure handeling of a node
    def failure_handling(self, failed_ip):
        leader_ip = self.leader.get_leader() 
        if leader_ip == self.my_ip:                 #If I lam leader, 
            self.leader.failure_handling(failed_ip)     # perform failure handeling
        elif failed_ip == leader_ip:                # if leader has failed
            self.leader_failure_notification(failed_ip)          # send notification to other nodes
        elif leader_ip is None:                     #if no leader found, 
            self.initiate_election()                   # initiate election
        else:                                       #else inform leader
            node_fail_msg =  {NODEFAIL_KEY: failed_ip}            
            self.send_msg(destination_ip={leader_ip}, msg=node_fail_msg)

    # actions to perform if leader has failed
    def leader_failure_notification(self, failed_ip):
        # Algorithm stops ans starts election when all nodes have cleared their leader
        leader_ip = self.leader.get_leader() 
        if leader_ip is None:                     # if no leader found,
            self.initiate_election()                         # initiate election
            return
        elif failed_ip != leader_ip:                # If leader has not failed
            self.failure_handling(failed_ip)            # send to failure_handling
            return
        elif leader_ip == self.next_ip:               # if next node has failed, 
            self.next_ip = self.next_successsor_ip      # make backup node as next node
            self.next_successsor_ip = None              # and clear backup node
            
        self.leader.update_leader(None)             #clear leader, so as to end the notificaton cycle 
        leader_fail_msg =  {LEADERFAIL_KEY: failed_ip}            
        self.send_msg(destination_ip={self.next_ip}, msg=leader_fail_msg) #inform next node about leader failure