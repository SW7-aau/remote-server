import schedule
import time
import psutil
import json
import requests


ip_address = requests.get('https://api.ipify.org').text
resources_dict_list = []
SECONDS_BEFORE_COMMIT = 5


def get_resources():
    tid = str(time.time()).split('.')[0]
    status_struct = {'timestamp': tid,
                     'CPU%': str(psutil.cpu_percent()),
                     'RAM% ': str(psutil.virtual_memory().percent)}
    # Bandwith not included atm.
    resources_dict_list.append(status_struct)
    print('Resources: ', tid)


def send_node_status(json_object):
    url = "127.0.0.1:8080/sendtohost"
    headers = {'Content-type': 'application/json',
               'Accept': 'text/plain',
               'auth-token': 'testtoken',
               'msg_type': '1',
               'nodeid': 'testid',
               'ip-address': str(ip_address)}
    r = requests.post(url, json=json_object, headers=headers)
    print(r.status_code)


def send_resources_list():
    json_object = json.dumps(resources_dict_list)
    print("Sending")
    # send_node_status(json_object)
    resources_dict_list.clear()


if __name__ == '__main__':
    schedule.every(1).second.do(get_resources)
    schedule.every(SECONDS_BEFORE_COMMIT).seconds.do(send_resources_list)

    while True:
        schedule.run_pending()
        time.sleep(1)

