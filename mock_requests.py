import mock_app
import mock_nodes

class requests():
    def post(self, url, json, headers):
        if(url == "http://127.0.0.1:5000/sendtohost"):
            return self.Response(mock_app.say_hello(headers=headers, json=json))
        if(url == "http://217.69.10.141:5000/node-resources"):
            return self.Response(mock_nodes.node_resources(json))
        if(url == "http://217.69.10.141:5000/node-network"):
            return self.Response(mock_nodes.node_network(json))
    
    class Response():
        def __init__(self, status_code):
            self.status_code = status_code  