import requests

candidacy = False
config = requests.get('http://95.179.226.113:5000/get-config?cluster_id=' + '3000').json()
ip = '172.17.0.3'
test = int(config[ip])
print('ip: ' + ip)
print('config: ' + str([*config]))
print('config[ip]: ' + str(config[ip]))
print('Config but different ip: ' + str(config['172.17.0.3']))
print('candidacy: ' + str(candidacy))
print('This cant be real: ' + str(test))
if candidacy == False and test == 1:
    candidacy = test
    print('FUCK')
else:
    candidacy = test
print(str(candidacy))