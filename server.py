#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AsyncIO implementation
#
#

__author__ = 'Arseniy Tyurin'
__version__ = '0.1'
__license__ = 'MIT'

import os, sys, re, time, datetime, json, socket, threading, webbrowser

def fancy_introduction(port):
    '''Confirmation that server has started'''
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    server = f' Python Webserver v.{__version__}'
    status = ' Status: ✓'
    addr = f' Address: http://{ip}:{port}'
    print('\n')
    print('┌' + '─'*36 + '┐')
    print('│' + f'{server:36}' + '│')
    print('│' + f'{addr:36}' + '│')
    print('│' + f'{status:36}' + '│')
    print('└' + '─'*36 + '┘')
    print('\n')

def load_config(filename):
    '''Open config file in JSON format'''
    with open(filename) as f:
        config = json.load(f)
        return config

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
    return http_status[status].encode() + sep \
        + content_type[file_type].encode() + sep \
        + last_modified + sep + sep

def parse_request(request):
    '''
    Function parse HTTP-request and returns method,
    file requested by the browser and protocol.
    Since the server can process GET requests only (so far),
    method and protocol are not used anywhere in the code,
    but will be useful in the future
    '''
    print(request.decode())
    GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    headers = request.decode().split('\r\n')
    method, request, protocol = headers[0].split(' ')
    if request == '/': request = '/index.html'
    path = re.findall('[/a-z.]+', request)[0]
    file_type = path.split('.')[1]

    if method == 'POST':
        body = headers[-1]
        print(f'Form data: {body}')

    return method, path, file_type

def prepare_response(method, path, file_type):
    '''
    Function reads a static file located on the server and returns file
    content with appropriate header if success, otherwise throw 404 error.
    Function supports only few file types, such as html, css and jpg
    '''
    if routes.get(file_type):
        path = routes[file_type] + path
    else:
        path = '.' + path
    # Open file
    body, last_modified = open_static(path, 'rb')
    # If success, return header and body, otherwise throw 404
    if body:
        header = build_header('200', file_type, last_modified)
    else:
        header = build_header('404', file_type, last_modified)

    return header + body

def process_request(msg, client):
    method, path, file_type = parse_request(msg)
    response = prepare_response(method, path, file_type)
    client.send(response)
    client.close()
    print(f'({time.ctime()}) - {method} - {path}')

def run():
    '''
    Heart of the Server
    Function opens socket on hostname:port and starts to listen for requests
    '''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Host (0.0.0.0 means for any ip address)
        host = '0.0.0.0'
        # Take port from command line
        try:
            port = int(sys.argv[1])
        except:
            port = config['default_port']
            print(f'Missing or Invalid port. Setting to default port {port}')
        # Bind socket to the desired address
        s.bind((host, port))
        # Listen for incoming messages
        s.listen()
        # Shows introduction to the terminal
        fancy_introduction(port)
        webbrowser.open(f'http://localhost:{port}')
        # Server is going to run until something breaks
        while True:
            # Client connected
            client, addr = s.accept()
            # Read clients message (suppose to be HTTP GET request)
            # 4096 is arbitrary, you can go as much as 65535
            msg = client.recv(4096)
            # if server go appropriate request -> create response
            if msg:
                threading.Thread(target=process_request, args=(msg, client)).start()

# Load server configuration
config = load_config('config.json')
http_status = config['http_status']
content_type = config['content_type']
routes = config['routes']
sep = config['sep'].encode()

if __name__ == '__main__':
    run()
