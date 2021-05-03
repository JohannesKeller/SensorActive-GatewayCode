import http.server, ssl
import cgi
import base64
import json
from urllib.parse import urlparse, parse_qs
import json
from colorama import init, Fore, Style
import os
from io import BytesIO
import time
import sys
import _thread


import globalvars


class CustomServerHandler(http.server.BaseHTTPRequestHandler):

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header(
            'WWW-Authenticate', 'Basic realm="Demo Realm"')
        self.send_header('Content-type', 'application/json')
        self.end_headers()
    
    def get_Postvar(self, x, befehl):
        for y in x:
            if y[0] == befehl:
                return y[1]
        
        

    def do_POST(self):
        key = self.server.get_auth_key()
        base_path = urlparse(self.path).path        
        self.do_AUTHHEAD()
        response =""
        
        if self.headers.get('Authorization') == None:  
            
            if base_path == '/sensoractive_gateway':
                
                response = {
                    'success': True,
                }
                
                
            else:
            
                response = {
                    'success': False,
                    'error': 'no auth'
                }
            
            self.wfile.write(bytes(json.dumps(response), 'utf-8'))

        elif self.headers.get('Authorization') == 'Basic ' + str(key):
            
            content_len = int(self.headers.get('content-length', 0))
            post_body = self.rfile.read(content_len).decode("utf-8").split("&")
            
            p = []
            
            
            for x in post_body:
                x=x.split("=")
                p.append(x)
                #print(x)
            
            #print(p)          
            
            
            if base_path == '/sensoractive_gateway':
                
                response = {
                    'success': True,
                }
                
            
            elif base_path == '/status':
                
                with open(globalvars.path_to_framework_data_json, 'r') as f:
                    json_data = json.load(f)
                
                response = {
                            'success': True,
                            'data': json_data
                        }
                
                pass
            
            elif base_path == '/changeintervall':
                
                sensor = self.get_Postvar(p, "sensor")
                intervall = self.get_Postvar(p, "intervall")
            
                print(sensor)
                print(intervall)
                
                with open(globalvars.path_to_framework_data_json, "r") as jsonFile:
                    data = json.load(jsonFile)
                    
                data["sensors"][sensor]["sync_interval"] = intervall

                with open(globalvars.path_to_framework_data_json, "w") as jsonFile:
                    json.dump(data, jsonFile)
                
                response = {
                    'success': True,
                }
                #self.wfile.write(bytes(json.dumps(response), 'utf-8'))
                pass
            elif base_path == '/changeusername':
                old = self.get_Postvar(p, "old")
                new = self.get_Postvar(p, "new")
            
                print(old)
                print(new)
                
                with open(globalvars.path_to_password_json, "r") as jsonFile:
                    data = json.load(jsonFile)
                    
                if data["username"] == old:
                    data["username"] = new

                    with open(globalvars.path_to_password_json, "w") as jsonFile:
                        json.dump(data, jsonFile)
                    response = {
                        'success': True
                    }
                    self.wfile.write(bytes(json.dumps(response), 'utf-8'))
                    #time.sleep(5)
                    #super().shutdown()
                    #self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    #time.sleep(2)
                    _thread.start_new_thread(start_server, ())
                    
                    sys.exit()
                    #self.server.shutdown()
                    
                    #
                    #self.server.set_auth(data["username"], data["password"])
                    #self.server.serve_forever()
                else:
                    response = {
                            'success': False
                        }
                pass
            
            self.wfile.write(bytes(json.dumps(response), 'utf-8'))
            
        else:
            self.do_AUTHHEAD()

            response = {
                'success': False,
                'error': 'Invalid credentials'
            }

            self.wfile.write(bytes(json.dumps(response), 'utf-8'))



class CustomHTTPServer(http.server.HTTPServer):
    key = ''

    def __init__(self, address, handlerClass=CustomServerHandler):
        super().__init__(address, handlerClass)
    def set_auth(self, username, password):
        self.key = base64.b64encode(
            bytes('%s:%s' % (username, password), 'utf-8')).decode('ascii')
    
    def get_auth_key(self):
        return self.key
    

def start_server():
    IPAdresse = (("".join(os.popen('hostname -I').readlines())).split(" ", 1))[0]
    Port = 8888
    
    server = CustomHTTPServer((IPAdresse, Port))
    
    with open(globalvars.path_to_password_json, "r") as jsonFile:
        data = json.load(jsonFile)
        
    server.set_auth(data["username"], data["password"])
    
    server.socket = ssl.wrap_socket(server.socket,
                                    server_side=True,
                                    certfile='SSL/cert.pem',
                                    keyfile='SSL/key.pem',
                                    ssl_version=ssl.PROTOCOL_TLS)
    
    print(Fore.MAGENTA + "Webserver: Server läuft und ist über folgende Adresse erreichbar: "+IPAdresse+":"+str(Port))
    server.serve_forever()
    