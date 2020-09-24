import schedule
import time
import requests
import subprocess

import server_reader


SECONDS_BEFORE_COMMIT = 5


if __name__ == '__main__':
    print("Main")
    # read_packets = "python3 read_packets.py wlp3s0"
    # process = subprocess.Popen(read_packets.split(), stdout=subprocess.PIPE)
    # output, error = process.communicate()
    schedule.every(1).second.do(server_reader.read_status)
    # schedule.every(SECONDS_BEFORE_COMMIT).seconds.do(server_reader.send_status_list)

    while True:
        schedule.run_pending()
        print(server_reader.status_struct_list)
        # time.sleep(1)
