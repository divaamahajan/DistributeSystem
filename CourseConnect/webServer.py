import socket
import time
import threading

class ThreadServer(object):
    # create socket and bind host
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 9000))
    connection = client_socket.makefile('wb')    
    try:
        count = 1
        while True:
            data = 'from Motor: '
            client_socket.send(b'motor')
            time.sleep(1)
            count += 1
    finally:
        connection.close()
        client_socket.close()


if __name__ == '__main__':
    motor_thread = threading.Thread(target=motor_client('localhost',9003))
    motor_thread.start()
    ThreadServer()