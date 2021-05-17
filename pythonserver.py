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

import find_and_connect_ble_device
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
        response = {
                        'success': False
                    }
        
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
            
            elif base_path == '/change_sensor':
                    
                sensor_id = self.get_Postvar(p, "sensor_id")
                sync_interval = self.get_Postvar(p, "sync_interval")
                sensor_new_name = self.get_Postvar(p, "sensor_new_name")
                
                if sensor_id == None:
                    response = {
                    'success': False,
                    'Ursache': "Kein Sensor angegeben"
                    }
                    
                else:
                    print("sensor_id: " + sensor_id)
                    with open(globalvars.path_to_framework_data_json, "r") as jsonFile:
                        data = json.load(jsonFile)
                        
                    if sync_interval != None:
                        data["sensors"][sensor_id]["sync_interval"] = sync_interval
                        print("new sync_interval: " + sync_interval)
                        
                    if sensor_new_name != None:
                        data["sensors"][sensor_id]["sensor_name"] = sensor_new_name
                        print("new sensor_name: " + sensor_new_name) 
                    
                

                    with open(globalvars.path_to_framework_data_json, "w") as jsonFile:
                        json.dump(data, jsonFile)
                
                
                #self.wfile.write(bytes(json.dumps(response), 'utf-8'))
                pass
            elif base_path == '/change_ud':
                
                
                old_un = self.get_Postvar(p, "old_un")
                new_un = self.get_Postvar(p, "new_un")
                old_pw = self.get_Postvar(p, "old_pw")
                new_pw = self.get_Postvar(p, "new_pw")
                    
                
                with open(globalvars.path_to_password_json, "r") as jsonFile:
                    data = json.load(jsonFile)
                    
                if old_un != None and new_un != None:
                    if data["username"] == old_un:
                        data["username"] = new_un
                        print("Neuer Username: " + new_un)
                    
                if old_pw != None and new_pw != None:
                    if data["password"] == old_pw:
                        data["password"] = new_pw
                        print("Neues Passwort: " + new_pw)

                with open(globalvars.path_to_password_json, "w") as jsonFile:
                    json.dump(data, jsonFile)
                    
                    response = {
                        'success': True
                    }
                    
                    self.wfile.write(bytes(json.dumps(response), 'utf-8'))
                    _thread.start_new_thread(start_server, ())
                    
                    sys.exit()
                    
            elif base_path == '/search_bluetooth-devices':
                
                json_data = find_and_connect_ble_device.search_ble_devices()
                
                response = {
                            'success': True,
                            'data': json_data
                        }
                
                pass
            
            elif base_path == '/read_serial_address':
                
                json_data = find_and_connect_ble_device.read_ble_serial()
                if json_data != False:
                    response = {
                                'success': True,
                                'data': json_data
                            }
                else:
                    response = {
                                'success': False,
                                'Ursache': 'kein Sensor verbunden'
                            }
                pass
            
            elif base_path == '/add_sensor':
                
                address = self.get_Postvar(p, "address")
                address = address.replace("%3A",":")
                new_name = self.get_Postvar(p, "new_name")
                
                if find_and_connect_ble_device.add_device_bluetoothctl(address) == True:
                    find_and_connect_ble_device.add_device_json(address, new_name)
                    response = {
                        'success': True
                    }
                
                pass
            
            elif base_path == '/remove_sensor':
                
                device_id = self.get_Postvar(p, "device_id")
                
                if find_and_connect_ble_device.delete_device_bluetoothctl(device_id) == True:
                    find_and_connect_ble_device.delete_device_json(device_id)
                    response = {
                        'success': True,
                    }
                
                pass
            
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
    print("Username: "+data["username"])
    print("Passwort: "+data["password"])
    
    server.socket = ssl.wrap_socket(server.socket,
                                    server_side=True,
                                    certfile='SSL/cert.pem',
                                    keyfile='SSL/key.pem',
                                    ssl_version=ssl.PROTOCOL_TLS)
    
    print(Fore.MAGENTA + "Webserver: Server läuft und ist über folgende Adresse erreichbar: "+IPAdresse+":"+str(Port))
    server.serve_forever()
    