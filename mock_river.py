import time
from random import Random
import hashlib
import base64
import concurrent.futures

class Node:
    def __init__(self):
        self.ip = "127.0.0.1"
        self.config = {}
        self.candidacy = False
        self.main_queue = []

    def set_config(self, config):
        if self.ip in config:
            self.config = config
            active = int(self.config[self.ip])
            print(active)
            if self.candidacy is False and active == 1:
                self.candidacy = True
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    executor.submit(self.timer)
            elif active != 1:
                self.candidacy = False
            print(len(self.config))




    #PLACEHOLDER FUNCTIONS
    def timer(self):
        print()
    
