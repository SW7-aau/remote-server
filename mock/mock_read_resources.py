import time
import psutil
from mock import mock_requests


class ReadResources:
    resources_dict_list = []
    requests = mock_requests.Requests()

    def get_resources(self):
        timestamp = str(time.time()).split('.')[0]
        status_struct = {'timestamp': timestamp,
                         'CPU%': str(psutil.cpu_percent()),
                         'RAM%': str(psutil.virtual_memory().percent)}
        # Bandwidth not included atm.
        print(status_struct)
        self.resources_dict_list.append(status_struct)

    def send_node_status(self, json_object):
        url = "http://127.0.0.1:5000/sendtohost"
        headers = {'Content-type': 'application/json',
                   'Accept': 'text/plain',
                   'auth-token': 'testtoken',
                   'package_type': '1',
                   'nodeid': 'testid',
                   'ip-address': "127.0.0.1"}
        r = self.requests.post(url, json=json_object, headers=headers)
        return r.status_code
