import time
import psutil
import mock_requests

class read_resources():
    resources_dict_list = []
    requests = mock_requests.requests()
    def get_resources(self):
        timestamp = str(time.time()).split('.')[0]
        status_struct = {'timestamp': timestamp,
                        'CPU%': str(psutil.cpu_percent()),
                        'RAM%': str(psutil.virtual_memory().percent)}
        # Bandwith not included atm.
        print(status_struct)
        self.resources_dict_list.append(status_struct)

    def send_node_status(self, json_object):
        url = "http://127.0.0.1:5000/storedata"
        headers = {'Content-type': 'application/json',
                'Accept': 'text/plain',
                'package_type': '1'}
        r = self.requests.post(url, json=json_object, headers=headers)
        return r.status_code