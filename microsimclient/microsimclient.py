#!/usr/local/bin/python3
import sys
import os
import socket
import time
import random
import string
import requests
import json

REQUEST_URLS = os.getenv('REQUEST_URLS', False)
REQUEST_INTERNET = os.getenv('REQUEST_INTERNET', False)
REQUEST_MALWARE = os.getenv('REQUEST_MALWARE', False)
SEND_SQLI = os.getenv('SEND_SQLI', False)
SEND_DIR_TRAVERSAL = os.getenv('SEND_DIR_TRAVERSAL', False)
SEND_XSS = os.getenv('SEND_XSS', False)
SEND_DGA = os.getenv('SEND_DGA', False)
REQUEST_WAIT_SECONDS = float(os.getenv('REQUEST_WAIT_SECONDS', 3.0))
REQUEST_BYTES = int(os.getenv('REQUEST_BYTES', 1024))
STOP_SECONDS = int(os.getenv('STOP_SECONDS', 0))
ATTACK_PROBABILITY = float(os.getenv('ATTACK_PROBABILITY', 0.001))
EGRESS_PROBABILITY = float(os.getenv('EGRESS_PROBABILITY', 0.1))
START_TIME = int(time.time())

def keep_running():
    if not REQUEST_URLS:
        sys.exit('Server killed - REQUEST_URLS environment variable required.')

    if (STOP_SECONDS != 0) and ((START_TIME + STOP_SECONDS) < int(time.time())):
        sys.exit('Server killed after ' + str(STOP_SECONDS) + ' seconds.')
    return True

def insert_data():
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(REQUEST_BYTES)])

while keep_running():
    url_list = REQUEST_URLS.split(',')

    json_body = {}
    json_body['data'] = insert_data()

    for url in url_list:
        try:
            response = requests.post(url, json=json_body)
            print('Request to ' + response.url + '   Request size: ' + str(len(response.request.body)) + '   Response size: ' + str(len(response.content)))
        except Exception as e:
            print(str(e) + ' error to: ' + url)

        if SEND_SQLI:
            if random.random() < ATTACK_PROBABILITY:
                parameters = {
                    'username': 'joe@example.com',
                    'password': ';UNION SELECT 1, version() limit 1,1--'
                }

                try:
                    sqli = requests.get(url, params=parameters)
                    print('SQLi sent: ' + sqli.url)
                except Exception as e:
                    print(str(e) + ' error to: ' + url)

        if SEND_XSS:
            if random.random() < ATTACK_PROBABILITY:
                parameters = {
                    'username': 'joe@example.com',
                    'password': "pwd<script>alert('attacked')</script>"
                }

                try:
                    xss = requests.get(url, params=parameters)
                    print('XSS sent: ' + xss.url)
                except Exception as e:
                    print(str(e) + ' error to: ' + url)

        if SEND_DIR_TRAVERSAL:
            if random.random() < ATTACK_PROBABILITY:
                parameters = {
                    'username': 'joe@example.com',
                    'password': '../../../../../passwd'
                }

                try:
                    dirtraversal = requests.get(url, params=parameters)
                    print('Directory Traversal sent: ' + dirtraversal.url)
                except Exception as e:
                    print(str(e) + ' error to: ' + url)

    if REQUEST_INTERNET:
        if random.random() < EGRESS_PROBABILITY:
            fortinet = requests.Session()
            
            try:
                fortinet = fortinet.get('http://www.fortinet.com', allow_redirects=True)
                print('Internet request to: ' + fortinet.url)
            except Exception as e:
                print(str(e) + ' error to: ' + url)

    if REQUEST_MALWARE:
        if random.random() < ATTACK_PROBABILITY:
            eicar = requests.Session()
            
            try:
                eicar = eicar.get('http://www.eicar.org/download/eicar.com.txt')
                print('Malware downloaded: ' + eicar.text)
            except Exception as e:
                print(str(e) + ' error to: ' + url)

    if SEND_DGA:
        if random.random() < ATTACK_PROBABILITY:
            dga_domains = [
                't3622c4773260c097e2e9b26705212ab85.ws',
                'u83ccf36d9f02e9ea79a9d16c0336677e4.to',
                'v02bec0c090508bc76b3ea81dfc2198a71.in',
                'wa9e4628c334324e181e40f33f878c153f.hk',
                'xdcc5481252db5f38d5fc18c9ad3b2f7fd.cn',
                'yf32d9ac7f0a9f463e8da4736b12d7044a.tk'
            ]

            try:
                for dga in dga_domains:
                    dga_response = socket.gethostbyname(dga)
                    print('DGA query sent: ' + dga + '   Response: ' + dga_response)
            except Exception as e:
                print(str(e) + ' error to: ' + url)

    time.sleep(REQUEST_WAIT_SECONDS)


