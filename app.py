from flask import Flask
from flask import request
import requests

app = Flask(__name__)
main_queue = []
send_queue = []


@app.route('/')
def index():
    return 'Server Works!'


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
    print(r.status_code)


@app.route('/sendtohost', methods=['POST'])
def say_hello():
    data_dict = []
    # package_type = request.headers["package_type"]
    # from_node = request.headers["nodeid"]
    # from_ip = request.headers["ip-address"]
    # token = request.headers["auth-token"]
    # message = request.get_json()
    send_queue.append(main_queue)
    main_queue.clear()

    data = send_queue.pop(0)

    data_dict.append(data)
    data_dict.append(hash(data))

    send_node_status(request.headers, data_dict)
    data_dict.clear()
    return 'Hello from Server'


@app.route('/storedata', methods=['POST'])
def information_queue():
    main_queue.append(request.get_json())

