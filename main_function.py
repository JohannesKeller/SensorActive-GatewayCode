from m5stack import m5Stack
import json
import _thread

with open('framework_data.json', 'r') as f:
    json_data = json.load(f)

for sensor in json_data["sensors"]:
    print(json_data["sensors"][sensor])
    
    M51 = m5Stack(json_data["sensors"][sensor]["sensor_bluetooth_adress"],
                  json_data["sensors"][sensor]["sensor_name"],
                  json_data["sensors"][sensor]["sync_interval"],
                  json_data["main_info"]["local_adress"],
                  json_data["main_info"]["global_adress"],
                  json_data["main_info"]["device_name"])
_thread.start_new_thread( M51.startup,() )
