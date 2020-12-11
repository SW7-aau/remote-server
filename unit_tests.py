import unittest
import time
import mock_read_resources
#import mock_read_process
import mock_read_packets
import concurrent.futures
import mock_river
import mock_app

class TestReaderMethods(unittest.TestCase):

    def test_resource_sending(self):
        rr = mock_read_resources.read_resources()
        rr.get_resources()
        result = rr.send_node_status(rr.resources_dict_list)
        self.assertTrue(result == 200)

    def test_resource_missing_message_timestamp(self):
        rr = mock_read_resources.read_resources()
        message = [{'CPU%': "50%", 'RAM%': "30%"}]
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
        self.assertFalse(result == 200)

    def test_packets_sending(self):
        rp = mock_read_packets.read_packets()
        packets = [
            {
                "id":"172.17.0.6",
                "timestamp":"2020-11-23 12:41:52",
                "protocol":"TCP",
                "size":"66",
                "dst":"172.17.0.7",
                "dst_resolved":"NULL",
                "dst_port":"50572",
                "src_resolved":"NULL",
                "src":"172.17.0.6",
                "src_port":"5000",
                "layer":"NULL"
            }
        ]
        result = rp.send_node_status(packets)
        self.assertTrue(result == 200)

    def test_packets_missing_info(self):
        rp = mock_read_packets.read_packets()
        packets = [
            {
                "id":"172.17.0.6",
                "timestamp":"2020-11-23 12:41:52",
                "protocol":"TCP",
                "size":"66",
                "dst":"172.17.0.7",
                "dst_resolved":"NULL",
                "dst_port":"50572",
                "src_resolved":"NULL",
                "src_port":"5000",
                "layer":"NULL"
            }
        ]
        result = rp.send_node_status(packets)
        self.assertFalse(result == 200)



class TestElectionMethods(unittest.TestCase):
    def test_own_ip_in_config(self):
        config = {'127.0.0.1': '1'}
        self.node.set_config(config)
        self.assertTrue(len(self.node.config) == 1)

    def test_own_ip_not_in_config(self):
        config = {'172.17.0.6': '1'}
        self.node.set_config(config)
        self.assertFalse(len(self.node.config) == 1)

    def test_successful_candidacy(self):
        config = {'127.0.0.1': '1'}
        self.node.set_config(config)
        self.assertTrue(self.node.candidacy)

    def test_unsuccessful_candidacy(self):
        config = {'127.0.0.1': '0'}
        self.node.set_config(config)
        self.assertFalse(self.node.candidacy)

    def setUp(self):
        #Maybe move this outside the class so it doesn't close between tests?
        with concurrent.futures.ThreadPoolExecutor() as executor:
            self.node = mock_river.Node(executor)



class TestAppMethods(unittest.TestCase):

    def test_sender_greater_term(self):
        headers = {
            'term': '1',
            'status': 'Candidate'
        }
        self.assertTrue(self.app.check_headers(headers))

    def test_sender_is_leader(self):
        self.assertTrue(False)
    
    def test_sender_lower_term(self):
        self.assertFalse(True)

    def setUp(self):
        self.app = mock_app.App()

    

if __name__ == '__main__':
    unittest.main()