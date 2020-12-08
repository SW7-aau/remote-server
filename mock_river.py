import time
from random import Random
import hashlib
import base64

class Node:
    def __init__(self, executor, args):
        self.main_queue = []
