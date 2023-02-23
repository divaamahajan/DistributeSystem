import sys
import socket
import threading
import pandas as pd

HOST = 'localhost'
portNo = 8010
PACKET_SIZE = 4086



def clientHandling(clientSock):
    while True:        
        try:        
            print("Handeling client..")
            # Recive request (packet) from client and decode
            clientRequest = clientSock.recv(PACKET_SIZE)
            # If no request recieved from client close connection and break
            print("Check clientRequest data....")
            if not clientRequest:  
                print(f"\nNo request recieved.")
                raise Exception
            print(f"\nPacket received:{clientRequest}\n*******************\n")
            clientRequest = clientRequest.decode()
            print("Request received\n\tProcessing....")
            df = pd.read_json(clientRequest)  
            print(f"Below message received:\n {df}")

        except Exception:
            print(f"\nClosing client socket...")
            clientSock.close()
            break
        finally:
            print(f"\nClosing client socket...")
            clientSock.close()

if __name__ == "__main__":
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
        finally:
            print(f"\nClosing client socket...")
            clientSock.close()