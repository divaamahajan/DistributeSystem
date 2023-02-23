
import socket
import os
import json
import pandas as pd

HOST, PORT = "localhost", 8000
path = os.getcwd()
json_filepath = os.path.join(path, "CourseConnect", "userInput.json")
with open(json_filepath) as json_file:
    data = (json.load(json_file))
data = json.dumps(data)
print(type(data))
print(data)

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    print("connected to server")
    sock.sendall(bytes(data,encoding="utf-8"))
    print("data sent")


    # # Receive data from the server and shut down
    # received = sock.recv(1024)
    # received = received.decode("utf-8")

finally:
    sock.close()