# server.py

import sys
import socket
import json
from cache import values 
import _thread as thread
import time
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client.roverMessages

def on_new_client(clientsocket,addr):
    while True:
        data = clientsocket.recv(1024) 

        if not data:
            break

        #do some checks and if data == someWeirdSignal: break:
        print (addr, ' >> ', data)

        # parse data and return response
        data = json.loads(data.decode())

        # if data sent is 'waiting for rover signal'
        if data["code"] == 'W':
            while 1:
                time.sleep(1)
                if db.roverMessages.find_one():
                    print(db.roverMessages.find_one())
                    db.roverMessages.remove({})
                    response = 'Tagged'
                    break
        # pause the thread until it receives a rover type message

        elif data["code"] == 'S':
            response = 'Starting Rovers'

        elif data["code"] == 'R':
            response = 'Resetting Rovers'

        elif data["code"] == 'P':
            response = 'Pausing Rovers'

        elif data["code"] == 'M':
            response = data["text"]

        elif data["code"] == 'T':
            response = data["text"]
        
        else:
            response = 'Unrecognized Message'
        
        if clientsocket:
            response = response.encode()
            clientsocket.send(response) 
    clientsocket.close()


host = ''
port = int(sys.argv[2])
size = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to the host (this server) and to a predefined port from command line
s.bind((host, int(port)))
print('binding to port: ' + str(port) + ' and host: ' + str(host))

# wait for incoming connections from clients
s.listen(size)
while 1:
    c, addr = s.accept()     # Establish connection with client.
    thread.start_new_thread(on_new_client,(c,addr))
s.close()


#     #accept the client connection
#     client, address = s.accept()

#     data = client.recv(int(size))
#     if not data:
#         break
    
#     # parse data and return response
#     data = json.loads(data.decode())
    
#     if data["code"] == 'S':
#         response = 'Starting Rovers'

#     elif data["code"] == 'R':
#         response = 'Resetting Rovers'

#     elif data["code"] == 'P':
#         response = 'Pausing Rovers'

#     response = response.encode()
#     client.sendall(response)
# client.close()    