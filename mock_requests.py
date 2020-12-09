import mock_app

class requests():
    def post(self, url, json={}, headers={}):
        result = 0
        if(url == "http://127.0.0.1:5000/storedata"):
            result = mock_app.information_queue(self.request(headers=headers, json=json))
            if result == 'Data Appended':
                return self.Response(200)
        return self.Response(500)
    class Response():
        def __init__(self, status_code):
            self.status_code = status_code
    class request():
        def __init__(self, json={}, headers={}):
            self.json = json
            self.headers = headers

        def get_json(self):
            return self.json