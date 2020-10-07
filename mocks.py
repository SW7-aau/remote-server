import time
import psutil

class request():
    def post(self, url, json, headers):
        
        
    def get(self, url):
        
    class Response():
        status_code = 0
        def __init__(self, status_code):
            self.status_code = status_code
        
class read_resources():
    resources_dict_list = []
    def get_resources(self):
        timestamp = str(time.time()).split('.')[0]
        status_struct = {'timestamp': timestamp,
            'CPU%': str(psutil.cpu_percent()),
            'RAM%': str(psutil.virtual_memory().percent)}
        # Bandwith not included atm.
        print(status_struct)
        return status_struct
        
    def send_node_status(self, json_object):
        url = "http://127.0.0.1:5000/sendtohost"
        headers = { 'Content-type': 'application/json',
                    'Accept': 'text/plain',
                    'auth-token': 'testtoken',
                    'package_type': '1',
                    'nodeid': 'testid',
                    'ip-address': str(ip_address)}
        r = self.requests.post(url, json=json_object, headers=headers)
        print(r.status_code)
        
    def send_resources_list(self):
        
class read_processes():
    processes_dict_list = []
    def get_processes(self):
        
    def send_node_status(self):
        
    def send_process_list(self):