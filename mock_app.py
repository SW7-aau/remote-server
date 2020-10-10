import mock_nodes
class requests():
    def post(self, url, json, headers):
        if(url == "http://127.0.0.1:5000/sendtohost"):
            return self.Response(say_hello(headers=headers, json=json))
        if(url == "http://217.69.10.141:5000/node-resources"):
            return self.Response(mock_nodes.node_resources(json))
        if(url == "http://217.69.10.141:5000/node-network"):
            return self.Response(mock_nodes.node_network(json))
    
    class Response():
        def __init__(self, status_code):
            self.status_code = status_code

requests = requests()

def index():
    return 'Server Works!'

def send_node_status(old_headers, message):
    if old_headers['package_type'] == '1':
        url = "http://217.69.10.141:5000/node-resources"
    elif old_headers['package_type'] == '2':
        url = "http://217.69.10.141:5000/node-network"
    elif old_headers['package_type'] == '3':
        url = "http://217.69.10.141:5000/node-proc"
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


def say_hello(headers, json):
    # package_type = request.headers["package_type"]
    # from_node = request.headers["nodeid"]
    # from_ip = request.headers["ip-address"]
    # token = request.headers["auth-token"]
    # message = request.get_json()

    return send_node_status(headers, json)
