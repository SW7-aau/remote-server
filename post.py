import requests
import argparse

def arg_parsing():
    parser = argparse.ArgumentParser(prog='Read Packets',
                                     description='Read Network Packets')
    parser.add_argument('-i', '--ip-address',
                        help='IP Address of the current node.')
    return parser.parse_args()

args = arg_parsing()

d = {
    '172.17.0.3': '0',
    '172.17.0.4': '0',
    '172.17.0.5': '0',
    '172.17.0.6': '0',
    '172.17.0.7': '0'
}

url = 'https://' + str(args.ip_address) + ':5000/updateconfig'

r = requests.post(url=url, json=d)