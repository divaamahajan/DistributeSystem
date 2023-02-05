import socket
import time
import threading
import signal
import sys
import argparse


HOST = "localhost"
PACKET_SIZE = 1024 # Number of bytes to read from client requests
# PORTNO = 8081 # Port server socket will be bound to, 80 is default port for http
VERSION_11 = '1.1'
VERSION_10 = '1.0'
DIRNAME = 'www.scu.edu'
OKPAGE = 'index.html'
HTMLpage = 'html'
imageType = ("jpg" , "jpeg" , "png", "css", "js", "json")


def serverShutdown(serverSock):
    print(f"\nServer shutting down ...")
    serverSock.close()
    sys.exit(1)

def getPortNo():
    parser = argparse.ArgumentParser()  # Initialize parser
    parser.add_argument("-port", "--portNo", help = "choose a portNo") # Adding optional argument
    args = parser.parse_args() # Read arguments from command line
    if not args.portNo: return 8081
    else: return args.portNo

def getRequest(clientSock):
    clientRequest, requestType, httpVersion = '','',''
    # Recive request (packet) from client and decode
    clientRequest = clientSock.recv(PACKET_SIZE).decode()  
    # If no request recieved from client close connection and break
    if not clientRequest:  
       print(f"\nNo request recieved.")
       raise Exception
    # Get request type and version from client request
    try:
       requestType = clientRequest.split(' ')[0]     
    #    httpVersion = clientRequest.split('/')[2][:3]
       httpVersion = clientRequest.split('HTTP/')[1][:3]
       print(f"\nRequest: {clientRequest}")
       print(f"\n\tMethod: {requestType} || HTTP Version: {httpVersion}")
    except Exception as e:
       print(f"\nError getting request clientRequest/requestType/http version/")
       raise Exception
    return (clientRequest, requestType, httpVersion)
    
def getFileDetails(clientRequest):
    fileType,filepath = '',''
    try:               
       fileRequested = clientRequest.split(' ')[1]   # GET /index.html (split on space)
       if fileRequested == "/": fileRequested = "/index.html" # / means request for the base html page 
       elif fileRequested[-1] == '/': fileRequested += 'index.html'      
       fileType = fileRequested.split('.')[1]  # Get filetype of request
       print(f"\nFile requested by client: " + fileRequested)
       print(f"\nFiletype of file: " + fileType)
    except Exception as e:
       print(f"\nError getting filetype/requested file")
    #    raise Exception

    filepath = DIRNAME + fileRequested  # Base page is in wget folder
    print(f"\nFilepath to serve: " + filepath + '\n')
    return(fileType,filepath)

# Generates http response headers based on http protocol version and response code
def createHeader(responseCode, httpVersion, fileType):
    header = ''
    try:        
        time_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        header += f'HTTP/{httpVersion} {responseCode}'
        if responseCode == 200: header += ' OK\n'
        elif responseCode == 404: header += ' Not Found\n'
        elif responseCode == 403: header += 'Forbidden\n'

        header += 'Date: ' + time_now + '\n'
        header += "Server: Divya Mahajan's Python Server\n"

        if httpVersion == VERSION_10: header += 'Connection: close\n'  
        elif httpVersion == VERSION_11: header += 'Connection: keep-alive\n'  

        if fileType == 'html': header += 'Content-Type: text/html\n\n'
        elif fileType in imageType: header += f'Content-Type: image/{fileType}\n\n'
        else:header += 'Content-Type: ' + fileType + '\n\n'
    except Exception:
        print("header could not be created for responseCode {responseCode}, httpVersion {httpVersion}, fileType {fileType}")
    return header

def parseHTMLpage(httpVersion, fileType, requestType, filepath):
    responseCode, responseData = int(),''
    try:
        if requestType == "GET":  # Only want to read if was GET request
            file = open(filepath, 'r')
            print("file opened")                     
            if filepath == DIRNAME + '/'+ OKPAGE : 
                responseData = file.read()
                responseCode = 200 # Make 200 OK response
            else: responseCode = 403 # Make 403 permission denied response
            file.close()
        
    except Exception:  # If exception is thrown by attempting to open file that doesnt exist
        print(f"\nFile not found, serving 404 file not found response")      # Make 404 file not found response
        responseCode = 404
    return (createHeader(responseCode, httpVersion, fileType), responseCode, responseData)


def parseImages(httpVersion, fileType, requestType, filepath):
    responseHeader, responseCode, responseData = '', int(),''
    try:
       if requestType == "GET":  # Only want to read if was GET request
          file = open(filepath, 'rb')  # Open image in bytes format
          responseData = file.read()
          file.close()
       responseHeader = createHeader(200, httpVersion, fileType)  # Make 200 OK response
       responseCode = 200
    except Exception:  # If exception is thrown by attempting to open file that doesnt exist
       print(f"\nImage not found/couldn't be opened, serving 404 file not found response")
       responseHeader = createHeader(404, httpVersion, fileType)  # Make 404 file not found response
       responseCode = 404    
    return (responseHeader, responseCode, responseData)
       
def clientHandling(clientSock):
    persistent = False
    while True:        
      try:        
         clientRequest, requestType, httpVersion = getRequest(clientSock)

         # Set the socket to timeout after 10 seconds if http version is 1.1 (persistent connection)
         if httpVersion == VERSION_11 and not persistent:
            persistent = True
            clientSock.settimeout(10)

         # valid requests
         if requestType == "GET" or requestType == "HEAD":
            fileType,filepath = getFileDetails(clientRequest)

            # Attempt to load and serve file content
            # If just serving a html file
            if fileType == HTMLpage:
                responseHeader, responseCode, responseData = parseHTMLpage(httpVersion, fileType, requestType, filepath)
            # Else if trying to serve up an image
            elif fileType in imageType:
               responseHeader, responseCode, responseData = parseImages(httpVersion, fileType, requestType, filepath)
            # Else trying to request/open an invalid file type
            else:
               print(f"\nInvalid requested filetype: " + fileType)
               responseHeader = createHeader(404, httpVersion, fileType)
            
            # If request was GET and requested file was read successfully, append the file to the response header
            if (fileType == HTMLpage or fileType in imageType) and requestType == "GET" and responseCode == 200:
                print(f"\nSending: \n" + responseHeader + responseData)
                # Encode the response in bytes format so can be sent to client
                clientSock.send(responseHeader.encode() + responseData.encode())
            # Else simply return the response header (HEAD request - 200/404)
            else:
                print(f"\nSending: \n" + responseHeader)
                clientSock.send(responseHeader.encode())
            # If http version 1.0, want to close connection after completing request
            if httpVersion == VERSION_10: raise Exception
            # Else if http version 1.1, want to keep persistent connection after completing request
            elif httpVersion == VERSION_11 and persistent == True:
               print(f"\nhttp 1.1: peristent connection, continuing to recieve requests...")
         # else invalid request, error and close
         else:
            print(f"\nError: Unknown HTTP request method: " + requestType)  # 501 Not Implemented
            raise Exception
      except FileNotFoundError:
            print(f"File Not Found : {fileType}")
            responseHeader = createHeader(404, httpVersion, fileType)
            print(f"Sending: \n \t {responseHeader}")
            clientSock.send(responseHeader.encode())
            print(f"\nClosing client socket...")
            clientSock.close()
            break
      # Exception is thrown once the socket connection times out (http 1.1 - persistent connection)
      except socket.timeout:
         print(f"\nSocket connection timeout reached (10 seconds)")
         print(f"\nClosing client socket...")
         clientSock.close()
         break
      except Exception:
         print(f"\nClosing client socket...")
         clientSock.close()
         break
    
    print(f"\nClient handeled, Closing client socket...")
    clientSock.close()


# if __name__ == "__main__":
# Interrupt from keyboard (CTRL + C).Default action is to raise KeyboardInterrupt.
signal.signal(signal.SIGINT, serverShutdown)
portNo = getPortNo()
print(f"go to link: http://localhost:{portNo}")

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