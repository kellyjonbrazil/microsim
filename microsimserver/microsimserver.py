#!/usr/local/bin/python3
import sys
import os
import socket
import time
import random
import string
import re
import json
import threading
import urllib.parse
from socketserver import ThreadingMixIn
from statsd import StatsClient
from http.server import BaseHTTPRequestHandler, HTTPServer

def str2bool(val):
    if val and val.lower() != 'false':
        return bool(val)
    return False

LISTEN_PORT = int(os.getenv('LISTEN_PORT', 8080))
STATS_PORT = os.getenv('STATS_PORT', None)
STATSD_HOST = os.getenv('STATSD_HOST', None)
STATSD_PORT = int(os.getenv('STATSD_PORT', 8125))
RESPOND_BYTES = int(os.getenv('RESPOND_BYTES', 16384))
STOP_SECONDS = int(os.getenv('STOP_SECONDS', 0))
STOP_PADDING = str2bool(os.getenv('STOP_PADDING', False))
START_TIME = int(time.time())
HOST_NAME = ''

padding = 0
if STOP_SECONDS and STOP_PADDING:
    padding = random.choice(range(STOP_SECONDS))

stats = {
    'Total': {
        'Requests': 0,
        'Sent Bytes': 0,
        'Received Bytes': 0,
        'Attacks': 0,
        'SQLi': 0,
        'XSS': 0,
        'Directory Traversal': 0
    },
    'Last 30 Seconds': {
        'Requests': 0,
        'Sent Bytes': 0,
        'Received Bytes': 0,
        'Attacks': 0,
        'SQLi': 0,
        'XSS': 0,
        'Directory Traversal': 0
    }
}

if STATSD_HOST:
    server_stats = StatsClient(prefix='all_servers',
                               host=STATSD_HOST,
                               port=STATSD_PORT)

    host_stats = StatsClient(prefix='server-' + socket.gethostname(),
                             host=STATSD_HOST,
                             port=STATSD_PORT)

lock = threading.Lock()

def keep_running():
    if (STOP_SECONDS != 0) and ((START_TIME + STOP_SECONDS + padding) < int(time.time())):
        sys.exit('Server killed after ' + str(int(STOP_SECONDS) + int(padding)) + ' seconds.')
        
    return True

def insert_data():
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(RESPOND_BYTES)])

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class state():
    last_timestamp = START_TIME

def every_30_seconds():
    with lock:
        if state.last_timestamp + 30 > int(time.time()):
            return False

        state.last_timestamp = int(time.time())
        return True

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

        with lock:
            stats['Total']['Requests'] += 1
            stats['Total']['Sent Bytes'] += len(body)
            stats['Last 30 Seconds']['Requests'] += 1
            stats['Last 30 Seconds']['Sent Bytes'] += len(body)

        if STATSD_HOST:
            server_stats.incr('requests')
            server_stats.incr('sent_bytes', len(body))
            host_stats.incr('requests')
            host_stats.incr('sent_bytes', len(body))
            
        if re.search('UNION SELECT', urllib.parse.unquote_plus(self.path)):
            print(time.strftime("%Y-%m-%dT%H:%M:%S") + '   SQLi attack detected')
            with lock:
                stats['Total']['Attacks'] += 1
                stats['Total']['SQLi'] += 1
                stats['Last 30 Seconds']['Attacks'] += 1
                stats['Last 30 Seconds']['SQLi'] += 1

            if STATSD_HOST:
                server_stats.incr('attacks')
                server_stats.incr('sqli')
                host_stats.incr('attacks')
                host_stats.incr('sqli')

        if re.search('<script>alert', urllib.parse.unquote(self.path)):
            print(time.strftime("%Y-%m-%dT%H:%M:%S") + '   XSS attack detected')
            with lock:
                stats['Total']['Attacks'] += 1
                stats['Total']['XSS'] += 1
                stats['Last 30 Seconds']['Attacks'] += 1
                stats['Last 30 Seconds']['XSS'] += 1

            if STATSD_HOST:
                server_stats.incr('attacks')
                server_stats.incr('xss')
                host_stats.incr('attacks')
                host_stats.incr('xss')

        if re.search('../../../../../passwd', urllib.parse.unquote(self.path)):
            print(time.strftime("%Y-%m-%dT%H:%M:%S") + '   Directory Traversal attack detected')
            with lock:
                stats['Total']['Attacks'] += 1
                stats['Total']['Directory Traversal'] += 1
                stats['Last 30 Seconds']['Attacks'] += 1
                stats['Last 30 Seconds']['Directory Traversal'] += 1

            if STATSD_HOST:
                server_stats.incr('attacks')
                server_stats.incr('directory_traversal')
                host_stats.incr('attacks')
                host_stats.incr('directory_traversal')

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
        with lock:
            stats['Total']['Requests'] += 1
            stats['Total']['Sent Bytes'] += len(body)
            stats['Total']['Received Bytes'] += int(self.headers['Content-Length'])
            stats['Last 30 Seconds']['Requests'] += 1
            stats['Last 30 Seconds']['Sent Bytes'] += len(body)
            stats['Last 30 Seconds']['Received Bytes'] += int(self.headers['Content-Length'])

        if STATSD_HOST:
            server_stats.incr('requests')
            server_stats.incr('sent_bytes', len(body))
            server_stats.incr('received_bytes', int(self.headers['Content-Length']))
            host_stats.incr('requests')
            host_stats.incr('sent_bytes', len(body))
            host_stats.incr('received_bytes', int(self.headers['Content-Length']))

        if re.search(';UNION SELECT 1, version() limit 1,1--', urllib.parse.unquote(self.path)):
            print(time.strftime("%Y-%m-%dT%H:%M:%S") + '   SQLi attack detected')
            with lock:
                stats['Total']['Attacks'] += 1
                stats['Total']['SQLi'] += 1
                stats['Last 30 Seconds']['Attacks'] += 1
                stats['Last 30 Seconds']['SQLi'] += 1

            if STATSD_HOST:
                server_stats.incr('attacks')
                server_stats.incr('sqli')
                host_stats.incr('attacks')
                host_stats.incr('sqli')

        if re.search("pwd<script>alert('attacked')</script>", urllib.parse.unquote(self.path)):
            print(time.strftime("%Y-%m-%dT%H:%M:%S") + '   XSS attack detected')
            with lock:
                stats['Total']['Attacks'] += 1
                stats['Total']['XSS'] += 1
                stats['Last 30 Seconds']['Attacks'] += 1
                stats['Last 30 Seconds']['XSS'] += 1

            if STATSD_HOST:
                server_stats.incr('attacks')
                server_stats.incr('xss')
                host_stats.incr('attacks')
                host_stats.incr('xss')

        if re.search('../../../../../passwd', urllib.parse.unquote(self.path)):
            print(time.strftime("%Y-%m-%dT%H:%M:%S") + '   Directory Traversal attack detected')
            with lock:
                stats['Total']['Attacks'] += 1
                stats['Total']['Directory Traversal'] += 1
                stats['Last 30 Seconds']['Attacks'] += 1
                stats['Last 30 Seconds']['Directory Traversal'] += 1

            if STATSD_HOST:
                server_stats.incr('attacks')
                server_stats.incr('directory_traversal')
                host_stats.incr('attacks')
                host_stats.incr('directory_traversal')

class stats_httpd(BaseHTTPRequestHandler):
    server_name = socket.gethostname()
    server_ip = socket.gethostbyname(server_name)

    def do_GET(self):
        host_header = self.headers['Host']
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        with lock:
            self.response = {
                'time': time.asctime(),
                'runtime': int(time.time() - START_TIME),
                'hostname': self.server_name,
                'ip': self.server_ip,
                'stats': stats['Total'],
                'config': {
                    'LISTEN_PORT': LISTEN_PORT,
                    'STATS_PORT': int(STATS_PORT),
                    'STATSD_HOST': STATSD_HOST,
                    'STATSD_PORT': STATSD_PORT,
                    'RESPOND_BYTES': RESPOND_BYTES,
                    'STOP_SECONDS': STOP_SECONDS,
                    'STOP_PADDING': STOP_PADDING,
                    'TOTAL_STOP_SECONDS': STOP_SECONDS + padding,
                }
            }
        body = json.dumps(self.response, indent=2)
        self.wfile.write(body.encode('utf-8'))

def statistics_server():
    stats_server = ThreadingHTTPServer((HOST_NAME, int(STATS_PORT)), stats_httpd)
    stats_server.serve_forever()

def main():
    microservice = ThreadingHTTPServer((HOST_NAME, LISTEN_PORT), httpd)
    while keep_running():
        microservice.handle_request()

        if every_30_seconds():
            # Print and clear statistics
            with lock:
                print(json.dumps(stats))
                stats['Last 30 Seconds'] = {
                    'Requests': 0,
                    'Sent Bytes': 0,
                    'Received Bytes': 0,
                    'Attacks': 0,
                    'SQLi': 0,
                    'XSS': 0,
                    'Directory Traversal': 0
                }

if STATS_PORT:
    stats_thread = threading.Thread(target=statistics_server, daemon=True)
    stats_thread.start()

main()
