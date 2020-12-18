import mock_requests


class read_packets():
    packets_dict_list = []
    requests = mock_requests.requests()

    def send_node_status(self, json_object):
        url = "http://127.0.0.1:5000/storedata"
        headers = {'Content-type': 'application/json',
                'Accept': 'text/plain',
                'package_type': '2'}
        print(json_object)
        r = self.requests.post(url, json=json_object, headers=headers)
        return r.status_code

    def send_packets_list(self):
        self.send_node_status(self.packets_dict_list)
        self.packets_dict_list.clear()