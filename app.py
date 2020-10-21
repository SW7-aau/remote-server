from flask import Flask
from flask import request
import requests

app = Flask(__name__)
main_queue = []
send_queue = []


@app.route('/')
def index():
    return 'Server Works!'

def send_hash(message):
    url = "Hash endpoint url here"
    headers = {'Content-Type': 'application/json',
               'Accept': 'text/plain',
               'auth-token': old_headers['auth-token'], #TODO do something here to get a proper auth token
               }
    r = requests.post(url, json=message, headers=headers)
    return r.status_code


def send_node_status(old_headers, message):

    if old_headers['package_type'] == '1':
        url = "https://europe-west3-wide-office-262621.cloudfunctions.net/node-status"
    elif old_headers['package_type'] == '2':
        url = "https://europe-west3-wide-office-262621.cloudfunctions.net/node-network"
    elif old_headers['package_type'] == '3':
        url = "https://europe-west3-wide-office-262621.cloudfunctions.net/node-processess"
    else:
        return

    print('Sent to: ', old_headers['package_type'])
    headers = {'Content-Type': 'application/json',
               'Accept': 'text/plain',
               'auth-token': old_headers['auth-token'],
               'nodeid': old_headers['nodeid'],
               'ip-address': old_headers['ip-address']}
    r = requests.post(url, json=message, headers=headers)
    return r.status_code


@app.route('/sendtohost', methods=['POST'])
def unpack_and_send():
    # package_type = request.headers["package_type"]
    # from_node = request.headers["nodeid"]
    # from_ip = request.headers["ip-address"]
    # token = request.headers["auth-token"]
    # message = request.get_json()
    resources = []
    packages = []
    processes = []

    request_list = request.get_json()

    for item in request_list:
        if item[0]['package_type'] == '1':
            resources.append(item)
        elif item[0]['package_type'] == '2':
            packages.append(item)
        elif item[0]['package_type'] == '3':
            processes.append(item)



    resources_hash = hash(resources)
    packages_hash = hash(packages)
    processes_hash = hash(processes)

    if send_hash(resources_hash) == 200:
        resources_status = send_node_status(resources[0][0], resources)

    if send_hash(packages_hash) == 200:
        packages_status = send_node_status(packages[0][0], packages)

    if send_hash(processes_hash) == 200:
        processes_status = send_node_status(processes[0][0], processes)

    if resources_status & packages_status & processes_status == 200:
        return resources_status
    elif
        return "500" #TODO error code here

@app.route('/sendtoleader', methods=['POST'])
def leader_send():
    send_queue.append(main_queue)
    main_queue.clear()

    data = send_queue(0)

    r = requests.post(leader_url, json=data) #TODO find a way to get leader url for endpoint
    if r.status_code == 200:
        send_queue.remove(data) # or use pop here instead to remove first index in queue

    
    return 'Data Sent to Leader'

@app.route('/storedata', methods=['POST'])
def information_queue():

    temp_request = [{
        'package_type': request.headers['package_type'],
        'auth-token': request.headers['auth-token'],
        'nodeid': request.headers['nodeid'],
        'ip-address': request.headers['ip-address']
    }, request.form]

    main_queue.append(temp_request)
    return 'Data Appended'


