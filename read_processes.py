import time
import psutil
import json
import requests

import cyclic_executive


ip_address = requests.get('https://api.ipify.org').text
processes_dict_list = []


def get_processes():
    tid = str(time.time()).split('.')[0]
    for proc in psutil.process_iter():
        try:
            processes_dict_list.append(proc.as_dict())
        except (psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess):
            pass


def send_node_status(json_object):
    url = "http://127.0.0.1:5000/sendtohost"
    headers = {'Content-type': 'application/json',
               'Accept': 'text/plain',
               'auth-token': 'testtoken',
               'package_type': '3',
               'nodeid': 'testid',
               'ip-address': str(ip_address)}
    r = requests.post(url, json=json_object, headers=headers)
    print(r.status_code)


def send_processes_list():
    json_object = json.dumps(processes_dict_list)
    # print(json_object)
    send_node_status(json_object)
    processes_dict_list.clear()


if __name__ == '__main__':
    cyclic = cyclic_executive.CyclicExecutive(verbosity=1,
                                              function='get_resources')

    while True:
        cyclic.run()
