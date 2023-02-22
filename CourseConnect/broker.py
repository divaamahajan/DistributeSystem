import random
from pubsub import MessageQueue
from time import sleep
import socket
import time
import threading
import signal
import sys
import argparse
import json
import os
import pandas as pd

folder1 = 'CourseConnect'
HOST = 'localhost'
PACKET_SIZE = 1024
path = os.getcwd()
filepath = os.path.join(path, folder1 , "userInput.json")

def getArguments():
    portNo, dirName = int(), ''
    parser = argparse.ArgumentParser()  # Initialize parser
    parser.add_argument("-port", "--portNo", help = "choose a portNo") # Adding optional argument
    args = parser.parse_args() # Read arguments from command line
    if not args.portNo: portNo =  8081
    else: portNo = int(args.portNo)
    return (portNo)

       
def clientHandling(clientSock):
    while True:        
        try:        
            # Recive request (packet) from client and decode
            clientRequest = clientSock.recv(PACKET_SIZE).decode()  
            # If no request recieved from client close connection and break
            if not clientRequest:  
                print(f"\nNo request recieved.")
                raise Exception
            df = pd.read_json(filepath)    
            
            
        except FileNotFoundError:
            print(f"File Not Found")
        except Exception:
            print(f"\nClosing client socket...")
            clientSock.close()
            break
def main():
    portNo = getArguments()
    print(f"The server is exposed to Port {portNo}")

    #create a TCP socket | AF_INET : ipv4 | SOCK_STREAM : TCP protocol. 
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # to rerun Python socket server on the same specific port after closing it once. 
    serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    print(f"\nSocket successfully created")
    # bind localhost IP to the port
    try:
        serverSock.bind((HOST, portNo))
        print(f"Socket bound successfully to host {HOST} and port {portNo}")
    except Exception as e:  # Exit if socket could not be bound to port
        print(f"Error: socket bound failure to port: {portNo}")
        serverSock.close()
        sys.exit(1)

    # Forever loop until interrupted/ error: 
    while True: 
        try:
            serverSock.listen() # Listen for connections   
            print(f"\nServer is listening for connection...\n")         
            clientSock, clientAddr = serverSock.accept() # Establish the connection from client 
            print(f"\nconnection established from client {clientAddr}" )
            # clientHandling(clientSock) #Single thread
            # Create new thread for client request, and continue accepting connections
            t = threading.Thread(target= clientHandling, args=(clientSock,))
            t.start()
        except Exception:
            print(f"\nException in forever loop. Closing client socket...")
            clientSock.close()
            break


if __name__ == '__main__':
    main()
