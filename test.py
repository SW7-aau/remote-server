import requests

config = requests.get('http://217.69.10.141:5000/get-config?cluster_id=' + '3000').json()
print(config)
print([*config])