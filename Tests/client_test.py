from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# You can generate a Token from the "Tokens Tab" in the UI
token = "biT7eNSPtoDh3uNlx_sFqPDAPcDDhjeYWpHJPprUF3CsQiYPQW0T-pzeSd0bX9IS8DxmtYsU067Ypr6dLcp7VA=="
org = "SensorActive"
bucket = "Bucket1"

client = InfluxDBClient(url="http://192.52.37.249:8086", token=token)


write_api = client.write_api(write_options=SYNCHRONOUS)

data = "raspberry1,beacon_name=m5stack1,measurement=rssi value=-50 1608145928210000000"
write_api.write(bucket, org, data)