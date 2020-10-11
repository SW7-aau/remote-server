import mock_requests
requests = mock_requests.requests()

packets_dict_list = []
def send_node_status(json_object):
    url = "http://127.0.0.1:5000/sendtohost"
    headers = {'Content-type': 'application/json',
               'Accept': 'text/plain',
               'auth-token': 'testtoken',
               'package_type': '2',
               'nodeid': 'testid',
               'ip-address': "127.0.0.1"}
    print(json_object)
    r = requests.post(url, json=json_object, headers=headers)
    return r.status_code