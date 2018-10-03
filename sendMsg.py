# sendMsg.py
import sys
import socket
import json

host = sys.argv[2]
port = int(sys.argv[4])
message = sys.argv[6]

if message == 'tag':
    msg = {
            "type": "rover",
            "text": "Chased Rover Tagged",
            "code": 'T',
        }
else:
    msg = {
            "type": "rover",
            "text": message,
            "code": 'M',
        }

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))

# construct message dict and pickle
print ('message from send message')
print (msg)
msg = json.dumps(msg).encode()
s.sendall(msg)
# data, addr = s.recvfrom(1024)
# data = data.decode()
s.close()

