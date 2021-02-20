from bm_runtime.standard import Standard
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol, TMultiplexedProtocol
from _state import State


class SimpleSwitchAPI:
    client = None
    transport = None
    stateInfo = None

    def __init__(self, port):
        self.stateInfo = State()
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

    def __del__(self):
        self.transport.close()

    def set_counter(self, counter_name, idx, pkts, byts):
        counter = self.stateInfo.get_counter_info(counter_name)
        if counter.is_direct:
            table_name = counter.binding
            self.client.bm_mt_write_counter(
                0, table_name, idx, Standard.BmCounterValue(bytes=byts, packets=pkts))
        else:
            self.client.bm_counter_write(
                0, counter_name, idx, Standard.BmCounterValue(bytes=byts, packets=pkts))

    def set_register(self, reg_name, idx, value):
        register = self.stateInfo.get_register_info(reg_name)
        self.client.bm_register_write(0, register.name, idx, value)



