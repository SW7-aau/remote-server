from flask import Flask
from flask import request
import requests
import concurrent.futures
import hashlib

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
        return resources_status
    else:

        return "Failed to send to host, resend request"



def send_hash(old_headers, message):
    url = "http://217.69.10.141:5000/node-hash"
    headers = {'Content-Type': 'application/json',
               'Accept': 'text/plain',
               'auth-token': old_headers['auth-token']
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


@app.route('/')
def index():
    return 'Server Works!'


@app.route('/sendtohost', methods=['POST'])
def send_data():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        return executor.submit(unpack_and_send(request)).result() 

@app.route('/sendtoleader', methods=['POST'])
def leader_send():
    send_queue.append(main_queue)
    main_queue.clear()

    data = send_queue(0)

    r = requests.post(leader_url, json=data) #TODO retrieve leader url from election guys
    if r.status_code == 200:
        send_queue.remove(data) # or use pop here instead to remove first index in queue
    #TODO else statement for handling repeat failures to send to host
    
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

if __name__ == '__main__':
    app.debug = True
    app.run(host = '127.0.0.1',port=5000)

