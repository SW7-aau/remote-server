from flask import Flask
from flask import request
import requests

app = Flask(__name__)
main_queue = []
send_queue = []


@app.route('/')
def index():
    return 'Server Works!'


def send_node_status(data):
    old_headers = data.headers
    message = data.get_json()

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
    #if post completes or hash exists delete sent element from send_queue
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

    request_dict = request.get_json()

    for item in request_dict:
        if item[0]['package_type'] == '1':
            resources.append(item)
        elif item[0]['package_type'] == '2':
            packages.append(item)
        elif item[0]['package_type'] == '3':
            processes.append(item)



    resources_hash = hash(resources)
    packages_hash = hash(packages)
    processes_hash = hash(processes)

    #TODO send resources hash and wait for response
    resources_status = send_node_status(resources[0][0], resources)
    #TODO send packages hash and wait for response
    packages_status = send_node_status(packages[0][0], packages)
    #TODO send processes hash and wait for response
    processes_status = send_node_status(processes[0][0], processes)

    if resources_status & packages_status & processes_status == 200:
        return resources_status
    elif
        return 

@app.route('/sendtoleader', methods=['POST'])
def leader_send():
    send_queue.append(main_queue)
    main_queue.clear()

    data = send_queue(0)

    r = requests.post(leader_url, json=data)
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


