import time
import psutil
import json
import requests


ip_address = requests.get('https://api.ipify.org').text
processes_dict_list = []


def get_processes():
    tid = str(time.time()).split('.')[0]
    for proc in psutil.process_iter():
        try:
            processes_dict_list.append(proc.as_dict())
            tmp = proc.as_dict()
            if tmp['username'] != 'root':
                print('hej')
        except (psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess):
            pass
    print('Processes: ', tid)


def send_node_status(json_object):
    url = "node-status"
    headers = {'Content-type': 'application/json',
               'Accept': 'text/plain',
               'auth-token': 'testtoken',
               'nodeid': 'testid',
               'ip-address': str(ip_address)}
    r = requests.post(url, json=json_object, headers=headers)
    print(r.status_code)


def send_processes_list():
    json_object = json.dumps(processes_dict_list)
    send_node_status(json_object)
    processes_dict_list.clear()


if __name__ == '__main__':
    print('Main')
    get_processes()
    for i in range(len(processes_dict_list)):
        print(processes_dict_list[i])
