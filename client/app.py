import base64
import threading

import eel
import secrets
from socket import *
import ssl
import os
import sys
import json
import subprocess
import time

#'170.64.145.153'
SERVER_IP = 'localhost'
SERVER_PORT = 5063

MTU = 1024

# global var that always stores the ssrc
ssrc: int = secrets.randbits(32)

r_socket = socket(AF_INET, SOCK_STREAM)

context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)

context.minimum_version = ssl.TLSVersion.TLSv1_3

context.check_hostname = True

# get CA from current dir
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CERT_PATH = os.path.join(BASE_DIR, "cert.pem")
context.load_verify_locations(cafile=CERT_PATH)
dest_name = ''

tls_socket = context.wrap_socket(r_socket, server_hostname=SERVER_IP)
try:
    tls_socket.connect((SERVER_IP, SERVER_PORT))
    print("sever connect successfully")
except Exception as e:
    print(f"Could not connect to server. error: {e}")

# helper function 
def register_json_m(name: str) -> str:
    json_message = {
        "name": name,
        "ssrc": ssrc
    }
    json_packet = json.dumps(json_message, separators=(',', ':')) + '\n'

    return json_packet

def connection_json_m(name:str) -> str:
    global dest_name
    dest_name = name
    json_message = {
        "name": dest_name
    }
    json_packet = json.dumps(json_message, separators=(',', ':')) + '\n'

    return json_packet

def answer_call_json_m(status:str) -> str:
    json_message = {
        "name" : dest_name,
        "status": status
    }
    json_packet = json.dumps(json_message, separators=(',', ':')) + '\n'

    return json_packet

@eel.expose
def user_input(command, input) -> str:
    match command:
        case 'r':
            message = "r\n"
            message = message + register_json_m(input)
            tls_socket.sendall(message.encode('utf-8'))
        case 'c':
            message = "c\n"
            message = message + connection_json_m(input)
            print(message)
            tls_socket.sendall(message.encode('utf-8'))
        case 'ac':
            message = "ac\n"
            message = message + answer_call_json_m(input)
            tls_socket.sendall(message.encode('utf-8'))
            print(message)

client_process = None

@eel.expose
def recv_thread():
    global client_process
    global dest_name
    while True:
        raw_data = tls_socket.recv(MTU)

        if not raw_data:
            print("server disconnected")

        data = raw_data.decode('utf-8')

        if '\n' in data:
            command = data.split('\n', 1)[0]
            remaining_data = data.split('\n', 1)[1]

        match command:
            case 'r':
                if '\n' in remaining_data:
                    server_msg = remaining_data.split('\n', 1)[0]
                
                if server_msg == 'ok':
                    # send ok to ui js
                    eel.displayRegistrationResult(server_msg)
                else:
                    print(f'error from server: {server_msg}')
                    eel.displayRegistrationResult(f'error: {server_msg}')
            case 'c':
                if '\n' in remaining_data:
                    server_msg = remaining_data.split('\n', 1)[0]

                match server_msg:
                    case "user is not registered to server":
                        eel.displayConnectionResult(server_msg)
                    case server_msg if "calling from" in server_msg:
                        dest_name = server_msg.replace("calling from ", "")
                        print(server_msg)
                        eel.displayConnectionResult(server_msg)
                    case server_msg if "waiting for" in server_msg:
                        print(server_msg)
                        eel.displayConnectionResult(server_msg)
                    case "you can't call yourself":
                        print(server_msg)
                        eel.displayConnectionResult(server_msg)
            case 'ac':
                if '\n' in remaining_data:
                    server_msg = remaining_data.split('\n', 1)[0]

                match server_msg:
                    case "call not answered":
                        print(server_msg)
                        eel.displayCallingStatus(server_msg)
                        dest_name = ''
                    case "you missed a call":
                        print(server_msg)
                        eel.displayCallingStatus(server_msg)
                        dest_name = ''
                    case "call accepted":
                        print(server_msg)
                        eel.displayCallingStatus(server_msg)
                    case "connecting":
                        print(server_msg)
                        eel.displayCallingStatus(server_msg)
                    case "key":
                        print("key recieved")
                        # get key from the data
                        server_msg, base64_section = remaining_data.split('\n', 1)
                        base64_key = base64_section.split('\n', 1)[0]
                        srtp_key = base64.b64decode(base64_key.encode('utf-8'))
                        print(srtp_key)
                        eel.displayCallingStatus(server_msg)
                    case "addr":
                        print("addr recieved")
                        server_msg, udp_ip, udp_port = remaining_data.split('\n', 2)
                        udp_ip = udp_ip.split('\n', 1)[0]
                        udp_port = udp_port.split('\n', 1)[0]
                        print(f"addr: {udp_ip}, {udp_port}")
                        eel.displayCallingStatus(server_msg)
                    case "spawn":
                        print("spawning udp program")
                        eel.displayCallingStatus(server_msg)
                        print("new udp client is running at background")
                        
                        #convert srtp key into hex form and pass it in to the subprocess
                        srtp_key_hex = srtp_key.hex()
                        client_process = subprocess.Popen(["python3", "client.py", srtp_key_hex, udp_ip, udp_port])
                        
                        if client_process.poll() == None:
                            msg = "connected"
                            eel.displayCallingStatus(msg)

                        # while True:
                        #     if process.poll() != None:
                        #         print("UDP chatting ended: could be bug or intensional")
                        #         break
                        #     time.sleep(1)
                        # msg = "disconnected"
                        # eel.displayCallingStatus(msg)
                    case "disconnected":
                        print("server is down")
                        client_process.kill()
                        client_process.wait()
                        client_process = None
                        
                        eel.displayCallingStatus(server_msg)

eel.init('ui')

t_recv = threading.Thread(target=recv_thread)
t_recv.daemon = True
t_recv.start()

eel.start('index.html', mode='chrome', size=(700,500), port=0)
#'index.html',