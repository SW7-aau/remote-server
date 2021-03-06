import requests
import time
from random import Random
import hashlib
import base64

class Node:
    def __init__(self, executor, args):
        """
        Node in river
        :param executor: thread to run on
        :param args: args used to start program (ip, cluster, port)
        """
        self.rand = Random()
        self.executor = executor
        self.ip = str(args.ip_address)
        self.cluster_id = str(args.cluster_id)
        self.port = str(args.port)
        self.verbosity = args.verbosity
        self.node = "test-node"
        self.status = "Follower"
        self.time = None
        self.timeout = 0
        self.set_timer()
        self.config = {}
        self.candidacy = False
        self.fetch_config()
        self.majority = int((len(self.config))/2)+1
        self.leader_ip = ""
        self.gcp_ip = ""
        self.term = 0
        self.votes = 0
        self.voted = False
        self.main_queue = []
        self.send_queue = []
        self.leader_queue = []
        self.client_secret = '506c8044e28cbc71e989a1d9885d0e'
        self.client_id = '6e9fe75e4263ee84a4cadc1674182f'
        self.token = None
        self.config_counter = 0
        self.config_counter_amount = 8

    # Setup functions
    def fetch_config(self):
        """
        Get config from GCP
        Assume dicts come in the form of {'ip': '0/1'}
        """
        url = f'http://95.179.226.113:5000/get-config?cluster_id=' \
              f'{self.cluster_id}'
        cfg = requests.get(url=url).json()
        self.set_config(cfg)

    def set_config(self, config):
        self.config = config
        #if self.status == 'Leader':
        #    self.share_config()
        active = int(self.config[self.ip])
        print(active)
        if self.candidacy is False and active == 1:
            self.candidacy = True
            self.executor.submit(self.timer)
        elif active != 1:
            self.candidacy = False
        print(len(self.config))

    def become_follower(self):
        """
        Sets timer and status as follower
        """
        self.status = "Follower"
        self.set_timer()
        # print(str(self.ip) + " became follower.")

    def become_candidate(self):
        """
        Resets timer to reattempt election, if not elected leader
        Sets status as candidate, updates term, and votes for self
        Starts election
        """
        if self.verbosity == 1:
            print(self.ip, " became candidate.")
        self.status = "Candidate"
        self.set_timer()  # Reset time so candidate reattempts election if it didnt get elected or no one else became leader in meanwhile
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
        self.status = "Leader"
        self.set_timer()
        self.get_auth_token()
        self.heartbeat()

    # Misc functions
    def create_endpoint_url(self, ip, port):
        return 'http://' + ip + ':' + port

    def heartbeat(self):
        """
        Sends heartbeat to all followers in config
        :return:
        """
        # Iterates through a list of keys in self.config
        for server in [*self.config]:
            if self.verbosity == 1:
                print("Sending heartbeat to ", server)
            server = self.create_endpoint_url(server, self.port)
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
        requests.get(url=follower_url, headers=headers, timeout=2)

    def share_config(self):
        for server in [*self.config]:
            server = self.create_endpoint_url(server, self.port)
            self.executor.submit(self.send_config, server)

    def send_config(self, server):
        follower_url = server + '/shareconfig'
        headers = {'Content_type': 'application/json',
                   'Accept': 'text/plain',
                   'nodeid': self.node,
                   'ip_address': self.ip,
                   'term': str(self.term),
                   'status': self.status}
        requests.post(url=follower_url, json=self.config, headers=headers)

    def request_vote(self, url):
        """
        Requests vote from other node
        If majority is achieved, become leader
        :param url: url to other node
        """
        response = int(requests.get(url + '/requestvote',
                                    headers=self.create_headers(),
                                    timeout=0.5).text)
        self.votes += response
        if self.verbosity == 1:
            print('votes: ', str(self.votes))
        if self.votes >= self.majority and self.status == "Candidate":
            self.become_leader()

    def start_election(self):
        """
        Starts a thread for each element in config file
        :return:
        """
        if self.verbosity == 1:
            print('term: ', str(self.term))
        for server in [*self.config]:
            server = self.create_endpoint_url(server, '5000')
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
    def get_auth_token(self):
        """
        Used to get access token from GCP
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
            'nodeid': self.node,
            'ip_address': self.ip,
            'cluster_id': self.cluster_id
        }
        url = "http://95.179.226.113:5000/token"

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
            if self.time >= self.timeout:
                print('We just timed out')
                self.set_timer()
                self.executor.submit(self.timer_handler)

    def set_timer(self):
        """
        Sets timer
        If status is follower or candidate, set random timer between 50 and 60 seconds
        If status is leader, set timer to 40 seconds
        """
        self.time = time.time()
        if self.status == "Follower":
            self.timeout = self.time + self.rand.uniform(50, 60)
        elif self.status == "Candidate":
            self.timeout = self.time + self.rand.uniform(2, 3)
        elif self.status == "Leader":
            self.timeout = self.time + 40
        
    def timer_handler(self):
        """
        If status is follower or candidate, become candidate, and reset timer
        If status is leader, call heartbeat
        """
        if self.status == "Follower" or self.status == "Candidate":
            self.become_candidate()
            self.config_counter = 0
        elif self.status == "Leader":
            self.heartbeat()
            if self.config_counter < self.config_counter_amount:
                self.config_counter += 1
            else:
                self.fetch_config()
                self.config_counter = 0
            
