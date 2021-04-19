#!/usr/bin/env python

__author__ = "Arseniy Tyurin"
__version__ = "0.1"
__license__ = "MIT"

## Example of HTTP GET Requst
#
# GET /index.html HTTP/1.1
# Host: localhost
#
# Example of HTTP Response
#
# HTTP/1.1 200 OK
# Content-Type: text/html; charset=utf-8
#
# <html>....</html>

import socket
import sys

# Shorthand for common HTTP statuses, feel free to add more
http_status = {
    '200': b'HTTP/1.1 200 OK',
    '400': b'HTTP/1.1 400 Bad Request',
    '404': b'HTTP/1.1 404 Not Found'
}
# Content types, self-explanatory
content_type = {
    'html': b'Content-Type: text/html; charset=utf-8',
    'jpg': b'Content-Type: image/jpeg',
    'png': b'Content-Type: image/png',
    'css': b'Content-Type: text/css',
    'js': b'Content-Type: text/javascript'
}
# HTTP request header lines separated by '\r\n', so we use that later
sep = b'\r\n'


def fancy_introduction(port):
    # Confirmation that server has started
    server = f' Python webserver v.{__version__}'
    checkmark = b'\xe2\x9c\x93'.decode()
    status = f' Status: {checkmark}'
    addr = f' Address: http://localhost:{port}'

    print('\n')
    print(u"\u250c" + u"\u2500" * 36+ u"\u2510")
    print(u"\u2502" + f'{server:36}' + u"\u2502")
    print(u"\u2502" + f'{addr:36}' + u"\u2502")
    print(u"\u2502" + f'{status:36}' + u"\u2502")
    print(u"\u2514" + u"\u2500" * 36 + u"\u2518")
    print('\n')

# Main part where we start 'TCP' socket and listen for incoming messages
# We create socket to tell our OS that we takeover certain port
# and start listening for incoming messages. These messages could be anything,
# event simple plain text, but our server will understand and react only
# to HTTP requests
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Take port from command line
    port = int(sys.argv[1])
    # Bind host and port to the socket
    s.bind(('localhost', port))
    # Listen for incoming messages
    s.listen()

    fancy_introduction(port)

    # Server is going to run until something breaks
    while True:
        # Client connected
        client, addr = s.accept()
        # Read clients message, suppose to be HTTP GET request
        # 4096 is arbitrary, you can go as much as 65535
        # Normally, HTTP header will fit into 4086 bytes
        msg = client.recv(4096)
        print(msg.decode().split("\n")[0])
        # Request URL
        request = msg.decode().split("\n")[0].split(' ')[1]
        if request == '/': request = '/index.html'
        # So far we serve HTML and JPG
        file_type = request.split('.')[1]
        # Load page if it exists or send 404 if not found
        if file_type == 'html':
            try:
                with open('html/' + request[1:], 'r') as f:
                    body = f.read()
                    body = body.encode()
                    header = http_status['200'] + sep + content_type['html'] + sep + sep
            except:
                    body = ''.encode()
                    header = http_status['404']
        # Load JPG image or send 404 if not found
        if file_type == 'jpg':
            try:
                with open(request[1:], 'rb') as f:
                    body = f.read()
                    header = http_status['200'] + sep + content_type['jpg'] + sep + sep
            except:
                    body = ''.encode()
                    header = http_status['404']
        # Load stylesheet
        if file_type == 'css':
            try:
                with open(request[1:], 'r') as f:
                    body = f.read()
                    body = body.encode()
                    header = http_status['200'] + sep + content_type['css'] + sep + sep
            except:
                    body = ''.encode()
                    header = http_status['404']

        # Every HTTP response contains header and body
        response = (header + body)
        # Sending response and closing connection
        client.send(response)
        client.close()
