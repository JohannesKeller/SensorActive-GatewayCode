import requests
import json
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

url = 'https://192.52.39.198:8086/api/v2/write?org=HFU&bucket=Bucket1&precision=ms'
body = 'cpu_load_short,host=server01,region=us-west value=0.64'
headers = {'Authorization': 'Token C3_mDVcsHuJjCqz7PZDy9OBc6N0HvjGTBJWbWOtgAiQREOVa71twQ77gR4z3p_aUT76ekULt50e7U4PiBEmeuA=='}

requests.post(url, data=body, headers=headers, verify=False)