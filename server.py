#!/usr/bin/python

# the "gatekeeper".
# an attempt to implement Hybrid TCP-UDP Transport for Web Traffic by Cidon, Rom, Gupta, and Schuba
import socket
import sys

# TCP Limit
LIMIT = 1460 * 2 # formerly 1460

if len(sys.argv) < 2:
    print "Usage: python server.py [server port]"
    print "This server-side proxy-ish script will redirect incoming"
    print "hybrid UDP-TCP HTTP traffic to the port."
    sys.exit()

# Timestap print
def log(msg):
    from datetime import datetime
    print '[' + str(datetime.now()) + '] ' + str(msg)

host = ''
port = 81
realPort = int(sys.argv[1])

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

import re
p = re.compile(ur'Content-Length:\s\d*')

while True:
    mode = ""
    data = ""

    try:
        data, addr = udp_sock.recvfrom(2048)
        if data != "":
            log("received UDP connection!")
            mode = "udp"
    except socket.error:
        pass

    try:
        sock, addr = tcp_sock.accept()
        data = sock.recv(2048)
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

        response = ''
        resp = 'placeholder'
        response = internal_sock.recv(2048)

        if len(response) >= LIMIT and mode == 'udp':
            response = 'USETCP'
            log('Cut off transfer, instructing client to use TCP')
        else:
            matches = re.findall(p, response)
            headerEnd = response.find('\r\n\r\n') + 4 # get end of header
            # TODO: share this between scripts
            if not (len(matches) < 1 or len(matches[0].split(' ')) < 1):
                contentLength = int(matches[0].split(' ')[1])
                log("content length = " + str(contentLength))
                log('header ends at ' + str(headerEnd))
                while len(response) - headerEnd < contentLength:
                    log("Need moar data!")
                    resp = internal_sock.recv(2048)
                    log("receiving more data..." + str(len(resp)))
                    response += resp

            else:
                log('no content length...')
                z = re.compile(ur'Transfer-Encoding:\schunked')
                if not len(re.findall(z, response)) > 0:
                    log('not chunking either, wtf?')
                    log('Fatal error: alien technology discovered! Report to CIA as soon as possible.')

                else:
                    log('chunking detected...')
                    runningTotal = headerEnd
                    chunkSize = -1
                    responseBody = response[headerEnd:]
                    runningTotal = 0
                    chunks = responseBody.split('\r\n')
                    #print chunks
                    i = 0
                    # TODO: replace this really problematic way of doing this
                    while '0' not in chunks: #response.find('\r\n0\r\n') == -1:
                        log('I need moar chunks!')
                        response += internal_sock.recv(2048)
                        responseBody = response[headerEnd:]
                        runningTotal = 0
                        chunks = responseBody.split('\r\n')


        #        print response
        internal_sock.shutdown(socket.SHUT_RDWR)
        internal_sock.close()
        if mode == "udp":
            udp_client.connect((addr[0], port))
            if len(response) < LIMIT:
                udp_client.sendall(response)
            else:
                udp_client.sendall("USETCP")
                log("response too large, directed client to retry with TCP")
        elif mode == "tcp":
            sock.sendall(response)
            sock.close()
