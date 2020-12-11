import time
from random import Random
import hashlib
import base64

class Node:
    def __init__(self, executor):
        self.executor = executor
        self.ip = "127.0.0.1"
        self.config = {}
        self.candidacy = False
        self.main_queue = []

    def set_config(self, config):
        if not self.ip in config:
            return False
        self.config = config
        active = int(self.config[self.ip])
        print(active)
        if self.candidacy is False and active == 1:
            self.candidacy = True
            self.executor.submit(self.timer)
        elif active != 1:
            self.candidacy = False
        print(len(self.config))




    #PLACEHOLDER FUNCTIONS
    def timer(self):
        print()
    
