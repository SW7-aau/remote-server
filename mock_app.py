from copy import deepcopy 
import mock_river
import concurrent.futures
import hashlib
import base64
import json
import argparse

class requests():
    def post(self, url="", json={}, headers={}):
        if url == "http://95.179.226.113:5000/check-hash":
            print()
        elif url == "http://95.179.226.113:5000/insert-hash":
            print()
        elif url == 'http://95.179.226.113:5000/node-resources':
            print()
        elif url == 'http://95.179.226.113:5000/node-network':
            print()
        return ""
    def get(self, url="", json={}, headers={}):
        print()
    class Response():
        def __init__(self, status_code):
            self.status_code = status_code

def arg_parsing():
    parser = argparse.ArgumentParser(prog='Read Packets',
                                     description='Read Network Packets')
    parser.add_argument('-i', '--ip-address',
                        help='IP Address of the current node.')
    parser.add_argument('-c', '--cluster-id', type=int,
                        help='ID of the cluster the current node is in.')
    parser.add_argument('-p', '--port', type=int,
                        help='The port the current node is using.')
    parser.add_argument('-v', '--verbosity', type=int, default=1,
                        help='Increase output verbosity.')

    return parser.parse_args()

args = arg_parsing()
request = requests()
with concurrent.futures.ThreadPoolExecutor() as executor:
    node = mock_river.Node(executor, args)

def information_queue(request):
    temp_request = [{
        'package_type': request.headers['package_type'],
        'nodeid': node.ip,
        'ip_address': node.ip,

    }, request.get_json()]

    if request.headers['package_type'] == '1':
        if not check_resources(request.get_json()):
            return 'Invalid Message'
    elif request.headers['package_type'] == '2':
        if not check_packets():
            return 'Invalid Message'
    else:
        return 'Invalid Package Type'

    node.main_queue.append(temp_request)
    return 'Data Appended'

### NEW FUNCTIONS ###
def check_resources(messages):
    for m in messages:
        if 'timestamp' in m and 'CPU%' in m and 'RAM%' in m:
            return True
        return False

def check_packets(messages):
    for m in messages:
        if m['protocol'] == 'TCP':
            if 'dst' in m and 'dst_resolved' in m and 'dst_port' in m and 'src' in m and 'src_resolved' in m and 'src_port' in m:
                return True
        if m['protocol'] == 'UDP':
            if 'dst' in m and 'dst_resolved' in m and 'dst_port' in m and 'src' in m and 'src_resolved' in m and 'src_port' in m and 'layer' in m:
                return True
        if m['protocol'] == 'IGMP':
            if 'dst' in m and 'dst_resolved' in m and 'src' in m and 'src_resolved' in m and 'layer' in m:
                return True
        return False


