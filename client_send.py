from dataclasses import dataclass
from socket import *
import threading
import time
import pyaudio
import opuslib
import struct 
import secrets
import queue

CHUNK = 120
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000

@dataclass
class user_map:
    ip: str
    port: int
    ssrc: int

user_lookup: dict[int, user_map] = {}

recv_queue = queue.Queue(maxsize=20)

encoder = opuslib.Encoder(RATE, CHANNELS, opuslib.APPLICATION_VOIP)
decoder = opuslib.Decoder(RATE, CHANNELS)

p = pyaudio.PyAudio()

print("\n--- Available Audio Devices ---")
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    
    # Check if it's an Input (Mic) or Output (Speaker)
    device_type = ""
    if info['maxInputChannels'] > 0:
        device_type += "[MIC] "
    if info['maxOutputChannels'] > 0:
        device_type += "[SPEAKER]"
    
    print(f"Index {i}: {info['name']} {device_type}")
    print(f"   Max Channels: {info['maxInputChannels']} in / {info['maxOutputChannels']} out")
    print(f"   Default Sample Rate: {int(info['defaultSampleRate'])}Hz\n")

socket = socket(AF_INET, SOCK_DGRAM)

last_seq_num = 0

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
def init_rtp() -> bytes:
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

    return rtp_header

#TODO then we need to have update rtp for eveypacket, which updates the seq_num, and payload

def modify_rtp_header(base_rtp: bytes, data: bytes, seq_num: int) -> bytes:
    base_rtp = bytearray(base_rtp)

    base_rtp[2:4] = struct.pack('!H', seq_num)

    samples_size = CHUNK

    timestamp = struct.unpack('!I',base_rtp[4:8])[0]

    timestamp = (timestamp + samples_size) & 0xFFFFFFFF

    base_rtp[4:8] = struct.pack('!I', timestamp)

    return bytes(base_rtp) + encoder.encode(data, CHUNK)

# TODO check timestamp and seq num, and put them into a queue in the right order, 
# if lost more than 5-10 seq_num, print internet connection unstable, also check
# all the other field see wether it is sent by the right user, also this function
# will be extensible for the future stage
# function return, if true continue process the package, if false, drop the packet
def check_packet(rtp_packet: bytes, addr: tuple[str, int]) -> bool:
    global last_seq_num
    rtp_packet = bytearray(rtp_packet)

    # check if the seq_num is the right one
    seq_num = struct.unpack('!H', rtp_packet[2:4])[0]
    # change seq_num into deciaml form

    
    # drop the packet if current seq is less than lst seq
    if last_seq_num > seq_num:
        if last_seq_num >= 65535 and seq_num == 0:
            pass
        else:
            return False

    # print out error if current seq is greater than last seq a lot
    if seq_num > last_seq_num + 10:
        print('Network connection unstable: at least 10 packets have lost')

    last_seq_num = seq_num

    print(f'seq_num: {seq_num} last_seq_num: {last_seq_num}')

    # map the user id with ip addr
    # currently i just trust the packet, and do not verify the source
    # in the future stage, i will add verifying process before i put them into the user list

    ip = addr[0]
    port = addr[1]
    ssrc = struct.unpack('!I', rtp_packet[8:12])[0]

    if user_lookup.get(ssrc) == None:
        print(f'new user connected: {ssrc}')
        user_lookup[ssrc] = user_map(ip=ip, port=port, ssrc=ssrc)
    
    return True


def sendingThread(serverAddr: str, portNum: int):
    stream_in = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, input_device_index=6, frames_per_buffer=CHUNK)
    base_rtp = init_rtp()
    seq_num = 0

    while True:
        data = stream_in.read(CHUNK)

        data = modify_rtp_header(base_rtp, data, seq_num)

        #print(f'data size: {len(data)}')

        base_rtp = data[:12]

        socket.sendto(data, (serverAddr, portNum))

        seq_num = (seq_num + 1) % 65536



def recievingThread():

    while True:

        recv_data, addr = socket.recvfrom(CHUNK)

        check = check_packet(recv_data, addr)

        if check == False:
            continue
        else:
            recv_queue.put(recv_data)

def playing_thread():
    stream_out = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, output_device_index=6, frames_per_buffer=CHUNK)

    buffering = True

    while True:
        # jitter buffer
        if buffering == True:
            # if the packet in the queue is less than 5 packets, 
            # the program will sleep for few msec to let it accumulate
            if recv_queue.qsize() < 5:
                time.sleep(0.001)
                continue
            else:
                buffering = False
        try:
            # pop the data from the queue then play it
            recv_data = recv_queue.get(timeout=1.0)
            header = recv_data[:12]
            payload = recv_data[12:]

            decode = decoder.decode(payload, CHUNK)
            stream_out.write(decode)
        except queue.Empty:
            buffering = False
    

t_send = threading.Thread(target=sendingThread, args=('10.10.1.114', 5500))
t_recv = threading.Thread(target=recievingThread)
t_playing = threading.Thread(target=playing_thread)
#t_send.daemon = True
# t_recv.daemon = True

t_send.start()
t_recv.start()
t_playing.start()
