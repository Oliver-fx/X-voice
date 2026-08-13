# X-voice
**Starts from socket, the blue print is to make a low-latency, high-encryption, and zero-knowledge voice chat app** 

**Version**: v 0.1 Early testing version    
&emsp;&emsp;&emsp;&emsp;&emsp;|__ Basic calling functionality, starting page designed, secondary page for testing purpose  

**Release**: v 0.1 Eraly testeing version (only supports Windows) 

## Quick start
### **Development environment**  
- OS: Debian & MacOS
- Python: Python 3.13 | 3.14
- Additional Libraries: python-eel, pyaudio, opuslib, pylibsrtp

### **Setup**  
Install Python dependencies:
`pip install -r requirements.txt`  

Once your python environment includes all the libraries listed above, you can start running the program using the following commands:

**Windows**:&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;**MacOS | Linux**:  
`python app.py`&emsp;&emsp;&emsp;&emsp;`python3 app.py`  

**Server SSL Setup**  
IMPORTANT MUST GENERATE FOLLOWING FILES ON YOUR SERVER  
Generate the key.pem file:  
`openssl genrsa -out key.pem 2048` 
  
Generate the cert.pem file using previous generated key.pem:  
`openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout key.pem -out cert.pem -subj "/CN=yourIP" -addext "subjectAltName=IP:yourIP"`  
  
Place your server generated cert.pem into the client folder, run your server and you are good to go!  

## Architecture
**Stage 1 and Stage 2 are early stages. It is there to show the history of this project. Because they were primarily developed for experimental and testing purposes, they contains a few perfomance limitations.**  

### **Current Version**  
```text
/client
      |__ ui
      |    |__ index.html         # secondary page
      |    |__ startPage.html     # entry page
      |    |__ script.js
      |    |__ style.css
      |__ app.py                  # backend of the client side
      |__ client.py               # UDP voice chatting client
      |__ cert.pem                # create from your own server
/server
      |__ tcp_server_start.py     # handles all the client side requests
      |__ udp_server.py           # UDP voice chatting server
```
