from collections import deque
import sys
import socket

class Message:
    q = deque()
    def check_queue_data(self):
        if(len(self.q) > 0):
            return True
        else:
            return False
    def add_message(self, message):
        self.q.append(message)
    
    def get_message(self):
        return self.q.popleft()

def start_server():
    HOST = '127.0.0.1'
    PORT = 8801
    try:
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        # listener.setblocking(False)
    except:
        print(f"\nError while creating socket.\nShutting down.....")
        sys.exit()
    
    try:
        listener.bind((HOST,PORT))
    except:
        print(f"\nError while binding socket.\nShutting down ....")
        sys.exit()
    print(f"\nBroker Ready, listening on {HOST}:{PORT} ....\nDefault Queue size is 10\n")
    
    Broker = Message()
    
    while True:
        listener.listen()
        clientSock, clientAddr = listener.accept()
        pub_and_sub(clientSock, Broker)
        clientSock.close()
        
def pub_and_sub(client, msg_Broker):
    request = client.recv(1024).decode()
    message = request.split("\n")
    if(message[0] == 'Publisher'):
        msg_Broker.add_message(message[1])
    else:
        pass_message = "Sorry no message available in the queue"
        if(msg_Broker.check_queue_data()):
            pass_message = msg_Broker.get_message()
            print(f"\nMessage passed to subscriber:\n{pass_message}")
        else:
            print(f"\nSorry no message available in the queue\n")
        client.sendall(pass_message.encode(encoding='utf-8'))
    
if __name__ == "__main__":
    start_server()