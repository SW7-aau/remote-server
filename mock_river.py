import time
from random import Random
import hashlib
import base64

class Node:
    def __init__(self, executor, args):
        self.ip = "127.0.0.1"
        self.main_queue = []
