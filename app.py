from copy import deepcopy
from flask import Flask
from flask import request
from raft import raft
import requests
import concurrent.futures
import hashlib
import base64
import json
import argparse
import os

app = Flask(__name__)


def arg_parsing():
    parser = argparse.ArgumentParser(prog='Read Packets',
                                     description='Read Network Packets')
    parser.add_argument('-i', '--ip-address',
                        help='IP Address of the current node.')
    parser.add_argument('-c', '--cluster-id', type=int,
                        help='ID of the cluster the current node is in.')
    parser.add_argument('-p', '--port', type=int,
                        help='The port the current node is using.')
    parser.add_argument('-v', '--verbosity', type=int, default=0,
                        help='Increase output verbosity.')

    return parser.parse_args()


def check_headers(headers):
    if int(headers['term']) < int(node.term):
        return False
    if int(headers['term']) > int(node.term):
        if node.verbosity == 1:
            print(node.ip, ' were ', node.status,
                  ' and had lower term limit'
                  ' than sender and became follower.')
        node.become_follower()
        node.update_term(int(headers['term']))
    if headers['status'] == 'Leader':
        node.leader_ip = headers['ip_address']

    return True


def unpack_and_send(queue):
    """
    Unpacks a send_queue and sends it to GCP
    :param queue: A send_queue from a follower
    :return: Nothing
    """
    resources_status = None
    packages_status = None
    processes_status = None
    resources_hash_status = None
    packages_hash_status = None
    processes_hash_status = None
    resources = []
    packages = []
    processes = []

    for item in queue:
        if item[0]['package_type'] == '1':
            resources.append(item)
        elif item[0]['package_type'] == '2':
            packages.append(item)
        elif item[0]['package_type'] == '3':
            processes.append(item)

    if resources:
        b64 = base64.encodebytes(json.dumps(resources).encode())
        hashed_resources = hashlib.sha256(b64).hexdigest()
        resources_hash_status = check_hash(resources[0][0], hashed_resources)

    if packages:
        b64 = base64.encodebytes(json.dumps(packages).encode())
        hashed_packages = hashlib.sha256(b64).hexdigest()
        packages_hash_status = check_hash(packages[0][0], hashed_packages)

    if processes:
        b64 = base64.encodebytes(json.dumps(processes).encode())
        hashed_processes = hashlib.sha256(b64).hexdigest()
        processes_hash_status = check_hash(processes[0][0], hashed_processes)

    if resources_hash_status == 200:
        resources_status = send_to_gcp(resources[0][0], resources)
        send_hash(hashed_resources)

    if packages_hash_status == 200:
        packages_status = send_to_gcp(packages[0][0], packages)
        send_hash(hashed_packages)

    if processes_hash_status == 200:
        processes_status = send_to_gcp(processes[0][0], processes)
        send_hash(hashed_processes)

    if ((resources_status == 200 or resources_status is None) and (packages_status == 200 or packages_status is None)) or ((resources_hash_status == 1 or resources_hash_status is None) and (packages_hash_status == 1 or packages_hash_status is None)):
        url = 'http://' + queue[0][0]['ip_address'] + ':' + node.port + '/datasent'
        print("data sent response sent to " + url)
        headers = {'leader_ip_address': node.ip}

        r = requests.get(url, headers=headers)
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
    print(type(r.status_code))
    if r.status_code == 409:
        print('Already in database')
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
    elif old_headers['package_type'] == '3':
        url = 'http://95.179.226.113:5000/node-processess'

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


@app.route('/')
def index():
    return 'Server Works!'


# Leader endpoints
@app.route('/sendtohost', methods=['POST', 'GET'])
def send_data():
    """
    Calls unpack_and_send in another thread until the leader_queue is empty
    :return: 'ok'
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        while node.leader_queue:
            executor.submit(unpack_and_send, node.leader_queue.pop(0))

    return 'ok'


@app.route('/storeleaderdata', methods=['POST'])
def store_leader_data():
    """
    Stores the send_queues from followers in a leader_queue
    :return: 'ok'
    """
    r = request.get_json()
    node.leader_queue.append(r)
    return 'ok'


# Follower endpoints
@app.route('/sendtoleader', methods=['POST', 'GET'])
def leader_send():
    """
    Copies main_queue to send_queue and sends it to Leader
    :return: If data is sent to leader
    """
    if check_headers(request.headers):
        if node.verbosity == 1:
            print('Heartbeat from: ' + request.headers['ip_address'])
        node.set_timer()

        if not node.send_queue:
            node.send_queue.append(deepcopy(node.main_queue))
            # print(node.send_queue)
            node.main_queue.clear()

        headers = {
            'local_ip_address': request.url_root + 'datasent'
        }
        leader_url = 'http://' + node.leader_ip + ':5000/storeleaderdata'
        r = requests.post(leader_url, json=node.send_queue[0],
                          headers=headers)
        if r.status_code == 200:
            return 'Data Sent to Leader'
        else:
            return 'Something went wrong sending the data, attempt to resend it'


@app.route('/datasent', methods=['GET'])
def data_sent_response():
    """
    Endpoint to tell follower data is sent to GCP, and can be deleted locally
    :return: "ok" if deleted, "Not leader" if called from follower node
    """
    print('Data is sent')
    if request.headers['leader_ip_address'] == node.leader_ip:
        node.send_queue.clear()
        json_object = {'message': 'ok'}
    else:
        json_object = {'message': 'Not leader'}
    return json_object


@app.route('/storedata', methods=['POST'])
def information_queue():
    """
    Stores data collected by read scripts
    :return: "Data appended"
    """
    temp_request = [{
        'package_type': request.headers['package_type'],
        'nodeid': node.ip,
        'ip_address': node.ip,

    }, request.get_json()]

    node.main_queue.append(temp_request)
    return 'Data Appended'


# Voting function
@app.route('/requestvote', methods=['GET'])
def request_vote():
    if node.verbosity == 1:
        print('Vote request received')
    if check_headers(request.headers):
        if node.voted is False and node.status == 'Follower':
            node.voted = True
            node.set_timer()
            return '1'
    return '0'


if __name__ == '__main__':
    args = arg_parsing()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        if args.verbosity == 1:
            print('Initializing Node')
        os.system("python3 read/read_packets.py -i \"eth0\" -a " + str(args.ip_address) + " -p " + str(args.port) + " &")
        os.system("python3 read/read_resources.py -i " + str(args.ip_address) + " -p " + str(args.port) + " &")
        node = raft.Node(executor, args)
        #executor.submit(node.timer)
        if args.verbosity == 1:
            print('Initializing done')
        app.debug = False
        app.run(host=node.ip, port=node.port)
