from socket import *
import sys
import time

if len(sys.argv) > 2:
    port = int(sys.argv[2])
    ipAddr = sys.argv[1]
else:
    print("error you need to input server ip addr and port")

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(0.6)

server = (ipAddr, port)

sequenceNum = 10000
timestamp = time.time()

successArr = []

globalStart = 0
globalEnd = 0

#send message to server
i = 0
while i < 15:
    message = f"Ping {sequenceNum} {timestamp}"
    try:
        if (i == 0):
            globalStart = time.time()
        startTime = time.time()
        clientSocket.sendto(message.encode('utf-8'), server)
        recvMsg, serverAddr = clientSocket.recvfrom(2048)
        globalEnd = time.time()
        endTime = time.time()
        rtt = endTime - startTime
        print(f"PING to {ipAddr}, seq={sequenceNum}, rtt={rtt} ms")
        successArr.append(rtt)
    except:
        print(f"PING to {ipAddr}, seq={sequenceNum}, rtt=timeout")
    sequenceNum += 1
    i += 1

packetLost = ((15 - len(successArr)) / 15) * 100

rttMax = max(successArr)
rttMin = min(successArr)
rttAvg = sum(successArr) / len(successArr)
totalTransTime = abs(globalStart - globalEnd)

jitterNumerator = 0
for j in  range(1, len(successArr)):
    jitterNumerator += abs(successArr[j] - successArr[j-1])
jitter = jitterNumerator / (len(successArr) - 1)

print(f"Packet loss: {packetLost}%")
print(f"Minimum RTT: {rttMin} ms, Maximum RTT: {rttMax} ms, Average RTT: {rttAvg} ms")
print(f"Total transmission time: {totalTransTime} ms")
print(f"Jitter: {jitter} ms")