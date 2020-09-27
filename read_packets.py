import argparse
import pyshark
import json


def arg_parsing():
    parser = argparse.ArgumentParser(prog='Read Packets',
                                     description='Read Network Packets')
    parser.add_argument('interface',
                        help='Network interface '
                             'used to capture network packets.')

    args = parser.parse_args()

    return args


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
        if protocol == 17:  # Protocol = UPD  ---- Else TCP
            d['info']['layer'] = packet[3].layer_name

    return d


def other_to_dict(packet, layer_name):
    d = {}
    if layer_name == 'llc':  # Protocol = STP
        d = {'timestamp': packet.sniff_timestamp.split('.')[0],
             'protocol': packet[2].layer_name.upper(),
             'size': str(packet.length), 'info': {}}
    elif layer_name == 'arp':  # Protocol = ARP
        d = {'timestamp': packet.sniff_timestamp.split('.')[0],
             'protocol': packet[1].layer_name.upper(),
             'size': str(packet.length), 'info': {}}

    d['info']['dst_resolved'] = str(packet[0].addr_oui_resolved)
    d['info']['src_resolved'] = str(packet[0].src_oui_resolved)

    return d


def get_packets(packet):
    d = {}
    try:
        protocol = packet[1].proto
        d = ip_to_dict(packet, protocol)

        # if str(protocol) == '6':  # Protocol = TCP
        #     print('TCP')
        # elif str(protocol) == '17':  # Protocol = UDP
        #     print('UDP')
        # elif str(protocol) == '2':  # Protocol = IGMP
        #     print('IGMP')

    except AttributeError:
        layer_name = str(packet[1].layer_name)
        d = other_to_dict(packet, layer_name)

        # if str(layer_name) == 'llc':  # Protocol = STP
            # print('STP')
        # elif str(layer_name) == 'arp':  # Protocol = ARP
            # print('ARP')
        # else:
        #     print('Unknown packet')

    if not d:  # Used to find undiscovered protocols
        print("Empty dict")

    json_object = json.dumps(d)
    # print(json_object)
    return json_object


if __name__ == '__main__':
    # Parse Args
    args = arg_parsing()

    capture = pyshark.LiveCapture(interface=args.interface)
    packets = []

    for n in capture.sniff_continuously(packet_count=500):
        print("a")
        packets.append(get_packets(n))

    print(len(packets))

    for i in range(len(packets)):
        print(packets[i])
