from copy import deepcopy

from flask import Flask
from flask import request
import requests
import concurrent.futures
import hashlib
import base64
import json

app = Flask(__name__)


main_queue = []
send_queue = []
leader_queue = []
client_secret = '506c8044e28cbc71e989a1d9885d0e'
client_id = '6e9fe75e4263ee84a4cadc1674182f'
global token


# Leader functions
def get_auth_token(ip_address):
    """
    Used to get access token from GCP
    :param ip_address: An IP Address used for generating access token
    :return: Sets global token to returned access token
    """
    global token
    client_creds = f'{client_id}:{client_secret}'
    client_creds_b64 = base64.b64encode(client_creds.encode()).decode()

    refresh_token = b'sw7 server monitoring'
    refresh_token = hashlib.sha512(refresh_token).hexdigest()
    refresh_token = f'Bearer {refresh_token}'

    grant_type = 'refresh_token'

    token_data = {
        'grant_type': grant_type,
        'refresh_token': refresh_token
    }
    token_headers = {
        'Authorization': client_creds_b64,
        'nodeid': 'test_id',
        'ip_address': ip_address,
        'package_type': '1'
    }
    url = "http://217.69.10.141:5000/token"

    r = requests.post(url=url, data=token_data, headers=token_headers)

    tmp = r.json()['access_token']
    token = f'Bearer {tmp}'


def unpack_and_send(queue):
    """
    Unpacks a send_queue and sends it to GCP
    :param queue: A send_queue from a follower
    :return: Nothing
    """
    resources_status = 0
    packages_status = 0
    processes_status = 0
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

    get_auth_token('fak')
    b64 = base64.encodebytes(json.dumps(resources).encode())
    hashed_resources = hashlib.sha256(b64).hexdigest()

    b64 = base64.encodebytes(json.dumps(packages).encode())
    hashed_packages = hashlib.sha256(b64).hexdigest()

    b64 = base64.encodebytes(json.dumps(processes).encode())
    hashed_processess = hashlib.sha256(b64).hexdigest()

    print(str(hashed_resources))
    resources_hash_status = send_hash(resources[0][0], hashed_resources)
    packages_hash_status = send_hash(packages[0][0], hashed_packages)
    processes_hash_status = send_hash(processes[0][0], hashed_processess)

    if resources_hash_status == 200:
        resources_status = send_node_status(resources[0][0], resources)

    if packages_hash_status == 200:
        packages_status = send_node_status(packages[0][0], packages)

    if processes_hash_status == 200:
        processes_status = send_node_status(processes[0][0], processes)

    if (resources_status & packages_status & processes_status == 200) | (resources_hash_status & packages_hash_status & processes_hash_status == 1):
        url = request.headers['local_ip_address']
        print("data sent response sent to " + url)
        headers = {'leader_ip_address': request.url_root}

        r = requests.get(url, headers=headers)

        if r.json()['message'] != 'ok':
            print('Not leader')


def send_hash(old_headers, message):
    """
    Sends a hashed version of the data to GCP to check if it is already there
    :param old_headers: Headers from the send_queue
    :param message: A hashed version of the send_queue
    :return: status_code from the request if successful, 1 if hash exists in
     database, 0 if access token has expired
    """
    print('in here')
    url = "http://217.69.10.141:5000/node-hash" #node hash url
    headers = {'Content_Type': 'application/json',
               'Accept': 'text/plain',
               'access_token': token
               }
    
    r = requests.post(url, json=message, headers=headers)
    print(r.json())
    if r.json()['message'] == 'ok':
        return r.status_code
    elif r.json()['message'] == 'token_expired':
        get_auth_token(old_headers['ip_address'])
        return 0
    elif r.json()['message'] == 'hash_exists':
        return 1


def send_node_status(old_headers, message):
    """
    Sends the send_queue to GCP
    :param old_headers: Headers from the send_queue
    :param message: The data to be stored in the database
    :return: status_code from the request
    """
    if old_headers['package_type'] == '1':
        url = "http://217.69.10.141:5000/node-status"
    elif old_headers['package_type'] == '2':
        url = "http://217.69.10.141:5000/node-network"
    elif old_headers['package_type'] == '3':
        url = "http://217.69.10.141:5000/node-processess"
    else:
        return

    print('Sent to: ', old_headers['package_type'])
    headers = {'Content_Type': 'application/json',
               'Accept': 'text/plain',
               'access_token': token
               }
    r = requests.post(url, json=message, headers=headers)

    if r.json()['message'] != 'ok':
        get_auth_token(old_headers['ip_address'])
        return 0

    return r.status_code


@app.route('/')
def index():
    return 'Server Works!'


# Leader endpoints
@app.route('/sendtohost', methods=['POST', 'GET'])
def send_data():
    """
    Calls unpack_and_send in another thread until the leader_queue is empty
    :return: "ok"
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        while leader_queue:
            executor.submit(unpack_and_send, leader_queue.pop(0))

    return "ok"


@app.route('/storeleaderdata', methods=['POST'])
def store_leader_data():
    """
    Stores the send_queues from followers in a leader_queue
    :return: "ok"
    """
    r = request.get_json()
    leader_queue.append(r)
    return 'ok'


# Follower endpoints
@app.route('/sendtoleader', methods=['POST', 'GET'])
def leader_send():
    """
    Copies main_queue to send_queue and sends it to Leader
    :return: If data is sent to leader
    """
    if not send_queue:
        send_queue.append(deepcopy(main_queue))
        main_queue.clear()

    headers = {
        'local_ip_address': request.url_root + "datasent"
    }
    leader_url = 'http://172.17.0.9:5000/storeleaderdata'
    r = requests.post(leader_url, json=send_queue[0], headers=headers)  # TODO retrieve leader url from election guys
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
    if request.headers['leader_ip_address'] == 'http://172.17.0.9:5000/':  # TODO retrieve leader url from election guys
        send_queue.clear()
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
        'nodeid': request.headers['nodeid'],
        'ip_address': request.headers['ip_address'],

    }, request.get_json()]

    main_queue.append(temp_request)
    return 'Data Appended'


if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port=5002)

