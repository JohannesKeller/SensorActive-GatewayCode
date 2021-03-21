import requests
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

class postandsync:
        
    def post_data_to_database(m5stack, nano_gekuerzt, measurement, value):
        global beacon_addr
        global timestamp_lost_connection
        
        headers = {'Authorization': 'Token C3_mDVcsHuJjCqz7PZDy9OBc6N0HvjGTBJWbWOtgAiQREOVa71twQ77gR4z3p_aUT76ekULt50e7U4PiBEmeuA=='}
        
        data_string=m5stack.Device_name + ",beacon_name="+m5stack.Name+",measurement=" + measurement + " value=" + str(value) + " " + nano_gekuerzt
        print("Lokal gepostet: "+data_string)
        requests.post(m5stack.Local_addr, data=data_string)
        
        try:
            
            token = "biT7eNSPtoDh3uNlx_sFqPDAPcDDhjeYWpHJPprUF3CsQiYPQW0T-pzeSd0bX9IS8DxmtYsU067Ypr6dLcp7VA=="
            org = "SensorActive"
            bucket = "Bucket1"
            client = InfluxDBClient(url="http://192.52.37.249:8086", token=token)
            write_api = client.write_api(write_options=SYNCHRONOUS)
            data = m5stack.Device_name + ",beacon_name="+m5stack.Name+" measurement=" + measurement + " value=" + str(value) + " " + nano_gekuerzt
            print(data)
            write_api.write(bucket, org, data_string)
            
            if m5stack.connected_to_server == False:
                secs = m5stack.timestamp_lost_connection / 1e9
                dt = datetime.datetime.fromtimestamp(secs)            
                formattet_time = dt.strftime('%Y-%m-%dT%H:%M:%SZ')            
                x = requests.get('http://localhost:8086/query?pretty=true&q=SELECT "value" FROM "raspberry1" WHERE time >= \'' + formattet_time + '\' AND "measurement" = \''+measurement+'\'&db=framework_measurements')
                data = x.json()
                lenght_of_json = len(data["results"][0]["series"][0]["values"])
                data_array = data["results"][0]["series"][0]["values"]
                
                for x in data_array:
                    what_we_get = str(x[0])
                    what_we_get_gekuertzt = what_we_get[:-2]
                    dt_obj = datetime.datetime.strptime(what_we_get_gekuertzt,'%Y-%m-%dT%H:%M:%S.%f')
                    
                    millisec = dt_obj.timestamp()*100
                    millisec = str(millisec)[:-3]
                    millisec = millisec + "10000000"
                    data_string=m5stack.Device_name + ",beacon_name="+beacon_name+",measurement=" + measurement + " value="+str(x[1])+" " + millisec
                    requests.post(m5stack.Global_addr, data=data_string)
                    
                m5stack.connected_to_server = True
        except:
            print("Keine Verbindung")
            if m5stack.connected_to_server == True:
                m5stack.timestamp_lost_connection = nano_gekuerzt
            m5stack.connected_to_server = False