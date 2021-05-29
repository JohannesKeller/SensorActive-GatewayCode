import pexpect
import time
import datetime
import globalvars
import json
from random import *
import serial

####################################################################
#                                                                  #
#                 FIND AND CONNECT A BLE-DEVICE                    #
#                                                                  #
####################################################################

####################################################################
#   searches for BLE-Devices within the bluetooth radius of the
#   Gateway. Returns a json-file with all available devices.
#   Already known devices are not returned.
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
            #print("alle devices: "+device)
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
        #print("nutzbare devices: "+x)
        counter=counter+1
        
    #json_file = {"bluetooth_devices":{json_file}}
    #print(json_file)
    return json_file

####################################################################
#   Reads the output of an Sensor which is connected to the usb-port
#   of the gateway. The bluetooth address of sensor can be cut out
#   of its output. Return is a String.
def read_ble_serial():
    try:
        port = serial.Serial("/dev/ttyUSB0", baudrate=115200, timeout=3.0)
        while True:
            address = port.read(33)
            address = address.decode('utf-8')
            #print(address)
            if "b_address:(" in address and "):end" in address:
                address = address.split("b_address:(")
                address = address[1].split("):end")
                address = address[0]
                #print(address)
                return address
    except:
        return False

####################################################################
#   This method pairs the gateway with a given bluetooth-address of
#   a sensor. If a sensor isn't paired it won't be possible to
#   exchange data with it. Returns True or False.
def add_device_bluetoothctl(address):
    with open(globalvars.path_to_framework_data_json, 'r') as f:
        json_data = json.load(f)
    pruefer = True
    for device_known in json_data["sensors"]:
        if json_data["sensors"][device_known]["sensor_bluetooth_adress"] == address:
            pruefer = False
    if pruefer == False:
        return False
    else:
        while globalvars.bluetooth_free == False:
            print("warte bis bluetooth frei ist...")
            time.sleep(1)
        globalvars.bluetooth_free = False
        child = pexpect.spawn('bluetoothctl')
        child.sendline ('scan on')
        time.sleep(1)
        child.sendline ('pair '+address)
        time.sleep(2)
        child.sendline ('quit')
        globalvars.bluetooth_free = True
        p=False
        while p == False:
            line = child.readline().decode("utf-8")
            #print(line)
            if "Connected: yes" in line:
                return True
            if "quit" in line:
                p=True
        return False

####################################################################
#   The opposite of the add_device_bluetoothctl-method. It removes
#   a given address from bluetooth.
def delete_device_bluetoothctl(device_id):
    try:
        with open(globalvars.path_to_framework_data_json, "r") as jsonFile:
            data = json.load(jsonFile)
        address = data["sensors"][device_id]["sensor_bluetooth_adress"]
        #print(address)
        while globalvars.bluetooth_free == False:
            print("warte bis bluetooth frei ist...")
            time.sleep(1)
        globalvars.bluetooth_free = False
        child = pexpect.spawn('bluetoothctl')
        child.sendline ('remove '+address)
        time.sleep(2)
        child.sendline ('quit')
        globalvars.bluetooth_free = True
        p=False
        while p == False:
            line = child.readline().decode("utf-8")
            #print(line)
            if "Device has been removed" in line:
                return True
            if "quit" in line:
                p=True
        return True
    except:
        return False

####################################################################
#   Adds an new device to the framework_data-json. So the gateway
#   can handle this new device. The method needs the bluetooth-
#   address of the new device and a name for it. This method
#   returns the id of the added sensor.
def add_device_json(address, new_name):
    with open(globalvars.path_to_framework_data_json, 'r') as f:
        json_data = json.load(f)
    l=False
    while l==False:
        l=True
        rand_id = str(randint(10000, 99999))
        for known_device_id in json_data["sensors"]:
            if known_device_id == rand_id:
                l=False
    #print(json_data)
    y = {rand_id:{}}
    json_data["sensors"].update(y)
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')
    y = {'sensor_name': new_name,
          'sensor_type': 'm5Stack',
          'sensor_bluetooth_adress': address,
          'helpCharacteristic_UUID': '8eabbd4a-7220-4c74-af1d-b45e97317595',
          'dataCharacteristic_UUID': 'beb5483e-36e1-4688-b7f5-ea07361b26a8',
          'sync_interval': '300',
          'status': 'on',
          'add_date': st,
          'last_succ_trans': ''}
    json_data["sensors"][rand_id].update(y)
    #print(json_data)
    with open(globalvars.path_to_framework_data_json, "w") as jsonFile:
        json.dump(json_data, jsonFile)
    return rand_id
        
####################################################################
#   Opposite of the add_device_json-method. Deletes a device out of
#   the json. The method needs the id which belongs to the device
#   in the json.
def delete_device_json(device_id):
    with open(globalvars.path_to_framework_data_json, 'r') as f:
        json_data = json.load(f)
    
    del json_data["sensors"][device_id]
    
    #print(json_data)
    with open(globalvars.path_to_framework_data_json, "w") as jsonFile:
       json.dump(json_data, jsonFile)