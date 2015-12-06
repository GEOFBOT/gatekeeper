#!/usr/bin/python

# the "gatekeeper".
# an attempt to implement Hybrid TCP-UDP Transport for Web Traffic by Cidon, Rom, Gupta, and Schuba
import socket
import sys
import select

# timestamp logging
def log(msg):
    from datetime import datetime
    print '[' + str(datetime.now()) + '] ' + str(msg)


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

import re
p = re.compile(ur'Content-Length:\s\d*\s')

def recvall(socket):
    response = socket.recv(4096)
    matches = re.findall(p, response)
    # with Content-Length
    if not (len(matches) < 1 or len(matches[0].split(' ')) < 1):
        contentLength = int(matches[0].split(' ')[1])
        log("content length = " + str(contentLength))
        headerEnd = response.find('\r\n\r\n') + 4
        log('header ends at ' + str(headerEnd))
        while len(response) - headerEnd < contentLength:
            resp = socket.recv(4096)
            log("receiving more data..." + str(len(resp)))
            response += resp

    else:
        log('no content length...')
        print response
        z = re.compile(ur'Transfer-Encoding:\schunked')
        if not len(re.findall(z, response)) > 0:
            log('not chunking either, wtf?')
            log('Fatal error: alien technology discovered!')
            log('Report to CIA as SOON AS POSSIBLE.')

        else:
            log('chunking detected...')
            runningTotal = headerEnd
            chunkSize = -1
            responseBody = response[headerEnd:]
            runningTotal = 0
            chunks = responseBody.split('\r\n')
            print chunks
            i = 0
            # TODO: replace this really problematic way of doing this
            while '0' not in chunks: #response.find('\r\n0\r\n') == -1:
                log('I need moar chunks!')
                response += internal_sock.recv(4096)
                responseBody = response[headerEnd:]
                runningTotal = 0
                chunks = responseBody.split('\r\n')
    return response

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
                    response = recvall(udp_receiver)
            if mode == "tcp" or not ready[0] or response.startswith('USETCP'): # use tcp
                if permmode == 'tcp':
                    log('Not using UDP...')
                log('Switching to TCP...')
                tcp_connector = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcp_connector.connect((remote, remotePort))
                tcp_connector.send(data)
                response = recvall(tcp_connector)
                tcp_connector.shutdown(socket.SHUT_RDWR)
                tcp_connector.close()

        sock.sendall(response)
        log('Sent response back to client browser')
        sock.close()

    except socket.error:
        pass
