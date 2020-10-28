import time
import psutil
from mock import mock_requests


class ReadProcesses:
    processes_dict_list = []
    requests = mock_requests.Requests()

    def get_processes(self):
        timestamp = str(time.time()).split('.')[0]
        for proc in psutil.process_iter():
            try:
                process = proc.as_dict()
                process['timestamp'] = timestamp
                self.processes_dict_list.append(process)
            except (psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess):
                pass

    def send_node_status(self, json_object):
        url = "http://127.0.0.1:5000/sendtohost"
        headers = {'Content-type': 'application/json',
                   'Accept': 'text/plain',
                   'auth-token': 'testtoken',
                   'package_type': '3',
                   'nodeid': 'testid',
                   'ip-address': "127.0.0.1"}
        r = self.requests.post(url, json=json_object, headers=headers)
        return r.status_code
