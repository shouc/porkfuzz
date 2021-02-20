from scapy.all import *
from base64 import b64encode
pkt = b64encode(raw(Ether()/IP(dst="10.10.3.90")))
print(f"0,{pkt.decode('latin-1')},0")
