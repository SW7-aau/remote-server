import unittest
import app
from mocks import read_resources

ip_address = requests.get('https://api.ipify.org').text

class TestStringMethods(unittest.TestCase):

    def test_resource_reading_timestamp():
        

if __name__ == '__main__':
    unittest.main()