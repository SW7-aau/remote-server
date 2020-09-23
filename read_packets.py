import pyshark
import json


def tcp_to_dict(packet):
    d = {'timestamp': str(packet.sniff_time), 'protocol': packet.transport_layer, 'size': str(packet.length),
         'info': {}}
    d['info']['dst'] = str(packet[1].dst)
    d['info']['dst_resolved'] = str(packet[0].addr_oui_resolved)
    d['info']['dst_port'] = packet[2].dstport
    d['info']['src'] = str(packet[1].src)
    d['info']['src_resolved'] = str(packet[0].src_oui_resolved)
    d['info']['src_port'] = packet[2].srcport

    return d


def udp_to_dict(packet):
    d = {'timestamp': str(packet.sniff_time), 'protocol': packet.transport_layer, 'size': str(packet.length),
         'info': {}}
    d['info']['dst'] = str(packet[1].dst)
    d['info']['dst_resolved'] = str(packet[0].addr_oui_resolved)
    d['info']['dst_port'] = packet[2].dstport
    d['info']['src'] = str(packet[1].src)
    d['info']['src_resolved'] = str(packet[0].src_oui_resolved)
    d['info']['src_port'] = packet[2].srcport
    d['info']['layer'] = packet[3].layer_name

    return d


def stp_to_dict(packet):
    d = {'timestamp': str(packet.sniff_time), 'protocol': packet[2].layer_name.upper(), 'size': str(packet.length),
         'info': {}}
    d['info']['dst_resolved'] = str(packet[0].addr_oui_resolved)
    d['info']['src_resolved'] = str(packet[0].src_oui_resolved)

    return d


def arp_to_dict(packet):
    d = {'timestamp': str(packet.sniff_time), 'protocol': packet[1].layer_name.upper(), 'size': str(packet.length),
         'info': {}}
    d['info']['dst_resolved'] = str(packet[0].addr_oui_resolved)
    d['info']['src_resolved'] = str(packet[0].src_oui_resolved)

    return d


def packet_to_dict(packet):
    d = {}
    try:
        protocol = packet[1].proto

        if str(protocol) == '6':  # Protocol = TCP
            print('TCP')
            d = tcp_to_dict(packet)
            if not d:
                print("Empty dict")
        elif str(protocol) == '17':  # Protocol = UDP
            print('UDP')
            d = udp_to_dict(packet)
            if not d:
                print("Empty dict")
    except AttributeError:
        try:
            layer_name = packet[1].layer_name

            if str(layer_name) == 'llc':  # Protocol = STP
                print('STP')
                d = stp_to_dict(packet)
                if not d:
                    print("Empty dict")
            elif str(layer_name) == 'arp':  # Protocol = ARP
                print('ARP')
                d = arp_to_dict(packet)
            else:
                print('Unknown packet')
        except AttributeError:  # Should not get here, but is a safety
            print("Other")
            print(packet)
    if not d:  # Used to find undiscovered protocols
        print("Empty dict")

    json_object = json.dumps(d)
    print(json_object)
    return json_object


capture = pyshark.LiveCapture(interface='enp3s0')
packets = []

for n in capture.sniff_continuously(packet_count=500):
    packets.append(packet_to_dict(n))

print(len(packets))

for i in range(len(packets)):
    print(packets[i])
