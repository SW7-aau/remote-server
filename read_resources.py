import time
import psutil
import json
import requests
import signal


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


def send_node_status(json_object):
    url = "http://127.0.0.1:5000/sendtohost"
    headers = {'Content-type': 'application/json',
               'Accept': 'text/plain',
               'auth-token': 'testtoken',
               'package_type': '1',
               'nodeid': 'testid',
               'ip-address': str(ip_address)}
    r = requests.post(url, json=json_object, headers=headers)
    print(r.status_code)


def send_resources_list():
    json_object = json.dumps(resources_dict_list)
    # print(json_object)
    send_node_status(json_object)
    resources_dict_list.clear()


def interrupt_handler(signum, frame):
    print('--- Interrupt ---')
    globals()['tasks_were_completed'] = False


def wait_for_interrupt(): # Not used
    globals()['tasks_were_completed'] = True
    # Do nothing until the end of this cycle
    while (tasks_were_completed):
        time.sleep(0)


def cyclic_executives():
    minor_cycle_duration = 5
    timer = 1
    signal.signal(signal.SIGALRM, interrupt_handler)
    print('Starting cycle...')
    while True:
        signal.alarm(minor_cycle_duration)
        get_resources()
        print("Resources read")
        if timer % 6 == 0:
            send_resources_list()
            print("Resources sent")
        timer = timer + 1
        wait_for_interrupt()


if __name__ == '__main__':
    cyclic_executives()

