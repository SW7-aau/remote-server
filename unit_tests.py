import unittest
import time
import mock_read_resources


class TestStringMethods(unittest.TestCase):

    def test_resource_sending(self):
        rr = mock_read_resources.read_resources()
        rr.get_resources()
        result = rr.send_node_status(rr.resources_dict_list)
        self.assertTrue(result == 200)
    
    def test_resource_missing_message_timestamp(self):
        rr = mock_read_resources.read_resources()
        message = [{'CPU%': "50%", 'RAM': "30%"}]
        result = rr.send_node_status(message)
        self.assertFalse(result == 200)

    def test_resource_missing_message_cpu(self):
        rr = mock_read_resources.read_resources()
        timestamp = str(time.time()).split('.')[0]
        message = [{'timestamp': timestamp, 'RAM%': '35%'}]
        result = rr.send_node_status(message)
        self.assertFalse(result == 200)
        

if __name__ == '__main__':
    unittest.main()