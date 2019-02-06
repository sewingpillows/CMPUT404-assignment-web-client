#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it


############################
# Sources
# stackoverflow
# TITLE: How can I determine the byte length of a utf-8 encoded string in Python?
# URL:  https://stackoverflow.com/questions/6714826/how-can-i-determine-the-byte-length-of-a-utf-8-encoded-string-in-python
# ANSWER: https://stackoverflow.com/a/6714872
# AUTHOR: Mark Reed - https://stackoverflow.com/users/797049/mark-reed

import sys
import socket
import re
import json
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")



class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

# Object to help build the response
class Request(object):
    def __init__(self):
        self.request = {}
        self.set_values()

    def set_values(self):
        self.request['init_header'] = ''
        self.request['header'] = ''
        self.request['payload'] = ''

    def toString(self):
        packet = self.request['init_header']
        packet += self.request['header']+"\r\n"
        packet += self.request['payload']
        return packet

    def init_header(self, method, resource):
        line = "%s /%s HTTP/1.1\r\n" % (method, resource)
        self.request['init_header'] = line

    def add_content_length(self):
        size = self.get_utflen()
        line = "Content-Length: %s\r\n" % str(size)    
        self.request['header'] = self.request['header']+line

    def add_host(self, host):
        line = "HOST: %s\r\n" %  (host)
        self.request['header'] = self.request['header']+line

    def add_contentType(self):
        line = "Content-Type: application/x-www-form-urlencoded\r\n"
        self.request['header'] = self.request['header']+line

    def add_post_args(self, args):
        variables =''
        if (args != None):
            for arg in args:
                variables += arg+'='+args[arg]+'&'
        variables = variables
        self.request['payload'] = variables

    def get_body(self):
        return self.request['payload']

    def get_header(self):
        return  self.request['init_header']+self.request['header']  

    def get_utflen(self):
        strBody = self.get_body()
        return len(strBody.encode('utf-8'))

    def clear(self):
        self.request.clear()
        self.set_values()

class HTTPClient(object):

    def __init__(self):
        self.request = Request()

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((host, port))
            return self.socket
        except:
            print ('Could not connect with:')
            print ('\thost: ' +host)
            print ('\tport: ',port)
            print ('terminating program')
            sys.exit(1)
      
    def get_port(self, url):
        port = re.search(':([0-9]+)', url)
        if (port == None):
            return 80
        return int(port.group(1))

    def get_resource(self, url):
        resource = re.sub('^https?:\/\/','', url)
        if ('/' in resource):
            return resource.split('/', 1)[1]
        return ''

    def get_request(self, host, resource):
        self.request.init_header("GET", resource)
        self.request.add_host(host)
        return self.request.toString()

    def post_request(self, host, resource, args=None):
        self.request.init_header("POST", resource)
        self.request.add_host(host)
        self.request.add_contentType()
        if (args != None):
            self.request.add_post_args(args)
        self.request.add_content_length()
        return self.request.toString()

    def get_code(self, data):
        return int(data[0].split(' ')[1].strip())

    def get_headers(self,data):
        return re.split('\r\n\r\n', data, 1)[0].split('\n')

    def get_body(self, data):
        return re.split('\r\n\r\n', data, 1)[-1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def get_host(self, url):
        host = re.search('https?:\/\/((?:[a-zA-Z0-9]*\.[a-zA-Z0-9]*)*)', url)
        return host.group(1)

    def GET(self, url, args=None):
        host = self.get_host(url)
        port = self.get_port(url)
        resource = self.get_resource(url)
        s = self.connect(host, port)
        data =self.get_request(host, resource)
        self.sendall(data)
        strData = self.recvall(s)      
        body = self.get_body(strData)
        header = self.get_headers(strData)
        code = self.get_code(header)
        self.close()
        self.request.clear()
        return HTTPResponse(code, body)


    def POST(self, url, args=None):
        host = self.get_host(url)
        port = self.get_port(url)
        resource = self.get_resource(url)
        data = self.post_request(host, resource, args)
        s = self.connect(host, port)
        self.sendall(data)
        strData = self.recvall(s)      
        body = self.get_body(strData)
        header = self.get_headers(strData)
        code = self.get_code(header)
        self.close()
        self.request.clear()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
