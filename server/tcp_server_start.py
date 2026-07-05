from dataclasses import dataclass
import json
from socket import *
import ssl
import os
import threading
import secrets
import base64
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CERT_PATH = os.path.join(BASE_DIR, "cert.pem")
KEY_PATH = os.path.join(BASE_DIR, "key.pem")
DEFAULT_IP = "0.0.0.0"
DEFAULT_PORT = 5062
SUCCESS_RETURN = 'ok'
MTU = 1024
UDP_SERVER_IP = "self define (str)"
UDP_SERVER_PORT = "self define (int)"

universal_count = 0


@dataclass
class user_detail:
    ssrc: int
    name: str
    s_socket: any


# user dictionary server will use this to coordinate new call
users: dict[int, user_detail] = {}
# name to ssrc dictonary
name_ssrc_lookup: dict[str, int] = {}
# ssrc to name dictonary
ssrc_name_lookup: dict[int, str] = {}

r_socket = socket(AF_INET, SOCK_STREAM)
r_socket.bind((DEFAULT_IP, DEFAULT_PORT))
r_socket.listen()

server_process = None

def handle_request(s_socket):
    global server_process
    global UDP_SERVER_PORT
    ssrc = None
    while True:
        try:
            raw_data = s_socket.recv(MTU)
            print(len(raw_data))

            if not raw_data:
                print("Client closed the connection")
                break

            data = raw_data.decode('utf-8')
            print(data)
        except (ConnectionResetError, OSError) as e:
            print(f"user disconnected: {e}")
            break
        # TODO design my own portocol, which has a header, easy for extension, and 
        # can carry a few common specific message
        
        # excxtract command, and then use match case to implement differnt functions
        if '\n' in data:
            command = data.split('\n', 1)[0]
            remaining_data = data.split('\n', 1)[1]
        else:
            message = "error\nno command\n"
            s_socket.sendall(message.encode('utf-8'))
            continue
        
        match command:
            # register logic
            case 'r':
                if '\n' in remaining_data:
                    raw_json = remaining_data.split('\n', 1)[0]

                try:
                    json_message = json.loads(raw_json)
                    name = json_message['name']
                    ssrc = json_message['ssrc']
                except (json.JSONDecodeError, KeyError) as e:
                    print("incorrect form sent to server, source unknown")
                    continue

                # if there is no srrc in the dict, store them into it
                if name_ssrc_lookup.get(name) == None:
                    print(f'new user "{name}" connected')
                    # register in three dictionaries
                    name_ssrc_lookup[name] = ssrc
                    ssrc_name_lookup[ssrc] = name
                    users[ssrc] = user_detail(ssrc=ssrc, name=name, s_socket=s_socket)
                    print(users)

                    message = "r\n"
                    message = message + SUCCESS_RETURN + '\n'

                    s_socket.sendall(message.encode('utf-8'))
                else:
                    message = "r\n"
                    message = message + "user already exist" + '\n'
                    s_socket.sendall((message).encode('utf-8'))
                    print('user already exist')
            # connection logic
            case 'c':
                # create a calling status for the second user
                second_user_status = False

                if '\n' in remaining_data:
                    raw_json = remaining_data.split('\n', 1)[0]
                try:
                    json_message = json.loads(raw_json)
                    dest_name = json_message['name']
                except (json.JSONDecodeError, KeyError) as e:
                    print("incorrect form sent to server, source unknown")
                    continue

                # checking for the user being called, and send calling request
                
                if name_ssrc_lookup.get(dest_name) == None:
                    message = "c\n"
                    message = message + "user is not registered to server" + '\n'
                    s_socket.sendall(message.encode('utf-8'))
                    continue

                dest_ssrc = name_ssrc_lookup.get(dest_name)
                dest_s_socket = users[dest_ssrc].s_socket
                origin_name = ssrc_name_lookup[ssrc]

                # check if the user is himself
                if origin_name == dest_name:
                    message = "c\n"
                    message = message + "you can't call yourself" + '\n'
                    s_socket.sendall(message.encode('utf-8'))
                    continue

                # send message to both user to inform them the current connection status
                message = "c\n"
                message = message + f"calling from {origin_name}" + '\n'

                dest_s_socket.sendall(message.encode('utf-8'))

                message = "c\n"
                message = message + f"waiting for {dest_name} to answer" + '\n'

                s_socket.sendall(message.encode('utf-8'))
            # accpet connection
            case 'ac':
                if '\n' in remaining_data:
                    raw_json = remaining_data.split('\n', 1)[0]
                try:
                    json_message = json.loads(raw_json)
                    dest_name = json_message['name']
                    status = json_message['status']
                except (json.JSONDecodeError, KeyError) as e:
                    print("incorrect form sent to server, source unknown")
                    continue
                
                if name_ssrc_lookup.get(dest_name) == None:
                    message = "c\n"
                    message = message + "user is not registered to server" + '\n'
                    s_socket.sendall(message.encode('utf-8'))
                    continue

                dest_ssrc = name_ssrc_lookup.get(dest_name)
                dest_s_socket = users[dest_ssrc].s_socket

                match status:
                    case "no_answer":
                        message = "ac\n"
                        message = message + "call not answered" + '\n'
                        dest_s_socket.sendall(message.encode('utf-8'))

                        message = "ac\n"
                        message = message + "you missed a call" + '\n'
                        s_socket.sendall(message.encode('utf-8'))
                    case "call_accept":
                        message = "ac\n"
                        message = message + "call accepted" + '\n'
                        dest_s_socket.sendall(message.encode('utf-8'))
                        print(message)
                    case "request_to_connect":
                        message = "ac\n"
                        message = message + "connecting" + '\n'

                        # send reuqest to connect to both client
                        dest_s_socket.sendall(message.encode('utf-8'))
                        s_socket.sendall(message.encode('utf-8'))

                    case "get_key":
                        # generate encryption key which is 30bytes
                        # 16 bytes/ 128bites for aes and 14 bytes as the salt
                        srtp_key = secrets.token_bytes(30)
                        # start to send encryption data
                        message = "ac\n"
                        message = message + "key\n" + base64.b64encode(srtp_key).decode('utf-8') + '\n'

                        dest_s_socket.sendall(message.encode('utf-8'))
                        s_socket.sendall(message.encode('utf-8'))

                    case "get_addr":
                        message = "ac\n"
                        message = message + "addr\n" + UDP_SERVER_IP + "\n" + str(UDP_SERVER_PORT) + '\n'

                        dest_s_socket.sendall(message.encode('utf-8'))
                        s_socket.sendall(message.encode('utf-8'))

                    case "spawn_udp_program":
                        message = "ac\n"
                        message = message + "spawn" + '\n'

                        dest_s_socket.sendall(message.encode('utf-8'))
                        s_socket.sendall(message.encode('utf-8'))

                        # spawn new udp program
                        universal_count += 1
                        UDP_SERVER_PORT = int(UDP_SERVER_PORT) + universal_count
                        server_process = subprocess.Popen(["python3", "udp_server.py", str(UDP_SERVER_PORT)])
                        print("udp_server is running")
                    case "disconnect":
                        server_process.kill()
                        server_process.wait()
                        server_process = None

                        print("udp server stopped")

                        message = "ac\n"
                        message = message + "disconnected" + '\n'

                        dest_s_socket.sendall(message.encode('utf-8'))
                        s_socket.sendall(message.encode('utf-8'))





    s_socket.close()
    if ssrc != None:
        if ssrc in users:
            del users[ssrc]
        if name in name_ssrc_lookup:
            del name_ssrc_lookup[name]
        if ssrc in ssrc_name_lookup:
            del ssrc_name_lookup[ssrc]
        print("user deleted")

def main():
    print("1")
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_3
    context.load_cert_chain(certfile=CERT_PATH, keyfile=KEY_PATH)

    print("server is starting")
    try:
        while True:
            try:
                client_sock, addr = r_socket.accept()
                s_socket = context.wrap_socket(client_sock, server_side=True)

                t = threading.Thread(target=handle_request, args=(s_socket,))
                t.start()
            except Exception as e:
                print(f"ERROR: {e}")
    except KeyboardInterrupt:
        print('\n(⌐■_■)Server is shutting down (⌐■_■)')
    finally:
        r_socket.close()

if __name__ == "__main__":
    main()