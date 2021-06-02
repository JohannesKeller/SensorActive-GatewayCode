import requests
import json
from urllib3.exceptions import InsecureRequestWarning

class postandsync:
        
    def post_data_to_database(m5stack, nano_gekuerzt, measurement, value):
        global beacon_addr
        global timestamp_lost_connection
        
        data_string=m5stack.Device_name + ",beacon_name="+m5stack.Name+",measurement=" + measurement + " value=" + str(value) + " " + str(nano_gekuerzt)
        requests.post(m5stack.Local_addr, data=data_string)
        try:
            print("wird gepostet")
            url = 'https://sensoractive.ddnss.de:8086/api/v2/write?org=SensorActive&bucket=GatewayData&precision=ms'
            body = str(str(data_string)[:-6])
            print(body)
            headers = {'Authorization': 'Token 5wVhu0xvugVDSeH7S-cYJCUapMnQ_3eiufZ2tStC85_aspjDklV9-KnGssO7HXY24lMC0HigWXfoOAeKSAfcfA=='}

            requests.post(m5stack.Global_addr, data=body, headers=headers)
            
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
            #print("Keine Verbindung")
            if m5stack.connected_to_server == True:
                m5stack.timestamp_lost_connection = nano_gekuerzt
            m5stack.connected_to_server = False