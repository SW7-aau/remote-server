import argparse
import pyshark
import json
import requests


ip_address = requests.get('https://api.ipify.org').text
packets_dict_list = []


def arg_parsing():
    parser = argparse.ArgumentParser(prog='Read Packets',
                                     description='Read Network Packets')
    parser.add_argument('-i', '--interface',
                        help='Network interface '
                             'used to capture network packets.')
    parser.add_argument('-s', '--send-frequency', type=int, default=50,
                        help='How many packets should be sniffed before sent')
    parser.add_argument('-v', '--verbosity', type=int, default=1,
                        help='Increase output verbosity.')

    return parser.parse_args()


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


def other_to_dict(packet, layer_name):
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


def get_packets(packet, verbosity):
    d = {}
    try:
        protocol = str(packet[1].proto)
        d = ip_to_dict(packet, protocol)
        packets_dict_list.append(d)

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


def send_node_status(json_object):
    url = "http://127.0.0.1:5000/sendtohost"
    headers = {'Content-type': 'application/json',
               'Accept': 'text/plain',
               'auth-token': 'testtoken',
               'package_type': '2',
               'nodeid': 'testid',
               'ip-address': str(ip_address)}
    print(json_object)
    r = requests.post(url, json=json_object, headers=headers)
    print(r.status_code)


def send_packets_list():
    send_node_status(packets_dict_list)
    packets_dict_list.clear()


if __name__ == '__main__':
    # Parse Args
    args = arg_parsing()

    verbosity = 1 if args.verbosity != 0 else args.verbosity

    capture = pyshark.LiveCapture(interface=args.interface)

    if verbosity == 1:
        print('Starting sniffing...')

    for n in capture.sniff_continuously():
        # packets_dict_list.append(get_packets(packet=n, verbosity=verbosity))
        get_packets(packet=n, verbosity=verbosity)

        if len(packets_dict_list) == args.send_frequency:
            if verbosity == 1:
                print('Sending packets')
            send_packets_list()
