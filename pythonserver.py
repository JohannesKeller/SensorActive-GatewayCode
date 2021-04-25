import http.server, ssl
import cgi
import base64
import json
from urllib.parse import urlparse, parse_qs
import json
from colorama import init, Fore, Style
import os

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

    def do_GET(self):
        key = self.server.get_auth_key()

        ''' Present frontpage with user authentication. '''
        if self.headers.get('Authorization') == None:
            self.do_AUTHHEAD()

            response = {
                'success': False,
                'error': 'No auth header received'
            }

            self.wfile.write(bytes(json.dumps(response), 'utf-8'))

        elif self.headers.get('Authorization') == 'Basic ' + str(key):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            getvars = self._parse_GET()

            response = {
                'path': self.path,
                'get_vars': str(getvars)
            }

            base_path = urlparse(self.path).path
            if base_path == '/status':
                with open(globalvars.path_to_framework_data_json, 'r') as f:
                    json_data = json.load(f)
                self.wfile.write(bytes(json.dumps(json_data), 'utf-8'))
                # Do some work
                pass
            elif base_path == '/path2':
                # Do some work
                pass

            self.wfile.write(bytes(json.dumps(response), 'utf-8'))
        else:
            self.do_AUTHHEAD()

            response = {
                'success': False,
                'error': 'Invalid credentials'
            }

            self.wfile.write(bytes(json.dumps(response), 'utf-8'))

    def do_POST(self):
        key = self.server.get_auth_key()

        ''' Present frontpage with user authentication. '''
        if self.headers.get('Authorization') == None:
            self.do_AUTHHEAD()
                
            response = {
                'success': False,
                'error': 'No auth header received'
            }

            self.wfile.write(bytes(json.dumps(response), 'utf-8'))

        elif self.headers.get('Authorization') == 'Basic ' + str(key):
            
            content_len = int(self.headers.get('content-length', 0))
            post_body = self.rfile.read(content_len).decode("utf-8").split("&")
            
            p = []
            
            
            for x in post_body:
                x=x.split("=")
                p.append(x)
                print(x)
            
            print(p)          
            
            
            
            
            response = {
                'path': self.path,
                #'get_vars': str(getvars)
                #'get_vars': str(postvars)
            }
            
            switch (urlparse(self.path).path) {
            case '/changeintervall':
                monthString = "January";
                break;
            default: monthString = "Invalid month";
                     break;
        }
            if base_path == '/changeintervall':
                
                
                """
                sensor = postvars["sensor"][0]
                intervall = postvars["intervall"][0]
            
                print(sensor)
                print(intervall)
                
                with open(globalvars.path_to_framework_data_json, "r") as jsonFile:
                    data = json.load(jsonFile)
                    
                data["sensors"][sensor]["sync_interval"] = intervall

                with open(globalvars.path_to_framework_data_json, "w") as jsonFile:
                    json.dump(data, jsonFile)
                """
                # Do some work
                pass
            elif base_path == '/changeusername':
                old = postvars["old"][0]
                new = postvars["new"][0]
            
                print(old)
                print(new)
                
                with open(globalvars.path_to_password_json, "r") as jsonFile:
                    data = json.load(jsonFile)
                    
                if data["username"] == old:
                    data["username"] = new

                    with open(globalvars.path_to_password_json, "w") as jsonFile:
                        json.dump(data, jsonFile)
                        response = {
                            'success': True,
                            'error': 'Invalid credentials'
                        }
                        #self.wfile.write(bytes(json.dumps(response), 'utf-8'))
                        
                        with open(globalvars.path_to_password_json, "r") as jsonFile:
                            data = json.load(jsonFile)
                        #server.shutdown()
                        #server.set_auth(data["username"], data["password"])
                        #server.serve_forever()
                else:
                    response = {
                            'success': False,
                            'error': 'Invalid credentials'
                        }
                    
                # Do some work
                pass
            
            self.wfile.write(bytes(json.dumps(response), 'utf-8'))
            
        else:
            self.do_AUTHHEAD()

            response = {
                'success': False,
                'error': 'Invalid credentials'
            }

            self.wfile.write(bytes(json.dumps(response), 'utf-8'))

        response = {
            'path': self.path,
            'get_vars': str(postvars)
            #'get_vars': str(postvars)
        }

        #self.wfile.write(bytes(json.dumps(response), 'utf-8'))
        
    def _parse_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            postvars = parse_qs(self.rfile.read(length),keep_blank_values=1)
        else:
            postvars = {}
        return postvars

    def _parse_GET(self):
        print(parse_qs(urlparse(self.path).query))
        print(urlparse(self.path).query)
        print(urlparse(self.path))
        print(self.path)
        getvars = parse_qs(urlparse(self.path).query)

        return getvars


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
    print("")
    print(Fore.MAGENTA + "Webserver: Server läuft und ist über folgende Adresse erreichbar: "+IPAdresse+":"+str(Port))
    server.serve_forever()
    