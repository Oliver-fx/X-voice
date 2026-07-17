# X-voice
**Starts from socket, the blue print is to make a low-latency, high-encryption, and zero-knowledge voice chat app** 

**Version**: v0.1 Early testing version    
&emsp;&emsp;&emsp;&emsp;|__ Basic calling functionality, starting page designed, secondary page for testing purpose  

**Release**: v0.1 Eraly testeing version (only supports Windows) 

## Quick start
### **Development environment**  
- OS: Debian & MacOS
- Python: Python 3.13 | 3.14
- Additional Libraries: python-eel, pyaudio, opuslib, pylibsrtp

### **Setup**  
Once your python environment includes all the libraries listed above, you can start running the program using the following commands:

**Windows**:&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;**MacOS | Linux**:  
`python app.py`&emsp;&emsp;&emsp;&emsp;`python3 app.py`  


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
