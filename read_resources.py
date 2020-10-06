import time
import psutil
import requests
import argparse
import sys

import cyclic_executive


ip_address = requests.get('https://api.ipify.org').text
resources_dict_list = []

#Scheduler options
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

#Reads the resource stats of the machine this application is running on.
def get_resources():
    timestamp = str(time.time()).split('.')[0]
    status_struct = {'timestamp': timestamp,
                     'CPU%': str(psutil.cpu_percent()),
                     'RAM%': str(psutil.virtual_memory().percent)}
    # Bandwith not included atm.
    print(status_struct)
    resources_dict_list.append(status_struct)

#Sends current recorded metrics to sidecar (I hope)
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
    return r.status_code

#Clears batch of metric reading after calling send_node_status
def send_resources_list():
    send_node_status(resources_dict_list)
    resources_dict_list.clear()


if __name__ == '__main__':

    args = arg_parsing()

    verbosity = 1 if args.verbosity != 0 else args.verbosity
    functions = [sys.modules[__name__], 'get_resources', 'send_resources_list']
    cyclic = cyclic_executive.CyclicExecutive(verbosity=verbosity,
                                              cycle_duration=args.cycle_duration,
                                              send_frequency=args.send_frequency,
                                              functions=functions)

    #Why do we have an infinite while loop here when the scheduler already has one?
    while True:
        cyclic.run()
