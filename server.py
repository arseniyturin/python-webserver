#!/usr/bin/env python

__author__ = "Arseniy Tyurin"
__version__ = "0.1"
__license__ = "MIT"

import socket
import sys
import os
import time
import datetime

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
    'js': b'Content-Type: text/javascript',
    'ico': b'Content-Type: image/x-icon'
}

# HTTP request header lines separated by '\r\n', so we use that later
sep = b'\r\n'
# Define routes for specific file types
# It works as alias if you want to mask the real path to the file
routes = {
    'html': 'html'
}
#Last-Modified: <day-name>, <day> <month> <year> <hour>:<minute>:<second> GMT

def fancy_introduction(port):
    # Confirmation that server has started
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    server = f' Python Webserver v.{__version__}'
    checkmark = b'\xe2\x9c\x93'.decode()
    status = f' Status: {checkmark}'
    addr = f' Address: http://{ip}:{port}'

    print('\n')
    print(u"\u250c" + u"\u2500" * 36+ u"\u2510")
    print(u"\u2502" + f'{server:36}' + u"\u2502")
    print(u"\u2502" + f'{addr:36}' + u"\u2502")
    print(u"\u2502" + f'{status:36}' + u"\u2502")
    print(u"\u2514" + u"\u2500" * 36 + u"\u2518")
    print('\n')


def open_static(filename, mode='rb'):
    '''Opens static file and returns it\'s binary representation'''
    try:
        with open(filename, mode) as f:
            data = f.read()
            ts = os.stat(filename).st_mtime
            last_modified = datetime.datetime \
                .utcfromtimestamp(ts) \
                .strftime('%a, %d %b %Y %H:%M:%S GMT')
            return data, last_modified
    except:
        return b'', 0

def build_header(status, file_type, last_modified):
    '''
    Forming HTTP Header for a response, for example:

    HTTP/1.1 200 OK\r\n
    Content-Type: text/html\r\n
    Last-Modified: Wed, 21 Apr 2021 14:05:46 GMT

    '''
    last_modified = f'Last-Modified: {last_modified}'.encode()
    return http_status[status] + sep \
        + content_type[file_type] + sep \
        + last_modified + sep + sep

def prepare_response(filename):
    '''
    Function reads a static file located on the server and returns file
    content with appropriate header if success, otherwise throw 404 error.
    Function supports only few file types, such as html, css and jpg
    '''
    if filename == '': filename = 'index.html'
    # Get requested file type, ex index.html -> html
    file_type = filename.split('.')[1]
    # If route is defined, use it
    if routes.get(file_type):
        path = routes[file_type] + '/' + filename
    else:
        path = filename
    # Open file
    body, last_modified = open_static(path, 'rb')

    # If success, return header and body, otherwise throw 404
    if body:
        header = build_header('200', file_type, last_modified)
    else:
        header = build_header('404', file_type, last_modified)

    return header + body

def parse_request(request):
    '''
    Function parse HTTP-request and returns method,
    file requested by the browser and protocol.
    Since the server can process GET requests only (so far), method and protocol
    are not used anywhere in the code, but will be useful in the future
    '''
    headers = request.decode().split('\r\n')
    method, file, protocol = headers[0].split(' ')
    return method, file[1:], protocol


def run():
    '''
    Function opens socket on hostname:port and starts to listen for requests
    '''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Host (0.0.0.0 means for any ip address)
        host = '0.0.0.0'
        # Take port from command line
        port = int(sys.argv[1])
        # Bind socket to the desired address
        s.bind((host, port))
        # Listen for incoming messages
        s.listen()

        # Shows introduction to the terminal
        fancy_introduction(port)
        # Server is going to run until something breaks
        while True:
            # Client connected
            client, addr = s.accept()
            # Read clients message (suppose to be HTTP GET request)
            # 4096 is arbitrary, you can go as much as 65535
            msg = client.recv(4096)
            # if server go appropriate request -> create response
            if msg:
                method, file, protocol = parse_request(msg)
                response = prepare_response(file)
                client.send(response)
                client.close()
                print(f'({time.ctime()}) - {method} - {file}')

if __name__ == '__main__':
    run()
