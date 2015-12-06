#!/usr/bin/python

# the "gatekeeper".
# an attempt to implement Hybrid TCP-UDP Transport for Web Traffic by Cidon, Rom, Gupta, and Schuba
import socket
import sys
import select

# timestamp logging
def log(msg):
    from datetime import datetime
    print '[' + str(datetime.now()) + '] ' + msg
            

if len(sys.argv) < 2:
    print "Usage: python client.py [remote host address] [-usetcp]"
    sys.exit()

host = ''
remote = sys.argv[1]
port = 82
remotePort = 81

udp_receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_receiver.setblocking(0)
udp_receiver.bind((host, remotePort))

udp_connector = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_connector.connect((remote, remotePort)) 

log("Client proxy started...")

tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.bind((host, port))
tcp_socket.listen(5)

permmode = ''
if len(sys.argv) > 2 and '-usetcp' in sys.argv:
    log("TCP only client mode")
    permmode = 'tcp'

while True:
    mode = ''
    data = ''
    
    try:        
        sock, addr = tcp_socket.accept()
        data = sock.recv(4096)
        log('Data received...')
        if data:
            response = ''
            if permmode == 'tcp':
                mode = 'tcp'
            else:
                mode = "udp"
                udp_connector.send(data)
                ready = select.select([udp_receiver], [], [], socket.getdefaulttimeout())
                if ready[0]:
                    response = udp_receiver.recv(4096 * 32)
                    #print response
            if mode == "tcp" or not ready[0] or response.startswith('USETCP'): # use tcp
                if permmode == 'tcp':
                    log('Not using UDP...')
                log('Switching to TCP...')
                tcp_connector = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcp_connector.connect((remote, remotePort))
                tcp_connector.send(data)
                response = tcp_connector.recv(4096 * 32)

        sock.sendall(response)
        log('Sent response back to client browser')
        sock.close()                

    except socket.error:
        pass


        
