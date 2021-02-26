from ipv4 import Cidr
from base64 import b64encode
from scapy.all import *
from mutable_types import Integer


def a():
    pkt = b64encode(raw(Ether()/IP(dst="137.137.137.137")))
    print(f"0,{pkt.decode('latin-1')},0")


def b():
    import pickle
    pkt = b64encode(pickle.dumps({
        "cidr": Cidr(),
        "port": Integer()
    }))
    print(f"0,{pkt.decode('latin-1')},1")

a()
