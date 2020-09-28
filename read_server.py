import schedule
import time
import requests
import subprocess
import pyshark
import threading

import read_packets
import read_resources
import read_processes


SECONDS_BEFORE_COMMIT = 5


def packets():
    capture = pyshark.LiveCapture(interface='wlp3s0')  # Usually enp3s0 or wlp3s0
    packet_list = []

    for n in capture.sniff_continuously(packet_count=500):
        packet_list.append(read_packets.get_packets(n))

    print(len(packet_list))


def resources_and_processes():
    schedule.every(1).second.do(read_resources.get_resources)
    schedule.every(5).seconds.do(read_processes.get_processes)
    # schedule.every(SECONDS_BEFORE_COMMIT).seconds.do(read_resources.send_resources_list)
    # schedule.every(SECONDS_BEFORE_COMMIT).seconds.do(read_processes.send_processes_list)

    while True:
        schedule.run_pending()


if __name__ == '__main__':
    print("Main")

    thread1 = threading.Thread(target=packets)
    thread2 = threading.Thread(target=resources_and_processes)
    thread1.start()
    thread2.start()

    # while True:
    #     schedule.run_pending()
    #     # time.sleep(1)
