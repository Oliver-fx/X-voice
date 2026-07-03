import datetime
from socket import *
#import socket
import threading

#STAGE 1 TESTING, in this stage i am trying to handle differnt users connecting to server
# and send back the data recieved from user.
client_list = []

def multiple_user(data: bytes, clientAddr: tuple):
    #message = f"message from {clientAddr} to others"
    #print('new user is connecting')
    if clientAddr not in client_list:
        client_list.append(clientAddr)
        print('append succced')
    for addr in client_list:
        if (addr != clientAddr):
        #socket.sendto(data, addr)
            socket.sendto(data, addr)



PORT = 5500

socket = socket(AF_INET, SOCK_DGRAM)

socket.bind(('0.0.0.0', PORT))


print('server is starting')

while 1:
    data, clientAddr = socket.recvfrom(2048)

    multiple_user(data, clientAddr)
    print(f'recieved audio {datetime.datetime.now()}')
    
    #socket.sendto(message.encode(), clinetAddr)
socket.close()


