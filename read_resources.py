import time
import psutil
import json
import requests
import argparse
import sys

import cyclic_executive


ip_address = requests.get('https://api.ipify.org').text
resources_dict_list = []


def arg_parsing():
    parser = argparse.ArgumentParser(prog='Read Resources',
                                     description='Read current resource usage.')
    parser.add_argument('-c', '--cycle-duration', type=int, default=5,
                        help='How often resources should be read.')
    parser.add_argument('-s', '--send-frequency', type=int, default=6,
                        help='How many times resources should be read '
                             'before sent.')
    parser.add_argument('-v', '--verbosity', action='count', default=1,
                        help='Increase output verbosity.')

    return parser.parse_args()


def get_resources():
    tid = str(time.time()).split('.')[0]
    status_struct = {'timestamp': tid,
                     'CPU%': str(psutil.cpu_percent()),
                     'RAM% ': str(psutil.virtual_memory().percent)}
    # Bandwith not included atm.
    print(status_struct)
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
    print(json_object)
    send_node_status(json_object)
    resources_dict_list.clear()


if __name__ == '__main__':

    args = arg_parsing()

    verbosity = 1 if args.verbosity != 0 else args.verbosity
    functions = [sys.modules[__name__], 'get_resources', 'send_resources_list']
    cyclic = cyclic_executive.CyclicExecutive(verbosity=verbosity,
                                              cycle_duration=args.cycle_duration,
                                              send_frequency=args.send_frequency,
                                              functions=functions)

    while True:
        cyclic.run()
