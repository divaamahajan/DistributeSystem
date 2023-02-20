import socket
import random

class User:
    list = ["Hello there!", "Well, I'm not hello!", "See you soon!"]
    
    def generate_message(self, value):
        if(value == '1'):
            msg = "Publisher\n"
            msg += random.choice(self.list)
        else:
            msg = "Subscriber\n"
        print(f"\nSending message to server : {msg}")
        return msg.encode(encoding='utf-8')

def start_client():
    HOST = '127.0.0.1'
    PORT = 8801
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    usr_input = ""
    while True:
        usr_input = input("\n[1]\tEnter 1 to be publisher\n[2]\tEnter 2 to be subscriber\n\n")
        if(usr_input < '1' or usr_input >'2'):
            print(f"\nIncorrect choice. Please select either 1 or 2.Retry")
        else:
            break
    node = User()
    client.connect((HOST,PORT))
    client.sendall(node.generate_message(usr_input))
    if(usr_input == '2'):
        data_recvd = client.recv(1024).decode()
        print(f"\nReceived message from broker:\t {data_recvd}")
    client.close()
    
if __name__ == "__main__":
    while True:
        start_client()
        c = input("\nPress 1 to continue or any other key to exit:\t")
        if(c != "1"):
            break