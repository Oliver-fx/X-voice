from socket import *
import threading
import time
import pyaudio
import opuslib

CHUNK = 120
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000


encoder = opuslib.Encoder(RATE, CHANNELS, opuslib.APPLICATION_VOIP)
decoder = opuslib.Decoder(RATE, CHANNELS)

p = pyaudio.PyAudio()

socket = socket(AF_INET, SOCK_DGRAM)

glo_start = 0
glo_end = 0
def sendingThread(serverAddr: str, portNum: int):
    stream_in = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, input_device_index=6, frames_per_buffer=CHUNK)
    global glo_start
    while True:
        glo_start = time.time()
        data = stream_in.read(CHUNK)
        encode = encoder.encode(data, CHUNK)
        socket.sendto(encode, (serverAddr, portNum))



def recievingThread():
    stream_out = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, output_device_index=6, frames_per_buffer=CHUNK)
    global glo_end
    while True:
        recv_data, addr = socket.recvfrom(CHUNK)
        decode = decoder.decode(recv_data, CHUNK)
        stream_out.write(decode)
        glo_end = time.time()
        print(f"total time: {glo_end - glo_start}")

    

t_send = threading.Thread(target=sendingThread, args=('localhost', 5500))
t_recv = threading.Thread(target=recievingThread)

#t_send.daemon = True
# t_recv.daemon = True

t_send.start()
t_recv.start()

