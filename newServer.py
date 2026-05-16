import datetime
from socket import *
#import socket
import threading
from queue import Queue
from dataclasses import dataclass
import time
from typing import List

#STAGE 1 TESTING, in this stage i am trying to handle differnt users connecting to server
# and send back the data recieved from user.

#STAGE2 TESTING And OPTIMZING according to the last stage, i found there is a delay issue when
# the program is running.
# So I changed the logic on how to build the server, I used to build a blocking server, which
# runs sending and recieving process in a static order in a while loop. This stage, I put sending and 
# recieveing process into two threads, each thread can now do their own thing without blocking
# others. Technically, the speed on server side would increased a lot. And i added a user dead 
# check, in order to make sure the server just sends the data to users that sends data to server
# in last 5 seconds

@dataclass
class QueueData:
    data: bytes = None
    clientAddr: tuple = None

@dataclass
class Client:
    clientAddr: tuple = None
    timestamp: float = None

client_list: List[Client] = []
client_list_lock = threading.Lock()
q = Queue(maxsize=0)

PORT = 5500
TIMEOUT = 3

socket = socket(AF_INET, SOCK_DGRAM)

socket.bind(('0.0.0.0', PORT))


print('server is starting')

def sendingThread():
    while 1:
        if (q.qsize() > 0):
            queObj:QueueData = q.get()
            clientAddr = queObj.clientAddr
            data = queObj.data
            with client_list_lock:
                exist = any(obj.clientAddr == clientAddr for obj in client_list)

                if not exist:
                    # construct ClientOBJ
                    c_obj = Client(clientAddr=clientAddr, timestamp=time.time())
                    client_list.append(c_obj)
                    print('append succced')
                print(client_list)

                for obj in client_list:
                    addr = obj.clientAddr
                    if (addr != clientAddr):
                        socket.sendto(data, addr)
                    elif addr == clientAddr:
                        obj.timestamp = time.time()
                        # !!! FOR TESTING CHANGE THIS LINE LATER
                        #socket.sendto(data, addr)
        # else:
        #     client_list[:] = []

def recievingThread():
    check_time = time.time()
    while 1:
        data, clientAddr = socket.recvfrom(2048)
        #print(f"recieve from{clientAddr}")
        #construct queue object
        queObj = QueueData(data=data, clientAddr=clientAddr)

        #put into the queue
        q.put(queObj)


def check_timeout():
    while True:
        time.sleep(10)
        curr_time = time.time()

        with client_list_lock:
            active:List[Client] = []
            timeout:List[Client] = []
            
            for c in client_list:
                if (curr_time - c.timestamp) >= TIMEOUT:
                    timeout.append(c)
                else:
                    active.append(c)
            
            client_list[:] = active

            timeout.clear()

send = threading.Thread(target=sendingThread)
recieve = threading.Thread(target=recievingThread)

send.daemon = True
recieve.daemon = True

send.start()
recieve.start()

send.join()
recieve.join()

socket.close()
