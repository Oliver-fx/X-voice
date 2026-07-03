import datetime
from socket import *
import threading
import time
import pyaudio
import numpy as np
import opuslib

CHUNK = 960
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
encoder = opuslib.Encoder(RATE, CHANNELS, opuslib.APPLICATION_VOIP)
socket = socket(AF_INET, SOCK_DGRAM)
p = pyaudio.PyAudio()

def sendingThread(data: str, serverAddr: str, portNum: int):
    stream_in = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, input_device_index=6, frames_per_buffer=CHUNK)
    while True:
        data = stream_in.read(CHUNK)
        encode = encoder.encode(data, CHUNK)
        socket.sendto(encode, (serverAddr, portNum))

def recievingThread():
    while True:
        recv_data, addr = socket.recvfrom(2048)
        #print(f'recieve data: {recv_data.decode()} timestamp: {datetime.datetime.now()}')


seq = 0

i = 0

message = f'client to server message {seq}'
t_send = threading.Thread(target=sendingThread, args=(message, 'localhost', 5500))
t_recv = threading.Thread(target=recievingThread)

#t_send.daemon = True
# t_recv.daemon = True

t_send.start()
t_recv.start()


#recv_message, addr = socket.recvfrom(2048)
#print(recv_message.decode() + "seq: ", seq)


