from m5stack import m5Stack
#from pythonserver import CustomHTTPServer
import pythonserver
import json
import _thread
from colorama import init, Fore, Style
import time
import globalvars


_thread.start_new_thread(pythonserver.start_server, ())

with open(globalvars.path_to_framework_data_json, 'r') as f:
    json_data = json.load(f)

for sensor in json_data["sensors"]:
    #print(json_data["sensors"][sensor])
    
    M51 = m5Stack(json_data["sensors"][sensor]["sensor_bluetooth_adress"],
                  sensor,
                  json_data["sensors"][sensor]["sync_interval"],
                  json_data["main_info"]["local_adress"],
                  json_data["main_info"]["global_adress"],
                  json_data["main_info"]["device_name"])
    M52 = m5Stack(json_data["sensors"][sensor]["sensor_bluetooth_adress"],
                  "m5stack2",
                  json_data["sensors"][sensor]["sync_interval"],
                  json_data["main_info"]["local_adress"],
                  json_data["main_info"]["global_adress"],
                  json_data["main_info"]["device_name"])
    
    

#_thread.start_new_thread( M51.startup,() )
#  time.sleep(6)
#_thread.start_new_thread( M52.startup,() )