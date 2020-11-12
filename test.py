candidacy = False
config = {'172.17.0.3': '0', '172.17.0.7': '0', '172.17.0.6': '0', '172.17.0.5': '0', '172.17.0.4': '1'}
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