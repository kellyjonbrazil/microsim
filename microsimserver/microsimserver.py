#!/usr/local/bin/python3
import sys
import os
import socket
import time
import random
import string
import json
import threading
from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer

LISTEN_PORT = int(os.getenv('LISTEN_PORT', 8080))
STATS_PORT = int(os.getenv('STATS_PORT', False))
RESPOND_BYTES = int(os.getenv('RESPOND_BYTES', 16384))
STOP_SECONDS = int(os.getenv('STOP_SECONDS', 0))
START_TIME = int(time.time())
HOST_NAME = ''

stats = {
    'Total': {
        'Requests': 0,
        'Sent Bytes': 0,
        'Received Bytes': 0
    }
}

def keep_running():
    if (STOP_SECONDS != 0) and ((START_TIME + STOP_SECONDS) < int(time.time())):
        sys.exit('Server killed after ' + str(STOP_SECONDS) + ' seconds.')
    return True

def insert_data():
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(RESPOND_BYTES)])

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class httpd(BaseHTTPRequestHandler):
    server_name = socket.gethostname()
    server_ip = socket.gethostbyname(server_name)

    def do_GET(self):
        """simple http response"""
        host_header = self.headers['Host']
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        data = insert_data() + '\n'
        info = time.asctime() + '   hostname: ' + self.server_name + '   ip: ' + self.server_ip + '   remote: ' + self.address_string() + '   hostheader: ' + str(host_header) + '   path: ' + self.path + '\n'
        body = data + info
        self.wfile.write(body.encode('utf-8'))
        stats['Total']['Requests'] += 1
        stats['Total']['Sent Bytes'] += len(body)

    def do_POST(self):
        """json api response"""
        host_header = self.headers['Host']
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.response = {
            'data': insert_data(),
            'time': time.asctime(),
            'hostname': self.server_name,
            'ip': self.server_ip,
            'remote': self.address_string(),
            'hostheader': host_header,
            'path': self.path
        }
        body = json.dumps(self.response)
        self.wfile.write(body.encode('utf-8'))
        stats['Total']['Requests'] += 1
        stats['Total']['Sent Bytes'] += len(body)
        stats['Total']['Received Bytes'] += int(self.headers['Content-Length'])

class stats_httpd(BaseHTTPRequestHandler):
    server_name = socket.gethostname()
    server_ip = socket.gethostbyname(server_name)

    def do_GET(self):
        host_header = self.headers['Host']
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.response = {
            'time': time.asctime(),
            'runtime': int(time.time() - START_TIME),
            'hostname': self.server_name,
            'ip': self.server_ip,
            'stats': stats['Total'],
            'config': {
                'LISTEN_PORT': LISTEN_PORT,
                'STATS_PORT': STATS_PORT,
                'RESPOND_BYTES': RESPOND_BYTES,
                'STOP_SECONDS': STOP_SECONDS
            }
        }
        body = json.dumps(self.response, indent=2)
        self.wfile.write(body.encode('utf-8'))

def statistics_server():
    if STATS_PORT:
        stats_server = ThreadingHTTPServer((HOST_NAME, STATS_PORT), stats_httpd)
        stats_server.serve_forever()

def main():
    microservice = ThreadingHTTPServer((HOST_NAME, LISTEN_PORT), httpd)
    while keep_running():
        microservice.handle_request()

stats_thread = threading.Thread(target=statistics_server, daemon=True)
stats_thread.start()

main()
