import pyshark

capture = pyshark.LiveCapture()
for n in capture.sniff_continuously():
    print(n)
