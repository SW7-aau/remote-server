from flask import Flask
from flask import request
import requests
import concurrent.futures
import hashlib
import socket

app = Flask(__name__)


main_queue = []
send_queue = []


def unpack_and_send(request):
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


    if send_hash(resources[0][0], hashlib.sha256(resources).hexdigest()) == 200:
        resources_status = send_node_status(resources[0][0], resources)

    if send_hash(packages[0][0], hashlib.sha256(packages).hexdigest()) == 200:
        packages_status = send_node_status(packages[0][0], packages)

    if send_hash(processes[0][0], hashlib.sha256(processes).hexdigest()) == 200:
        processes_status = send_node_status(processes[0][0], processes)

    if resources_status & packages_status & processes_status == 200:
        url = request.headers['localip']
        print("data sent response sent to " + url)
        headers = {'Content-Type': 'application/json',
                    'Accept': 'text/plain',
                    'auth-token': resources[0][0]['auth-token']
                  }
        r = requests.post(url, json=message, headers=headers)



def send_hash(old_headers, message):
    url = "http://217.69.10.141:5000/node-hash" #node hash url
    headers = {'Content-Type': 'application/json',
               'Accept': 'text/plain',
               'auth-token': old_headers['auth-token']
               }
    r = requests.post(url, json=message, headers=headers)
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
    headers = {'Content-Type': 'application/json',
               'Accept': 'text/plain',
               'auth-token': old_headers['auth-token'],
               'nodeid': old_headers['nodeid'],
               'ip-address': old_headers['ip-address']}
    r = requests.post(url, json=message, headers=headers)
    return r.status_code


@app.route('/')
def index():
    return 'Server Works!'


@app.route('/sendtohost', methods=['POST'])
def send_data():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(unpack_and_send, request)

    return "ok"

@app.route('/sendtoleader', methods=['POST'])
def leader_send():
    if not send_queue:
        send_queue.append(main_queue)
        main_queue.clear()

    headers = {
        'localip': request.url_root + "datasent"
    }

    r = requests.post(leader_url, json=send_queue, headers=headers) #TODO retrieve leader url from election guys
    if r.status_code == 200:
        return 'Data Sent to Leader'
    else: 
        return 'Something went wrong sending the data, attempt to resend it'

@app.route('/datasent', methods=['POST, GET'])
def data_sent_response():
    send_queue.clear()
    return 'ok'

@app.route('/storedata', methods=['POST'])
def information_queue():
    temp_request = [{
        'package_type': request.headers['package_type'],
        'auth-token': request.headers['auth-token'],
        'nodeid': request.headers['nodeid'],
        'ip-address': request.headers['ip-address'],

    }, request.form]

    main_queue.append(temp_request)
    return 'Data Appended'

if __name__ == '__main__':
    app.debug = True
    app.run(host = '127.0.0.1',port=5000)

