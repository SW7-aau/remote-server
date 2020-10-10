from datetime import datetime

#Check if legal shit is passed using try-catch
def node_resources(message):
    try:
        for i in message:
            timestamp = datetime.fromtimestamp(int(i['timestamp'])).strftime("%Y-%m-%d %I:%M:%S")
            print("timestamp = " + str(timestamp))
            cpu_percent = i['CPU%']
            ram_percent = i['RAM%']
        return 200
    except KeyError:
        return 500

def node_network(message):
    try:
        for i in message:
            protocol = i['protocol']
            timestamp = datetime.fromtimestamp(int(i['timestamp'])).strftime("%Y-%m-%d %I:%M:%S")
            size = i['size']
            info = i['info']
        return 200
    except KeyError:
        return 500