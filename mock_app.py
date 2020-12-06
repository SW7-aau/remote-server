from copy import deepcopy 
import mock_river
import concurrent.futures
import hashlib
import base64
import json
import argparse
import mock_nodes

class requests():
    def post(self, url, json, headers):
        print()
    def get(self, url, json, headers)
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
requests = requests()
with concurrent.futures.ThreadPoolExecutor() as executor:
    node = mock_river.Node(executor, args)

def send_data():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        while node.leader_queue:
            executor.submit(unpack_and_send, node.leader_queue.pop(0))

    return 'ok'

def unpack_and_send(queue):
    """
    Unpacks a send_queue and sends it to GCP
    :param queue: A send_queue from a follower
    :return: Nothing
    """
    resources_status = None
    packages_status = None
    resources_hash_status = None
    packages_hash_status = None
    resources = []
    packages = []

    for item in queue:
        if item[0]['package_type'] == '1':
            resources.append(item)
        elif item[0]['package_type'] == '2':
            packages.append(item)

    if resources:
        b64 = base64.encodebytes(json.dumps(resources).encode())
        hashed_resources = hashlib.sha256(b64).hexdigest()
        resources_hash_status = check_hash(resources[0][0], hashed_resources)

    if packages:
        b64 = base64.encodebytes(json.dumps(packages).encode())
        hashed_packages = hashlib.sha256(b64).hexdigest()
        packages_hash_status = check_hash(packages[0][0], hashed_packages)

    if resources_hash_status == 200:
        resources_status = send_to_gcp(resources[0][0], resources)
        send_hash(hashed_resources)

    if packages_hash_status == 200:
        packages_status = send_to_gcp(packages[0][0], packages)
        send_hash(hashed_packages)

    if ((resources_status == 200 or resources_status is None) and (packages_status == 200 or packages_status is None)) or ((resources_hash_status == 1 or resources_hash_status is None) and (packages_hash_status == 1 or packages_hash_status is None)):
        url = 'http://' + queue[0][0]['ip_address'] + ':' + node.port + '/datasent'
        print("data sent response sent to " + url)
        headers = {'leader_ip_address': node.ip}

        r = requests.get(url, headers=headers)
        if args.verbosity == 2:
            print(r)
        if r.json()['message'] != 'ok':
            print('Not leader')


def check_hash(old_headers, message):
    """
    Checks if the hash is already in the database at GCP
    :param old_headers: Headers from the send_queue
    :param message: A hashed version of the send_queue
    :return: status_code from the request if successful, 1 if hash exists in
     database, 0 if access token has expired
    """

    url = "http://95.179.226.113:5000/check-hash"  # node hash url
    headers = {'Content_Type': 'application/json',
               'Accept': 'text/plain',
               'access_token': node.token,
               'cluster_id': node.cluster_id
               }

    r = requests.post(url, json=message, headers=headers)

    if r.status_code == 409:
        return 1
    if r.json()['message'] == 'ok':
        return r.status_code
    elif r.json()['message'] == 'Authorization token is expired':
        node.get_auth_token()
        return 0
    elif r.json()['message'] == 'Not authorized':
        node.become_follower()
        return 0

def send_hash(message):
    url = "http://95.179.226.113:5000/insert-hash"
    headers = {'Content_Type': 'application/json',
               'Accept': 'text/plain',
               'access_token': node.token,
               'cluster_id': node.cluster_id
               }

    r = requests.post(url, json=message, headers=headers)

    if r.json()['message'] != 'ok':
        node.get_auth_token()
        return 0

    return r.status_code

def send_to_gcp(old_headers, message):
    """
    Sends the send_queue to GCP
    :param old_headers: Headers from the send_queue
    :param message: The data to be stored in the database
    :return: status_code from the request
    """
    if old_headers['package_type'] == '1':
        url = 'http://95.179.226.113:5000/node-resources'
    elif old_headers['package_type'] == '2':
        url = 'http://95.179.226.113:5000/node-network'

    else:
        return

    print('Sent to: ', old_headers['package_type'])
    headers = {'Content_Type': 'application/json',
               'Accept': 'text/plain',
               'access_token': node.token,
               'cluster_id': node.cluster_id
               }
    r = requests.post(url, json=message, headers=headers)

    if r.json()['message'] == 'ok':
        return r.status_code
    elif r.json()['message'] == 'Authorization token is expired':
        node.get_auth_token()
        return 0
    elif r.json()['message'] == 'Not authorized':
        node.become_follower()
        return 0


