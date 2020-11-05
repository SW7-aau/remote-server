# Election currently not configuration file managing / join consensus implemntation.

# ---- Leader behavior ------
# Start of new term (that last arbitary duration) (should be numbered current_term_number, increasing by an integer each term, to give new leader presumed highest term number)
# Initiate Election
# Request leadership, multithread requestVote RPC to all nodes.
# Response from majority of nodes in log from db (length divide by 2 and round up), accepted as leader and send confirmation out to other nodes to say its new leader
# and prevent further elections
# During split vote, reattempt election

# Leaders send periodic heartbeats to followers with appendEntries RPC.
# During any type of requests to followers, if the leaders current term is out of date, revert to follower immediately.

# ----- Follower behavior ------
# Response to leader, constant appendEntries RPC:
# - Update current term if it is different
# - If a follower recives a request from old term number, reject it.
# election_timeout: Timeout no leader request, Initiate Election - server transitions to candidate state

# Candidate, requestVote RPC:
# A server will vote for at most one candidate in a given term, in a first comes first serves basis
# If candidate received appendEntries request from a term that is equal to or larger than the term the candidate tries to propose, shift back to follower.


# Proof of concept with five nodes


# Environment setup for flask APIs
# set FLASK_ENV=development
# set FLASK_APP=logless_raft.py
# flask run -p (desired port number, ex. 5001)


import requests
import time
from random import Random
import sys
import hashlib
import base64


class Node:
    def __init__(self, executor, args):
        """
        Node in raft
        :param executor: thread to run on
        :param args: args used to start program (ip, cluster, port)
        """
        self.ip = str(args.ip_address)
        self.cluster_id = str(args.cluster_id)
        self.port = str(args.port)
        self.verbosity = args.verbosity
        self.node = "test-node"
        self.status = "Follower"
        self.set_timer()
        self.executor = executor
        self.config = []
        self.candidacy = False
        self.set_config()
        self.leader_ip = ""
        self.gcp_ip = ""
        self.majority = int((len(self.config))/2)+1
        # TODO: Reconsider vote-counting to be based on terms.
        self.term = 0
        self.votes = 0
        self.voted = False
        self.rand = Random()
        self.time = None
        self.timeout = 0
        self.time_flag = False
        self.main_queue = []
        self.send_queue = []
        self.leader_queue = []
        self.client_secret = '506c8044e28cbc71e989a1d9885d0e'
        self.client_id = '6e9fe75e4263ee84a4cadc1674182f'
        self.token = None

    # Setup functions
    def set_config(self):
        """
        Get config from GCP
        Assume dicts come in the form of {'ip': 'bool'}
        """
        #self.config = requests.get('http://217.69.10.141:5000/get-config?cluster_id=' + self.cluster_id).json()
        self.config = {'172.17.0.3': 'False', '172.17.0.7': 'False', '172.17.0.6': 'False', '172.17.0.5': 'False', '172.17.0.4': 'True'}
        print(bool(self.config[self.ip]))
        print(type(bool(self.config[self.ip])))
        if self.candidacy == False and bool(self.config[self.ip]):
            self.candidacy = bool(self.config[self.ip])
            self.executor.submit(self.timer)
        else:
            self.candidacy = bool(self.config[self.ip])
        print(len(self.config))

    def become_follower(self):
        """
        Sets timer and status as follower
        """
        self.set_timer()
        self.status = "Follower"
        # print(str(self.ip) + " became follower.")

    def become_candidate(self):
        """
        Resets timer to reattempt election, if not elected leader
        Sets status as candidate, updates term, and votes for self
        Starts election
        """
        if self.verbosity == 1:
            print(self.ip, " became candidate.")
        self.set_timer() # Reset time so candidate reattempts election if it didnt get elected or no one else became leader in meanwhile
        self.status = "Candidate"
        self.update_term(self.term + 1)
        self.voted = True
        self.votes = 1
        self.start_election()
        
    def become_leader(self):
        """
        Resets timer and sets status to leader
        Calls heartbeat to all followers
        """
        if self.verbosity == 1:
            print(self.ip, " became leader with ", str(self.votes), " votes.")
        self.set_timer()
        self.status = "Leader"
        self.get_auth_token(self.ip)
        self.heartbeat()

    # Misc functions
    def create_endpoint_url(self, ip, port):
        return 'http://' + ip + ':' + port

    def heartbeat(self):
        """
        Sends heartbeat to all followers in config
        :return:
        """
        # TODO: Also receive queue to send to gcp
        # Iterates through a list of keys in self.config
        for server in [*self.config]:
            if self.verbosity == 1:
                print("Sending heartbeat to ", server)
            self.executor.submit(self.get_data, server)
        # Send result to GCP
        host_url = f'http://{self.ip}:{self.port}/sendtohost'
        requests.post(url=host_url)

    def get_data(self, server):
        """
        Gets data from followers
        :param server: Follower node's address
        """
        # TODO: Send a received message to gcp
        follower_url = server + '/sendtoleader'
        headers = {'Content_type': 'application/json',
                   'Accept': 'text/plain',
                   'nodeid': self.node,
                   'ip_address': self.ip,
                   'term': str(self.term),
                   'status': self.status}
        r = requests.get(url=follower_url, headers=headers, timeout=2)

    def request_vote(self, url):
        """
        Requests vote from other node
        If majority is achieved, become leader
        :param url: url to other node
        """
        response = int(requests.get(url + '/requestvote',
                                    headers=self.create_headers(),
                                    timeout=0.15).text)
        self.votes += response
        if self.verbosity == 1:
            print('votes: ', str(self.votes))
        if self.votes >= self.majority and self.status == "Candidate":
            self.become_leader()

    def start_election(self):
        """
        Starts a thread for each element in config file
        Lacks code for stopping threads after an election have taken place.
        if they can't reach a node though.
        :return:
        """
        if self.verbosity == 1:
            print('term: ', str(self.term))
        for server in [*self.config]:
            self.executor.submit(self.request_vote, server)

    # Update functions
    def create_headers(self):
        # return {"ip": self.ip, "term": self.term}
        return {'Content_type': 'application/json',
                'Accept': 'text/plain',
                'access_token': 'testtoken',
                'package_type': '1',
                'nodeid': 'testid',
                'ip_address': self.ip,
                'term': str(self.term),
                'status': self.status}

    def update_term(self, term):
        """
        Updates own term to leaders term
        :param term: Leaders term
        """
        self.term = term
        self.voted = False
        self.votes = 0
        
    # Leader functions
    def get_auth_token(self, ip_address):
        """
        Used to get access token from GCP
        :param ip_address: An IP Address used for generating access token
        :return: Sets global token to returned access token
        """
        client_creds = f'{self.client_id}:{self.client_secret}'
        client_creds_b64 = base64.b64encode(client_creds.encode()).decode()

        refresh_token = b'sw7 server monitoring'
        refresh_token = hashlib.sha512(refresh_token).hexdigest()
        refresh_token = f'Bearer {refresh_token}'

        grant_type = 'refresh_token'

        token_data = {
            'grant_type': grant_type,
            'refresh_token': refresh_token
        }
        token_headers = {
            'Authorization': client_creds_b64,
            'nodeid': 'test_id',
            'ip_address': ip_address,
            'package_type': '1'
        }
        url = "http://217.69.10.141:5000/token"

        r = requests.post(url=url, data=token_data, headers=token_headers)

        tmp = r.json()['access_token']
        self.token = f'Bearer {tmp}'

    # Timer functions
    def timer(self):
        """
        If timeout is reached, call timer_handler
        """
        while self.candidacy:
            self.time = time.time()
            print('we setting time bois')
            if self.time >= self.timeout:
                self.set_timer()
                #self.time_flag = True
                self.executor.submit(self.timer_handler)

    def set_timer(self):
        """
        Sets timer
        If status is follower or candidate, set random timer between 0.15 and 0.3 secs
        If status is leader, set timer to 0.05 secs
        """
        self.time = time.time()
        if self.status == "Follower" or self.status == "Candidate":
            self.timeout = self.time + self.rand.uniform(50, 60)
            #self.time_flag = False
        elif self.status == "Leader":
            self.timeout = self.time + 40
            #self.time_flag = False
        
    def timer_handler(self):
        """
        If status is follower or candidate, become candidate, and reset timer
        If status is leader, call heartbeat
        """
        if self.status == "Follower" or self.status == "Candidate":
            self.become_candidate()
        elif self.status == "Leader":
            self.heartbeat()
