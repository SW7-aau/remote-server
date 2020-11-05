candidacy = False
config = {'172.17.0.3': 'False', '172.17.0.7': 'False', '172.17.0.6': 'False', '172.17.0.5': 'False', '172.17.0.4': 'True'}
ip = '172.17.0.4'
test = config[ip]
print('ip: ' + ip)
print('config: ' + str([*config]))
print('config[ip]: ' + str(config[ip]))
print('Config but different ip: ' + str(config['172.17.0.3']))
print('candidacy: ' + str(candidacy))
print('This cant be real: ' + str(test))
if ((candidacy == False) and test):
    candidacy = test
else:
    candidacy = test
print(str(candidacy))