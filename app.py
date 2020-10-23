from copy import deepcopy

from flask import Flask
from flask import request
import requests
import concurrent.futures
import hashlib
import base64

app = Flask(__name__)


main_queue = []
send_queue = []
leader_queue = []
client_secret = '506c8044e28cbc71e989a1d9885d0e'
client_id = '6e9fe75e4263ee84a4cadc1674182f'
global token


def get_auth_token(ip_address):
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
    url = "http://127.0.0.1:5000/token"

    r = requests.post(url=url, data=token_data, headers=token_headers)

    token = r.json()['access_token']


def unpack_and_send(queue):
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

    if send_hash(resources[0][0], hashlib.sha256(resources).hexdigest()) == 200:
        resources_status = send_node_status(resources[0][0], resources)

    if send_hash(packages[0][0], hashlib.sha256(packages).hexdigest()) == 200:
        packages_status = send_node_status(packages[0][0], packages)

    if send_hash(processes[0][0], hashlib.sha256(processes).hexdigest()) == 200:
        processes_status = send_node_status(processes[0][0], processes)

    if resources_status & packages_status & processes_status == 200:
        url = request.headers['local_ip_address']
        print("data sent response sent to " + url)
        headers = {'leader_ip_address': request.url_root}

        r = requests.get(url, headers=headers)

        if r.json()['message'] != 'ok':
            print('Not leader')


def send_hash(old_headers, message):
    url = "http://217.69.10.141:5000/node-hash" #node hash url
    headers = {'Content_Type': 'application/json',
               'Accept': 'text/plain',
               'access_token': token
               }
    r = requests.post(url, json=message, headers=headers)

    if r.json()['message'] != 'ok':
        get_auth_token(old_headers['ip_address'])
        return 0

    return r.status_code


def send_node_status(old_headers, message):
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
               'access_token': token,
               'nodeid': old_headers['nodeid'],
               'ip_address': old_headers['ip_address']}
    r = requests.post(url, json=message, headers=headers)

    if r.json()['message'] != 'ok':
        get_auth_token(old_headers['ip_address'])
        return 0

    return r.status_code


@app.route('/')
def index():
    return 'Server Works!'


@app.route('/sendtohost', methods=['POST'])
def send_data():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        while leader_queue:
            executor.submit(unpack_and_send, leader_queue.pop(0))

    return "ok"


@app.route('/pop', methods=['GET'])
def popp():
    print(leader_queue.pop(0))
    return 'Boy'


@app.route('/storeleaderdata', methods=['POST'])
def store_leader_data():
    r = request.get_json()
    leader_queue.append(r)
    print(leader_queue)
    # print(leader_queue.pop(0))
    return 'ok'


@app.route('/sendtoleader', methods=['POST', 'GET'])
def leader_send():
    if not send_queue:
        send_queue.append(deepcopy(main_queue))
        print(main_queue)
        print(send_queue)
        main_queue.clear()

    headers = {
        'local_ip_address': request.url_root + "datasent"
    }
    leader_url = 'http://127.0.0.1:5001/storeleaderdata'
    r = requests.post(leader_url, json=send_queue[0], headers=headers)  # TODO retrieve leader url from election guys
    if r.status_code == 200:
        return 'Data Sent to Leader'
    else: 
        return 'Something went wrong sending the data, attempt to resend it'


@app.route('/datasent', methods=['GET'])
def data_sent_response():
    if request.headers['leader_ip_address'] == 'http://127.0.0.1:5001/':
        send_queue.clear()
        print('God leader ip')
        json_object = {'message': 'ok'}
    else:
        print('Dårlig leader ip')
        json_object = {'message': 'Not leader'}
    return json_object


@app.route('/storedata', methods=['POST'])
def information_queue():
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

