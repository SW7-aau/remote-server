from flask import Flask
from flask import request

app = Flask(__name__)


@app.route('/')
def index():
    return 'Server Works!'


def send_node_status(header, message):
    if header['package_type'] == 1:
        url = "resources_endpoint"
    elif header['package_type'] == 2:
        url = "network_endpoint"
    elif header['package_type'] == 3:
        url = "process_endpoint"
    else:
        return
           
    # headers = {'Content-type': 'application/json',
    #            'Accept': 'text/plain',
    #            'auth-token': header['token'],
    #            'nodeid': header['from_node'],
    #            'ip-address': header['from_ip']}
    r = request.post(url, json=message, headers=header)
    print(r.status_code)


@app.route('/sendtohost', methods=['POST'])
def say_hello():
    # package_type = request.headers["package_type"]
    # from_node = request.headers["nodeid"]
    # from_ip = request.headers["ip-address"]
    # token = request.headers["auth-token"]
    # message = request.get_json()
    
    send_node_status(request.headers, request.get_json())
    return 'Hello from Server'