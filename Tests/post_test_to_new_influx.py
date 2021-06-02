import requests
import json
from urllib3.exceptions import InsecureRequestWarning



url = 'https://sensoractive.ddnss.de:8086/api/v2/write?org=SensorActive&bucket=GatewayData&precision=ms'
body = 'raspberry1,beacon_name=eins,measurement=hum value=413.00'
headers = {'Authorization': 'Token 5wVhu0xvugVDSeH7S-cYJCUapMnQ_3eiufZ2tStC85_aspjDklV9-KnGssO7HXY24lMC0HigWXfoOAeKSAfcfA=='}

requests.post(url, data=body, headers=headers)