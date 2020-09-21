import pyshark


def tcp_to_dict(packet):
    d = {'eth': {}, 'ip': {}, 'tcp': {}}
    d['eth']['src'] = packet[0].src_oui_resolved
    d['eth']['dst'] = packet[0].addr_oui_resolved
    d['ip']['src'] = packet[1].src
    d['ip']['dst'] = packet[1].dst
    d['tcp']['src'] = packet[2].srcport
    d['tcp']['dst'] = packet[2].dstport

    return d


def udp_to_dict(packet):
    d = {}

    if str(packet[3].layer_name) == 'ssdp':
        d = {'eth': {}, 'ip': {}, 'udp': {}, 'ssdp': 'ssdp'}
    elif str(packet[3].layer_name) == 'dns':
        d = {'eth': {}, 'ip': {}, 'udp': {}, 'dns': 'dns'}
    elif str(packet[3].layer_name) == 'mdns':
        d = {'eth': {}, 'ip': {}, 'udp': {}, 'mdns': 'mdns'}
    elif str(packet[3].layer_name) == 'db-lsp-disc':
        d = {'eth': {}, 'ip': {}, 'udp': {}, 'db-lsp-disc': 'db-lsp-disc'}
    else:
        d = {'eth': {}, 'ip': {}, 'udp': {}}

    d['eth']['src'] = packet[0].src_oui_resolved
    d['eth']['dst'] = packet[0].addr_oui_resolved
    d['ip']['src'] = packet[1].src
    d['ip']['dst'] = packet[1].dst
    d['udp']['src'] = packet[2].srcport
    d['udp']['dst'] = packet[2].dstport

    return d


def stp_to_dict(packet):
    d = {'eth': {}, 'llc': 'llc', 'stp': 'stp'}

    d['eth']['src'] = packet[0].src_oui_resolved
    d['eth']['dst'] = packet[0].addr_oui_resolved

    return d


def packet_to_dict(packet):
    d = {}
    try:
        protocol = packet[1].proto

        if str(protocol) == '6':  # Protocol = TCP
            d = tcp_to_dict(packet)
        elif str(protocol) == '17':  # Protocol = UDP
            print('UDP')
            d = udp_to_dict(packet)
    except AttributeError:
        try:
            llc_layer = packet[1].layer_name

            if str(llc_layer) == 'llc':  # Protocol = STP
                print('STP')
                d = stp_to_dict(packet)
        except AttributeError:  # Have not reached here yet
            print("Other")
            print(packet)

    return d


capture = pyshark.LiveCapture(interface='enp3s0')
packets = []

for n in capture.sniff_continuously(packet_count=500):
    packets.append(packet_to_dict(n))

print(len(packets))

for i in range(len(packets)):
    print(packets[i])
