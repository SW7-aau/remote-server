import time
from random import Random
import hashlib
import base64

class Node:
    def __init__(self, executor):
        self.executor = executor
        self.ip = "127.0.0.1"
        self.verbosity = 0
        self.status = "Follower"
        self.config = {}
        self.candidacy = False
        self.leader_ip = ""
        self.term = 0
        self.main_queue = []

    def set_config(self, config):
        if self.ip in config:
            self.config = config
            active = int(self.config[self.ip])
            print(active)
            if self.candidacy is False and active == 1:
                self.candidacy = True
                #self.executor.submit(self.timer) #REINSTATE
            elif active != 1:
                self.candidacy = False
            print(len(self.config))


    #NON-UNITTEST FUNCTIONS
    def become_follower(self):
        self.status = "Follower"
        self.set_timer()

    def update_term(self, term):
        self.term = term
        self.voted = False
        self.votes = 0

    #PLACEHOLDER FUNCTIONS
    def timer(self):
        return

    def set_timer(self):
        return
    
