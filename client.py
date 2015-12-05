#!/usr/bin/python

# the "gatekeeper".
# an attempt to implement Hybrid TCP-UDP Transport for Web Traffic by Cidon, Rom, Gupta, and Schuba
import socket
import sys
import select

host = ''
remote = 'golf620-linux.local'
port = 82
remotePort = 81

udp_receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_receiver.setblocking(0)
udp_receiver.bind((host, remotePort))

udp_connector = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_connector.connect((remote, remotePort)) 

print "Client proxy started..."

tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.bind((host, port))
tcp_socket.listen(5)

permmode = ''
if len(sys.argv) > 1:
    print 'tcp only client mode'
    permmode = 'tcp'

while True:
    mode = ''
    data = ''
    
    try:        
        sock, addr = tcp_socket.accept()
        data = sock.recv(4096)
        print data
        if data:
            response = ''
            if permmode == 'tcp':
                mode = 'tcp'
            else:
                mode = "udp"
                udp_connector.send(data)
                ready = select.select([udp_receiver], [], [], tcp_socket.getdefaulttimeout())
                if ready[0]:
                    response = udp_receiver.recv(4096 * 32)
                    print response
            if mode == "tcp" or not ready[0] or response.startswith('USETCP'): # use tcp
                if permmode == 'tcp':
                    print 'not using UDP...'
                print "switching to TCP"
                tcp_connector = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcp_connector.connect((remote, remotePort))
                tcp_connector.send(data)
                response = tcp_connector.recv(4096 * 32)

        print response
        sock.sendall(response)
        sock.close()                

    except socket.error:
        pass
    
        
        
