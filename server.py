#!/usr/bin/python

# the "gatekeeper".
# an attempt to implement Hybrid TCP-UDP Transport for Web Traffic by Cidon, Rom, Gupta, and Schuba
import socket

# Timestap print
def log(msg):
    from datetime import datetime
    print '[' + str(datetime.now()) + '] ' + msg

host = ''
port = 81
realPort = 80

tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.setblocking(0)
tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_sock.bind((host, port))
tcp_sock.listen(5)

udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.setblocking(0)
udp_sock.bind((host, port))

udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

log("Server started...")

while True:
    mode = ""
    data = ""
    
    try:
        data, addr = udp_sock.recvfrom(4096)
        if data != "":
            log("received UDP connection!")
            mode = "udp"
    except socket.error:
        pass
            
    try:
        sock, addr = tcp_sock.accept()
        data = sock.recv(4096)
        if data != "":
            mode = "tcp"
            log("received TCP connection!")
    except socket.error:
        pass

    if data != "":
        #print data, len(data)
        internal_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        internal_sock.connect((host, realPort))
        internal_sock.send(data)
        internal_sock.setblocking(1)
        log("data sent to web server")
        response = internal_sock.recv(4096*32)
        
        internal_sock.close()
        if mode == "udp":
            udp_client.connect((addr[0], port))
            if len(response) < 1460:
                udp_client.sendall(response)
            else:
                udp_client.sendall("USETCP")
                log("response to large, directed client to retry with TCP")
        elif mode == "tcp":
            sock.sendall(response)
            sock.close()
            
        
        
