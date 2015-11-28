#!/usr/bin/python

# the "gatekeeper".
# an attempt to implement Hybrid TCP-UDP Transport for Web Traffic by Cidon, Rom, Gupta, and Schuba
import socket
# TODO IMPLEMENT TIMEOUT FOR UDP TCP FALLBACK

host = ''
remote = 'golf620-linux.local'
port = 82
remotePort = 81

udp_receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_receiver.setblocking(1)
udp_receiver.bind((host, remotePort))

udp_connector = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_connector.connect((remote, remotePort)) 

print "Client proxy started..."

tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.bind((host, port))
tcp_socket.listen(5)

while True:
    mode = ""
    data = ""
    
    try:        
        sock, addr = tcp_socket.accept()
        data = sock.recv(4096)
        print data
        if data:
            udp_connector.send(data)
            #udp_connector.send('\n\n')
            response = udp_receiver.recv(4096 * 32)
            print response
            if response.startswith('USETCP'): # use tcp
                print "switching to TCP"
                tcp_connector = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcp_connector.connect((remote, remotePort))
                tcp_connector.send(data)
                #tcp_connector.send('\n\n')
                response = tcp_connector.recv(4096 * 32)

            print response
            sock.sendall(response)
        sock.close()                

    except socket.error:
        pass
            
        
        
