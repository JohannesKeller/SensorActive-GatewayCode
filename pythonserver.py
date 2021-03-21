import http.server
import cgi
import base64
import json
from urllib.parse import urlparse, parse_qs
import json


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
                with open('framework_data.json', 'r') as f:
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
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            #postvars = self._parse_POST()
            getvars = self._parse_GET()

            response = {
                'path': self.path,
                'get_vars': str(getvars)
                #'get_vars': str(postvars)
            }

            base_path = urlparse(self.path).path
            if base_path == '/changeintervall':
                sensor = getvars["sensor"][0]
                intervall = getvars["intervall"][0]
            
                print(sensor)
                print(intervall)
                
                with open("framework_data.json", "r") as jsonFile:
                    data = json.load(jsonFile)
                    
                data["sensors"][sensor]["sync_interval"] = intervall

                with open("framework_data.json", "w") as jsonFile:
                    json.dump(data, jsonFile)
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

        response = {
            'path': self.path,
            'get_vars': str(getvars)
            #'get_vars': str(postvars)
        }

        self.wfile.write(bytes(json.dumps(response), 'utf-8'))

    def _parse_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            postvars = cgi.parse_qs(
                self.rfile.read(length), keep_blank_values=1)
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
    server = CustomHTTPServer(('192.168.0.133', 8888))
    server.set_auth('demo', 'demo')
    server.serve_forever()
    print("server läuft")