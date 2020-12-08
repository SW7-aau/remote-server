import pyshark

capture = pyshark.LiveCapture(interface='eth0')
for n in capture.sniff_continuously():
    print(n)
