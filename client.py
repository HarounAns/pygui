# client.py

import socket
import sys
import json
from cache import values

size = 1024

def socketSend(msg, host, port):
    #print('message: ' + str(msg))
    # construct message dict and pickle
    msg = json.dumps(msg).encode()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #print('Host: ' + str(host) + ' Port: ' + str(port))
    s.connect((host, port))
    s.sendall(msg)
    data, addr = s.recvfrom(1024)
    data = data.decode()
    s.close()
    print ('Received from Server: "' + str(data) + '"')
    if str(data) == 'Tagged':
        return True