import time
import psutil
import json
import requests
import argparse

import cyclic_executive


ip_address = requests.get('https://api.ipify.org').text
processes_dict_list = []


def arg_parsing():
    parser = argparse.ArgumentParser(prog='Read Processes',
                                     description='Read Processes running.')
    parser.add_argument('-c', '--cycle-duration', type=int, default=5,
                        help='How often processes should be read.')
    parser.add_argument('-s', '--send-frequency', type=int, default=6,
                        help='How many times processes should be read '
                             'before sent.')
    parser.add_argument('-v', '--verbosity', action='count', default=0,
                        help='Increase output verbosity.')

    args = parser.parse_args()

    return args


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

    args = arg_parsing()

    verbosity = 1 if args.verbosity != 0 else args.verbosity

    cyclic = cyclic_executive.CyclicExecutive(verbosity=verbosity,
                                              cycle_duration=args.cycle_duration,
                                              send_frequency=args.send_frequency,
                                              func1='get_resources',
                                              func2='send_processes_list')

    while True:
        cyclic.run()