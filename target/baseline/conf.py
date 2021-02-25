from bm_runtime.standard import Standard as st
from bm_runtime.standard import Standard
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol, TMultiplexedProtocol
from ipv4 import Cidr
import struct


class ControlPlane:
    client = None
    transport = None

    def __init__(self, port):
        transport = TSocket.TSocket('127.0.0.1', port)

        # Buffering is critical. Raw sockets are very slow
        transport = TTransport.TBufferedTransport(transport)

        # Wrap in a protocol
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        protocol = TMultiplexedProtocol.TMultiplexedProtocol(
            protocol, "standard")
        self.client = Standard.Client(protocol)
        self.transport = transport
        transport.open()

    def __add_table_entry(self, ip: bytes, _action: bytes, prefix_length: int):
        match = [st.BmMatchParam(
            type=1,
            exact=None,
            lpm=st.BmMatchParamLPM(key=ip, prefix_length=prefix_length),
            ternary=None
        )]
        action = [bytearray(_action)]
        entry_handle = self.client.bm_mt_add_entry(
            0, 'my_ingress.ipv4_match', match, "my_ingress.to_port_action", action,
            st.BmAddEntryOptions(priority=0)
        )
        print(entry_handle)

    def TakeInput(self, cidr=Cidr(), port=1):
        ip, prefix = cidr.get()
        to_port = struct.pack("b", 0) + struct.pack("b", port % 3)
        try:
            self.__add_table_entry(ip, to_port, prefix)
        except Exception as e:
            print(e)


# x = ControlPlane(9090)
# x.__add_table_entry()

