import pexpect
import time
import globalvars
import json

import serial


def search_ble_devices():
    with open(globalvars.path_to_framework_data_json, 'r') as f:
        json_data = json.load(f)        
    
    ble_devices = []
    line_output = []
    while globalvars.bluetooth_free == False:
        print("warte bis bluetooth frei ist...")
        time.sleep(1)
    globalvars.bluetooth_free = False
    x=0
    p=False
    child = pexpect.spawn('bluetoothctl')
    child.sendline ('scan on')
    time.sleep(3)
    child.sendline ('quit')
    globalvars.bluetooth_free = True
    while p == False:
        line = child.readline().decode("utf-8")
        line_output.append(line)
        #print(line)
        if "quit" in line:
            p=True
    
    for l in line_output:
        if "] Device " in l:
            l = l.split("] Device ")
            l = l[1].split(" ")
            device = l[0]
            print("alle devices: "+device)
            pruefer = True
            
            for x in ble_devices:
                if x == device:
                    pruefer = False
                    
            for device_known in json_data["sensors"]:
                if json_data["sensors"][device_known]["sensor_bluetooth_adress"] == device:
                    pruefer = False
                    
            if pruefer == True:
                ble_devices.append(device)
    
    
    json_file =""
    counter=0
    for x in ble_devices:
        if counter>0:
            json_file = json_file +","
        json_file = json_file + x
        print("nutzbare devices: "+x)
        counter=counter+1
        
    json_file = {"bluetooth_devices":{json_file}}
    print(json_file)
            
            
def read_ble_serial():
    port = serial.Serial("/dev/ttyUSB0", baudrate=115200, timeout=3.0)
    
    while True:
        address = port.read(33)
        address = address.decode('utf-8')
        print(address)
        
        if "b_address:(" in address and "):end" in address:
            address = address.split("b_address:(")
            address = address[1].split("):end")
            address = address[0]
            print(address)
            return address
        
def add_device(address):
    while globalvars.bluetooth_free == False:
        print("warte bis bluetooth frei ist...")
        time.sleep(1)
    globalvars.bluetooth_free = False
    child = pexpect.spawn('bluetoothctl')
    child.sendline ('scan on')
    time.sleep(3)
    child.sendline ('pair '+address)
    time.sleep(2)
    child.sendline ('quit')
    globalvars.bluetooth_free = True
    p=False
    while p == False:
        line = child.readline().decode("utf-8")
        print(line)
        if "quit" in line:
            p=True
        #if "not available" in line:
         #   p=True
    

add_device("84:CC:A8:5E:8C:22")
#read_ble_serial()
#search_ble_devices()