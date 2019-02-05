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

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse
from functools import lru_cache

def help():
    print("httpclient.py [GET/POST] [URL]\n")




class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):

    def connect(self, host, port):
        print ("CONNECTED")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((host, port))
            return self.socket
        except:
            print ('''Could not connect with:
                    host: %s 
                    port: %s
                terminating program''') % (host, port)
            sys.exit(1)
      

    def get_port(self, host):
        if (re.fullmatch('^[^:]*:[^:]*', host)!=None):
            return host.split(':', 1)[-1]
        return '80'

    def get_resource(self, url):
        resource = re.sub('^https?:\/\/','', url)
        if ('/' in resource):
            return resource.split('/', 1)[1]
        return ''

    def get_request(self, host, resource):
        req = "GET /%s HTTP/1.1\r\n" % (resource)
        hos = "HOST: %s\r\n\r\n" %  (host)
        return req+hos

    def utflen(self, s):
        return len(s.encode('utf-8'))

        #CITE LATE https://stackoverflow.com/questions/6714826/how-can-i-determine-the-byte-length-of-a-utf-8-encoded-string-in-python
    def post_request(self, host, resource, args=None):
        req = "POST /%s HTTP/1.1\r\n" % (resource)
        hos = "HOST: %s\r\n" %  (host)
        content = "Content-Type: application/x-www-form-urlencoded\r\n"
        variables =''
        print (args)
        if (args != None):
            for arg in args:
                variables += arg+'='+repr(args[arg])[1:-1]+'&'
                print (variables)
            variables = variables[:-2]
        lwn = self.utflen(variables)
        contentlength = "Content-Length: %s\r\n" % str(lwn)
        return req+hos+content+contentlength+"\r\n"+variables

    def get_code(self, data):
        return int(data[0].split(' ')[1].strip())


    def get_headers(self,data):
        return re.split('\r\n\r\n', data, 1)[0].split('\n')

    def get_body(self, data):
        return re.split('\r\n\r\n', data, 1)[-1]
    
    def sendall(self, data):
        print ("IN SEND"+ data)
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
        host = re.sub('^https?:\/\/','', url).split('/', 1)[0]
        return host

    def get_host_port(self, url):
        host = re.sub('^https?:\/\/','', url).split('/', 1)[0]
        port = self.get_port(host)
        host = re.sub(':'+port, '', host)
        return (host, port)

    def GET(self, url, args=None):
        print ("URL "+ url)
        host, port  = self.get_host_port(url)
        resource = self.get_resource(url)
        s = self.connect(host, int(port))
        self.sendall(self.get_request(host, resource))
        strData = self.recvall(s)      
        body = self.get_body(strData)
        header = self.get_headers(strData)
        code = self.get_code(header)
        self.close()
        return HTTPResponse(code, body)


    def POST(self, url, args=None):
        print ("POST")
        host, port  = self.get_host_port(url)
        resource = self.get_resource(url)
        data = self.post_request(host, resource, args)
        print (data)
        s = self.connect(host, int(port))
        self.sendall(data)
        strData = self.recvall(s)      
        body = self.get_body(strData)
        header = self.get_headers(strData)
        code = self.get_code(header)
        self.close()
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
