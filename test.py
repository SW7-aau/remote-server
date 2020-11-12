import requests

config = requests.get('http://95.179.226.113:5000/get-config?cluster_id=' + '3000').json()
print(config)