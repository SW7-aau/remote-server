import argparse
import pyshark
import requests


packets_dict_list = []


def arg_parsing():
    parser = argparse.ArgumentParser(prog='Read Packets',
                                     description='Read Network Packets')
    parser.add_argument('-i', '--interface',
                        help='Network interface '
                             'used to capture network packets.')
    parser.add_argument('-s', '--send-frequency', type=int, default=50,
                        help='How many packets should be sniffed before sent')
    parser.add_argument('-v', '--verbosity', type=int, default=0,
                        help='Increase output verbosity.')
    parser.add_argument('-a', '--ip-address',
                        help='IP Adress of the current node.')
    parser.add_argument('-p', '--port', type=int,
                        help='The port the current node is using.')

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
        #d['info']['dst_resolved'] = str(packet[0].addr_oui_resolved)
        d['info']['dst_port'] = packet[2].dstport
        d['info']['src'] = str(packet[1].src)
        #d['info']['src_resolved'] = str(packet[0].src_oui_resolved)
        d['info']['src_port'] = packet[2].srcport
        if protocol == '17':  # Protocol = UPD  ---- Else TCP
            d['info']['layer'] = packet[3].layer_name
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
        if verbosity == 1:  # Used to find undiscovered protocols
            print("Empty dict")

    return d


def send_node_status(json_object):
    url = "http://"+ ip_address + ":" + str(port) + "/storedata"
    headers = {'Content-type': 'application/json',
               'Accept': 'text/plain',
               'package_type': '2'}
    r = requests.post(url, json=json_object, headers=headers)
    if verbosity == 1:
        print(json_object)
        print(r.status_code)


def send_packets_list():
    send_node_status(packets_dict_list)
    packets_dict_list.clear()


if __name__ == '__main__':
    # Parse Args
    args = arg_parsing()

    verbosity = 1 if args.verbosity != 0 else args.verbosity
    ip_address = args.ip_address
    port = args.port

    capture = pyshark.LiveCapture(interface=args.interface)

    if verbosity == 1:
        print('Starting sniffing...')

    for n in capture.sniff_continuously():
        get_packets(packet=n, verbosity=verbosity)

        if len(packets_dict_list) == args.send_frequency:
            if verbosity == 1:
                print('Sending packets')
            send_packets_list()
