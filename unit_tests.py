import unittest
import app
import read_resources
import read_processes
import requests

ip_address = requests.get('https://api.ipify.org').text

class TestStringMethods(unittest.TestCase):

    #should assert true if app.py is running
    def test_app_exists(self):
        url = "http://127.0.0.1:5000/"
        headers = {'Content-type': 'application/json',
                    'Accept': 'text/plain',
                    'auth-token': 'testtoken',
                    'package_type': '1',
                    'nodeid': 'testid',
                    'ip-address': str(ip_address)}
        r = requests.post(url, [], headers=headers)
        self.assertTrue(r.status_code == '200')

    #Test if we get something out of the read function
    def test_resource_read(self):
        read_resources.get_resources()
        assert(len(read_resources.resources_dict_list) == 1)

    #Test if we can successfully send resource metrics
    def test_resource_send(self):
        self.assertTrue(read_resources.send_node_status([]) == '200')

    def test_process_read(self):
        read_processes.get_processes()
        self.assertTrue(len(read_processes.processes_dict_list) == 1)

if __name__ == '__main__':
    unittest.main()