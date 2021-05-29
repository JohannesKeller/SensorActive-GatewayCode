import pygatt
from binascii import hexlify
import time
import datetime

import _thread
import pexpect
import re
import sys
import json

from post_and_sync import postandsync
from colorama import init, Fore, Style

import globalvars

class m5Stack:
    
    def __init__(self, sensor_id, blu_addr, name, sync_interval, local_addr, global_addr, device_name):
        self.Sensor_id = sensor_id
        self.Blu_addr = blu_addr
        self.Name = name
        print(self.Name)
        self.Local_addr = local_addr
        self.Global_addr = global_addr
        self.Device_name = device_name
        self.Sync_interval = int(sync_interval)
        
        self.adapter = pygatt.GATTToolBackend()

        self.connected_to_server = True
        self.timestamp_lost_connection = 0
        self.device = 0
        self.alles_da = False

        self.getcounter = -1
        self.anzahlvongets = 0
        self.nano_gekuerzt = 0
        self.werte_array = []
        self.tmstmp_from_startup = 0

    

    def get_rssi_and_check_erreichbarkeit(self):
        x=0
        child = pexpect.spawn('bluetoothctl')
        child.sendline ('scan on')
        time.sleep(3)
        child.sendline ('quit')
        while x == 0:
            line = child.readline().decode("utf-8")
            if "] Device "+ str(self.Blu_addr) +" RSSI: " in line:
                line = re.sub('] Device '+ str(self.Blu_addr) +' RSSI: ', '', line)
                line = re.sub(r"\s+", "", line)
                line = str(line)
                starter = 38
                number = ""
                try:
                    while x== 0:
                        number = number + line[starter]
                        starter=starter+1
                except:
                    print(Fore.BLUE + "BLE: " + self.Name + " - konnte gefunden werden - RSSI: "+number)
                
                time_nanosec = int(time.time_ns())
                nano_gekuerzt2 = str(time_nanosec)[:-8]
                nano_gekuerzt2 = nano_gekuerzt2 + "10000000"
                try:
                    _thread.start_new_thread( postandsync.post_data_to_database, (self, nano_gekuerzt2, "rssi", number) )
                except:
                    print("nicht geklappt")
                return True
            if line == "":
                print(Fore.BLUE + "BLE: " + self.Name + " - konnte nicht gefunden werden")
                
                with open(globalvars.path_to_framework_data_json, "r") as jsonFile:
                    data = json.load(jsonFile)
                    
                    if data["sensors"][self.Sensor_id]["status"] == "on":
                        data["sensors"][self.Sensor_id]["status"] = "off"

                        with open(globalvars.path_to_framework_data_json, "w") as jsonFile:
                            json.dump(data, jsonFile)
                    
                return False
                x=1

    def handle_data(self, handle, value):
        global anzahlvongets
        global nano_gekuerzt
        global tmstmp_from_startup
        getstring = str(value, 'utf-8')
        
        self.getcounter=self.getcounter+1
        
        if self.getcounter == 0:
            anzahlvongets = int(getstring)
            time_nanosec = int(time.time_ns())
            nano_gekuerzt = str(time_nanosec)[:-8]
            nano_gekuerzt = nano_gekuerzt + "10000000"
        else:
            if self.getcounter == 1:
                tmstmp_helper = getstring + "000000"
                tmstmp_from_startup = int(nano_gekuerzt)-int(tmstmp_helper)
            else:
                splitted = getstring.split(",")
                splitted[0] = splitted[0] + "000000"
                splitted[0] = int(splitted[0]) + tmstmp_from_startup
                splitted[0] = str(splitted[0])[:-8]
                splitted[0] = splitted[0] + "10000000"
                self.werte_array.append(splitted)
                
                if anzahlvongets+1 == self.getcounter:
                    self.alles_da = True
                    print(Fore.BLUE + "BLE: " + self.Name + " - "+str(len(self.werte_array))+" Messwerte wurden übertragen")
                    #print(self.werte_array)
                    try:
                        for i in self.werte_array: 
                            #print(i)
                            try:
                                _thread.start_new_thread( postandsync.post_data_to_database, (self, i[0], i[1], i[2]) )
                            except:
                                print("nicht geklappt")
                    finally:
                        try:
                            _thread.start_new_thread( self.thread_2, ("Thread-1", 2, ) )
                        except:
                            print("nicht geklappt")
        
    def thread_1(self, threadName, delay):
        self.device.subscribe("beb5483e-36e1-4688-b7f5-ea07361b26a8", callback=self.handle_data)
        self.device.char_write("8eabbd4a-7220-4c74-af1d-b45e97317595", bytearray([0x6C])) #sendet "l" fuer listening
        
        
    def thread_2(self, threadName, delay):
        value = self.device.char_read("8eabbd4a-7220-4c74-af1d-b45e97317595")
        value = str(value, 'utf-8')
        if value == "s" and self.alles_da == True:
            #if self.getcounter != -1:
                self.device.char_write("8eabbd4a-7220-4c74-af1d-b45e97317595", bytearray([0x67])) #g
                
                ts = time.time()
                st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')
                print(Fore.BLUE + "BLE: " + self.Name + " - Übertragung abgeschlossen - " + st)
                with open(globalvars.path_to_framework_data_json, "r") as jsonFile:
                    data = json.load(jsonFile)
                    
                data["sensors"][self.Sensor_id]["last_succ_trans"] = st

                with open(globalvars.path_to_framework_data_json, "w") as jsonFile:
                    json.dump(data, jsonFile)
                
                self.getcounter=-1        
        elif value == "s" and self.alles_da == False:
            print(Fore.BLUE + "BLE: " + self.Name + " - Übertragung fehlgeschlagen")
            self.getcounter=-1
        
        self.device.unsubscribe("beb5483e-36e1-4688-b7f5-ea07361b26a8",)
        self.adapter.stop()
        globalvars.bluetooth_free = True;
        time.sleep(self.Sync_interval)
        self.startup()
            
    def startup(self):
        if(globalvars.bluetooth_free):
            self.werte_array = []
            globalvars.bluetooth_free = False;
            poster1 = postandsync()
            if self.get_rssi_and_check_erreichbarkeit():
                try:
                    self.getcounter = -1
                    self.adapter.start()
                    self.device = self.adapter.connect(self.Blu_addr)
                finally:
                    print(Fore.BLUE + "BLE: " + self.Name + " - erfolgreicher Verbindungsaufbau")
                    try:
                        _thread.start_new_thread( self.thread_1, ("Thread-1", 2, ) )
                    except:
                        print("nicht geklappt")
            else:
                globalvars.bluetooth_free = True;
                time.sleep(self.Sync_interval)
                self.startup()
        else:
            time.sleep(5)
            self.startup()
