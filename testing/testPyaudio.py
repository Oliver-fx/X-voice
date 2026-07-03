import time
import pyaudio
import numpy as np

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHNNELS = 1
RATE = 44100

p = pyaudio.PyAudio()

for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(i, info['name'], info['maxInputChannels'], info['maxOutputChannels'])

time1 = time.time()

frame = []
stream_in = p.open(format=FORMAT, channels=CHNNELS, rate=RATE, input=True, input_device_index=6)
while time.time() - time1 < 3:
    data = stream_in.read(CHUNK)
    frame.append(data)

print('stop recording')
stream_in.stop_stream()
stream_in.close()

stream_out = p.open(format=FORMAT, channels=1, rate=44100, output=True, output_device_index=6)
for data in frame:
    audio = np.frombuffer(data, dtype=np.int16)
    audio = (audio * 0.5).astype(np.int16)
    stream_out.write(audio.tobytes())
stream_out.stop_stream()
stream_out.close()
print('stop playing')
