from scapy.all import rdpcap, raw
import os
import base64
import hashlib


for i in os.listdir("pcap/"):
    x = rdpcap(f"pcap/{i}")
    interface = i.split("_")[2].replace(".pcap", "").encode('latin-1')
    for j in x:
        jb = base64.b64encode(raw(j))
        hs = hashlib.sha1(b",".join([interface, jb, b'0'])).hexdigest()
        print(hs, j)
