from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# You can generate a Token from the "Tokens Tab" in the UI
token = "5wVhu0xvugVDSeH7S-cYJCUapMnQ_3eiufZ2tStC85_aspjDklV9-KnGssO7HXY24lMC0HigWXfoOAeKSAfcfA=="
org = "SensorActive"
bucket = "GatewayData"

client = InfluxDBClient(url="https://sensoractive.ddnss.de:8086", token=token)


write_api = client.write_api(write_options=SYNCHRONOUS)

data = "raspberry1,beacon_name=m5stack1,measurement=rssi value=-50 1608145928210000000"
write_api.write(bucket, org, data)