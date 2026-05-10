from socket import *
import threading
import time
import pyaudio
import opuslib
import struct 
import secrets

CHUNK = 120
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000


encoder = opuslib.Encoder(RATE, CHANNELS, opuslib.APPLICATION_VOIP)
decoder = opuslib.Decoder(RATE, CHANNELS)

p = pyaudio.PyAudio()

socket = socket(AF_INET, SOCK_DGRAM)

'''
0                   1                   2                   3
0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|V=2|P|X|  CC   |M|     PT      |       sequence number         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                           timestamp                           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|           synchronization source (SSRC) identifier            |
+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+
|            contributing source (CSRC) identifiers             |
|                             ....                              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
'''
# wrap the bytes data into rtp protocol, and send using udp
def init_rtp(data: bytes):
    # construct first row
    version = 0b10
    padding = 0b0
    extension = 0b0
    CSRC = 0B0000
    marker = 0b0
    payload_type = 0b1100100
    seq_num = 0b0000000000000000

    byte1 = (version << 6) | (padding << 5) | (extension << 4) | CSRC
    byte2 = (marker << 7) | payload_type

    # construct timestamp 32 bits long
    timestamp = 0

    # construct unique indentifier
    ssrc = secrets.randbits(32)

    # construct csrc, since the server can handle the broadcasting process, 
    # so I delete the csrc row entirely, the overall size of the header is 12 bytes
    rtp_header = struct.pack('!BBHII', byte1, byte2, seq_num, timestamp, ssrc)
    #TODO add first packet to after the rtp header

#TODO then we need to have update rtp for eveypacket, which updates the seq_num, and payload

def sendingThread(serverAddr: str, portNum: int):
    stream_in = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, input_device_index=6, frames_per_buffer=CHUNK)

    while True:

        data = stream_in.read(CHUNK)
        encode = encoder.encode(data, CHUNK)
        socket.sendto(encode, (serverAddr, portNum))



def recievingThread():
    stream_out = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, output_device_index=6, frames_per_buffer=CHUNK)

    while True:

        recv_data, addr = socket.recvfrom(CHUNK)
        decode = decoder.decode(recv_data, CHUNK)
        stream_out.write(decode)


    

t_send = threading.Thread(target=sendingThread, args=('localhost', 5500))
t_recv = threading.Thread(target=recievingThread)

#t_send.daemon = True
# t_recv.daemon = True

t_send.start()
t_recv.start()

