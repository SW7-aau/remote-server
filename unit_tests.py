import unittest
import time
import mock_read_resources
#import mock_read_process
#import mock_read_packets


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

    def test_resource_missing_message_ram(self):
        rr = mock_read_resources.read_resources()
        timestamp = str(time.time()).split('.')[0]
        message = [{'timestamp': timestamp, 'CPU%': '35%'}]
        result = rr.send_node_status(message)
        self.assertFalse(result == 200)

    def test_resource_missing_message(self):
        rr = mock_read_resources.read_resources()
        result = rr.send_node_status([{}])
        self.assertFalse(result == 200)

    #Considering that an empty list technically doesn't break anything
    #Maybe assertTrue is fine?
    def test_resource_empty_message(self):
        rr = mock_read_resources.read_resources()
        result = rr.send_node_status([])
        self.assertTrue(result == 200)

if __name__ == '__main__':
    unittest.main()

    #As of writing, process related tests will fail
    #As there is, to my knowledge, no handling of them in the nodes/api.
    # def test_process_sending(self):
    #    rp = mock_read_process.read_processes()
    #   rp.get_processes()
    #  result = rp.send_node_status(rp.processes_dict_list)
    # self.assertTrue(result == 200)

    #def test_process_missing_message(self):
    #    rp = mock_read_process.read_processes()
    #    result = rp.send_node_status({})
    #    self.assertFalse(result == 200)