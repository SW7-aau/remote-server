import schedule
import time
import psutil
import json
import requests
import socket

ip_address = requests.get('https://api.ipify.org').text

status_struct_list = []
SECONDS_BEFORE_COMMIT = 5

def read_status():
    status_struct = {}
    status_struct['timestamp'] = str(time.time()).split('.')[0]
    status_struct['CPU%'] = str(psutil.cpu_percent(interval=None, percpu=False))
    status_struct['RAM% '] = str(psutil.virtual_memory().percent)
    # Bandwith not included atm.
    status_struct_list.append(status_struct)
    
def send_node_status(json_object):
    url = "node-status"
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'auth-token': 'testtoken', 'nodeid': 'testid', 'ip-address': str(ip_address)}
    r = requests.post(url, json=json_object, headers=headers)
    print(r.status_code)

def send_status_list():
    json_object = json.dumps(status_struct_list)
    send_node_status(json_object)

    status_struct_list.clear()

schedule.every(1).second.do(read_status)
schedule.every(SECONDS_BEFORE_COMMIT).seconds.do(send_status_list)

while True:
    schedule.run_pending()
    time.sleep(1)

