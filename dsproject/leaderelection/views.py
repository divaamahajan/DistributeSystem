from django.shortcuts import render
import json
from . ringprotocol import RingProtocolLeaderElection as ring
# Create your views here.

election_key = 'election'
leader_elected_key = 'elected'
allnodes_key = 'network'
successor_key = 'successor'
nodefail_key = 'nodefail'
port = 9000
my_ip = "host"
next_ip = "next_host"
node = ring(my_ip, next_ip)
def listen(request):
    if(request.method == "POST"):
        msg = json.loads(request.body)
        if election_key in msg.keys():
            node.election(msg[election_key])
        elif leader_elected_key in msg.keys():
            node.elected_leader(msg[leader_elected_key],msg[allnodes_key] )
        elif successor_key in msg.keys():
            node.update_successor(msg[successor_key])
        elif nodefail_key in msg.keys():
            node.failure_handling(msg[nodefail_key])
        