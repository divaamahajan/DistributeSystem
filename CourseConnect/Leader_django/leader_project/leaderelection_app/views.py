from django.shortcuts import render
import json
from . ringprotocol import RingProtocolLeaderElection as ring
# Create your views here.

ELECTION_KEY = 'election'
LEADER_ELECTED_KEY = 'elected'
ALL_NODES_KEY = 'network'
SUCCESSOR_KEY = 'successor'
NODEFAIL_KEY = 'nodefail'
LEADERFAIL_KEY = 'leaderfailed'
PORT = 9000
my_ip = "host"
next_ip = "next_host"
node = ring(my_ip, next_ip)
def listen(request):
    if(request.method == "POST"):
        msg = json.loads(request.body)
        if ELECTION_KEY in msg.keys():
            node.election(msg[ELECTION_KEY])
        elif LEADER_ELECTED_KEY in msg.keys():
            node.elected_leader(msg[LEADER_ELECTED_KEY],msg[ALL_NODES_KEY] )
        elif SUCCESSOR_KEY in msg.keys():
            node.update_successor(msg[SUCCESSOR_KEY])
        elif NODEFAIL_KEY in msg.keys():
            node.failure_handling(msg[NODEFAIL_KEY])        
        elif LEADERFAIL_KEY in msg.keys():
            node.leader_failure_notification(msg[LEADERFAIL_KEY])
        