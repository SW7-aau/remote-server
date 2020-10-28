from mock import mock_requests


def ip_to_dict(packet, protocol):
    d = {'timestamp': packet.sniff_timestamp.split('.')[0],
         'protocol': packet.transport_layer, 'size': str(packet.length),
         'info': {}}
    if str(protocol) == '2':  # Protocol = IGMP
        d['info']['dst'] = str(packet[1].dst)
        d['info']['dst_resolved'] = str(packet[0].addr_oui_resolved)
        d['info']['src'] = str(packet[1].src)
        d['info']['src_resolved'] = str(packet[0].src_oui_resolved)
        d['info']['layer'] = packet[2].layer_name
    else:
        d['info']['dst'] = str(packet[1].dst)
        d['info']['dst_resolved'] = str(packet[0].addr_oui_resolved)
        d['info']['dst_port'] = packet[2].dstport
        d['info']['src'] = str(packet[1].src)
        d['info']['src_resolved'] = str(packet[0].src_oui_resolved)
        d['info']['src_port'] = packet[2].srcport
        if protocol == '17':  # Protocol = UPD  ---- Else TCP
            d['info']['layer'] = packet[3].layer_name
    return d


class ReadPackets:
    packets_dict_list = []
    requests = mock_requests.Requests()

    def other_to_dict(self, packet, layer_name):
        d = {}
        if layer_name == 'llc':  # Protocol = STP
            d = {'timestamp': packet.sniff_timestamp.split('.')[0],
                 'protocol': packet[2].layer_name.upper(),
                 'size': str(packet.length), 'info': {}}
        elif layer_name == 'arp' or layer_name == 'eapol':  # Protocol = ARP or EAPOL
            d = {'timestamp': packet.sniff_timestamp.split('.')[0],
                 'protocol': packet[1].layer_name.upper(),
                 'size': str(packet.length), 'info': {}}

        d['info']['dst_resolved'] = str(packet[0].addr_oui_resolved)
        d['info']['src_resolved'] = str(packet[0].src_oui_resolved)

        return d

    def get_packets(self, packet, verbosity):
        d = {}
        try:
            protocol = str(packet[1].proto)
            d = ip_to_dict(packet, protocol)
            self.packets_dict_list.append(d)

            if verbosity == 1:
                if protocol == '6':  # Protocol = TCP
                    print('TCP')
                elif protocol == '17':  # Protocol = UDP
                    print('UDP')
                elif str(protocol) == '2':  # Protocol = IGMP
                    print('IGMP')
                else:
                    print('Unknown package')

        except AttributeError:
            layer_name = str(packet[1].layer_name)
            # d = other_to_dict(packet, layer_name)

            if verbosity == 1:
                if layer_name == 'llc':  # Protocol = STP
                    print('STP')
                elif layer_name == 'arp':  # Protocol = ARP
                    print('ARP')
                elif layer_name == 'eapol':  # Protocol = EAPOL
                    print('EAPOL')
                else:
                    print('Unknown package')

        if not d and verbosity == 1:  # Used to find undiscovered protocols
            print("Empty dict")

        return d

    def send_node_status(self, json_object):
        url = "http://127.0.0.1:5000/sendtohost"
        headers = {'Content-type': 'application/json',
                   'Accept': 'text/plain',
                   'auth-token': 'testtoken',
                   'package_type': '2',
                   'nodeid': 'testid',
                   'ip-address': "127.0.0.1"}
        print(json_object)
        r = self.requests.post(url, json=json_object, headers=headers)
        return r.status_code
