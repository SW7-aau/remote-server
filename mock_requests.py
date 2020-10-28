import mock_app

class requests():
    def post(self, url, json, headers):
        if(url == "http://127.0.0.1:5000/sendtohost"):
            return self.Response(mock_app.say_hello(headers=headers, json=json))
    class Response():
        def __init__(self, status_code):
            self.status_code = status_code