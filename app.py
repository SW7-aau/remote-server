from flask import Flask
from flask import requests
app = Flask(__name__)

@app.route('/')
def index():
    return 'Server Works!'

def send_node_status(package_type, from_node, from_ip, token, message):
    if (package_type == 1):
        url = "sendtoresources"
    elif (package_type == 2):
        url = "sendtonetwrok"
    elif (package_type == 3):
        url = "sendtoprocess"
    else:
        return
           
    headers = {'Content-type': 'application/json',
               'Accept': 'text/plain',
               'auth-token': token,
               'nodeid': from_node,
               'ip-address': from_ip}
    r = requests.post(url, json=message, headers=headers)
    print(r.status_code)
    
    
@app.route('/sendtohost')
def say_hello(requests):
    package_type = requests.args.headers("package_type")
    from_node = requests.args.headers["nodeid"]
    from_ip = requests.args.headers["ip-address"]
    token = requests.args.headers["auth-token"]
    message = requests.args.get_json()
    
    send_node_status(package_type, from_node, from_ip, token, message)
    return 'Hello from Server'