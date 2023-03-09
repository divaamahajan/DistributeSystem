# from time import sleep
import socket
import threading
import sys
import os
import pandas as pd
import queue
import json

LISTEN_PORT = 8000
FORWARD_PORT = 8010
folder1 = 'CourseConnect'
HOST = 'localhost'
PACKET_SIZE = 4096
PUBCOLS = ['uname', 'startQuarter', 'term', 'planned']
SUBCOLS = ['uname','subscribe']

path = os.getcwd()
filepath = os.path.join(path, folder1 , "userInput.json")         
# create the lock
lock = threading.Lock()
       
def clientHandling(clientSock):
    sending_threads = []
    while True:        
        try:        
            # Recive request (packet) from client and decode
            clientRequest = clientSock.recv(PACKET_SIZE).decode()  
            # If no request recieved from client close connection and break
            if not clientRequest:  
                print(f"\nNo request recieved.")
                raise Exception
            df = pd.read_json(clientRequest)  
            print(f"Below message received:\n {df}")

            print(f"\n Executing Sender thread to forward the request to Computation Server's Port {FORWARD_PORT}....")
            send =threading.Thread(target= forwardData, args=(clientRequest,))
            send.start()
            sending_threads.append(send)
            print(f"\nSender thread execution complete")              
            # # send the response back to the client
            # clientSock.sendall(obj)
            
        except Exception as e:
            print(f"\nError in client handeling: {e}\nClosing client socket...\n")
            clientSock.close()
            break
        finally:
            #wait for sending threads to finish
            for t in sending_threads:
                t.join()
            print(f"\nClosing client socket...")
            clientSock.close()

def writeJsonToQueue(qName,json_obj, qList: queue.Queue()):
    
    data_queue = qList[0]
    # put each row of JSON object into the queue
    with lock:
        data_queue.put(json_obj)
        print(f"\nBelow object added to {qName} queue\n\t {json_obj} ")

def forwardData(receivedJson):
    try:  
        # create a list to keep track of all the threads
        threads = []
        json_list = json.loads(receivedJson)
        # list element is taken for refrencing objects as return      
        pubList, subList = [queue.Queue()], [queue.Queue()]
        
        for row in json_list:
            pub_dict = {k:v for (k,v) in row.items() if k in PUBCOLS and v is not None}
            if row.get('subscribe') is not None: #add only if user has subscribed
                sub_dict = {k:v for (k,v) in row.items() if k in SUBCOLS and v is not None}
            #start publishing Queue thread  
            pubThread =threading.Thread(target= writeJsonToQueue, args=("Pub", json.dumps(pub_dict), pubList,))
            pubThread.start()
            threads.append(pubThread) 

            #start Subscribing Queue thread
            subThread =threading.Thread(target= writeJsonToQueue, args=("Sub", json.dumps(sub_dict), subList,))
            subThread.start()  
            threads.append(subThread)          

        pubQueue, subQueue = pubList[0], subList[0]  
        print("\nBelow is the data of PubQ:\n\t") 
        print(*list(pubQueue.queue),sep='\t\n')
        print("\n\nBelow is the data of SubQ:\n\t") 
        print(*list(subQueue.queue),sep='\t\n')

        sendThread = threading.Thread(target= sendDatafromQueue, args=(pubQueue, subQueue,))
        # sendThread.daemon = True #daemon is set to ensure that the thread does not prevent the main program from exiting
        # start the reader thread
        sendThread.start()
        threads.append(sendThread)
        # wait for all threads to finish
        for t in threads: t.join()
        # # receive the response from the other port
        # response = forward_socket.recv(PACKET_SIZE)
    except Exception as e:
        print(f"\nError in forwarding data: {e}")

def sendDatafromQueue( pubQ, subQ):
    # forwarding socket is being closed inside the sendDatafromQueue function
    # wait for the pubQ to be empty
    while not pubQ.empty():
        with lock:
            obj = pubQ.get()
            print(f"\n\nforwarding Data:\n\t{obj}")
        send_data(FORWARD_PORT, obj)

    while pubQ.empty() and (not subQ.empty()):
        with lock:
            obj = subQ.get()
        send_data(FORWARD_PORT, obj)


def send_data(port,data):
    try:
        #Forward the contents of the queue to the Computational server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, port))
        sock.setblocking(1)		
        print(f"\n\nConnected to Computational server")
        sock.sendall(bytes(data,encoding="utf-8"))
        # sock.sendall(data.encode())
        print(f"\n\nBelow data is sent to CE: \n\t{data}")
    except (ConnectionResetError, BrokenPipeError, OSError) as e:
        print(f"Error sending data to CE {socket.getpeername()}: {e}")
    finally:
        sock.close()

def main():
    # listenPort = getArguments()
    listenPort = LISTEN_PORT
    print(f"The server is exposed to Port {listenPort}")

    #create a TCP socket | AF_INET : ipv4 | SOCK_STREAM : TCP protocol. 
    listenServSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # to rerun Python socket server on the same specific port after closing it once. 
    listenServSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    print(f"\nSocket successfully created")
    # bind host IP to the port
    try:
        listenServSock.bind((HOST, listenPort))
        print(f"Socket bound successfully to host {HOST}")
    except Exception as e:  # Exit if socket could not be bound to port
        print(f"Error: socket bound failure to port: {listenPort}")
        listenServSock.close()
        sys.exit(1)

    # accept incoming connections and forward the request to another port
    while True: 
        try:
            listenServSock.listen() # Listen for connections   
            print(f"\nServer is listening for connection on port {listenPort}...")
            clientSock, clientAddr = listenServSock.accept() # Establish the connection from client 
            print(f"\nconnection established from client {clientAddr}" )            
            print(f"\nExecuting listerner thread....")
            # # Create new thread for client request, and continue accepting connections
            listn =threading.Thread(target= clientHandling, args=(clientSock,))
            listn.start()
            listn.join()
            print(f"\nListner thread execution complete")
        except Exception as e:
            print(f"\nException in forever loop {e}\n. Closing client socket...")
            clientSock.close()
            break
        finally:
            print(f"\nClosing client socket...")
            clientSock.close()



if __name__ == '__main__':
    main()
