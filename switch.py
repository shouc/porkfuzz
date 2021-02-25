import sys
from const import *
import random
from subprocess import Popen, PIPE
from coverage import Coverage
import time
import os
from scapy.all import sendp, sniff, conf
from multiprocessing import Process, Queue
from api_wrapper import SimpleSwitchAPI

conf.verb = 0


class SimpleSwitch:
    process = None
    _id = -1
    cov = None
    thrift_port = 0
    interfaces = []
    api = None
    port_count = 0
    control_plane = None

    def create_veth(self, names):
        for name in names:
            os.system(f"ip link add name {name} type veth peer name {name}_p")
            os.system(f"ip link set dev {name} up")
            os.system(f"ip link set dev {name}_p up")
            os.system(f"ip link set {name} mtu 950")
            os.system(f"ip link set {name}_p mtu 950")

    def __init__(self, index: int = 1, port_count: int = 5, state_file_loc=None):
        print(state_file_loc)
        self._id = index
        self.port_count = port_count
        # Coverage
        self.cov = Coverage(self._id)

        # Switch
        ports = [f"veth_{self._id}_{x}" for x in range(port_count)]
        self.interfaces = ports
        self.create_veth(ports)
        ports_cmd = []
        for k, i in enumerate(ports):
            ports_cmd.append("--interface")
            ports_cmd.append(f"{k}@{i}")
        self.thrift_port = self._id * 1000

        state_info = ["--restore-state", str(state_file_loc)] if state_file_loc else []
        self.process = Popen([
            INSTRUMENTED_SWITCH_PATH,
            *ports_cmd,
            "--device-id", str(self._id),
            "--thrift-port", str(self.thrift_port),
            *state_info,
            COMPILED_JSON_PROGRAM
        ], stdout=sys.stdout, stderr=sys.stderr, stdin=PIPE, env=os.environ)
        time.sleep(0.5)
        self.cov.post_boot()

        # Start Control Plane
        self.control_plane = CONTROL_PLANE_OBJ(self.thrift_port)

        # Connect to Thrift Instance
        self.api = SimpleSwitchAPI(self.thrift_port)

        print("Init Completed!")

    @staticmethod
    def __send_pkt(this, content: bytes, port: int):
        this.cov.pre_execute()

        # Send Packet
        interface = f"veth_{this._id}_{port}_p"
        try:
            sendp(content, iface=interface)
        except Exception as e:
            print(e)

    @staticmethod
    def __sniff_pkt(this, i, q):
        try:
            pkt = sniff(iface=f"{i}_p", timeout=0.3)[0]
            # Get State Info
            stateHash = this.api.client.bm_serialize_state()

            # Get Coverage Info
            result = this.cov.cov_evaluate()

            q.put((i, pkt, stateHash, result))

        except IndexError:
            pass

    def send_pkt(self, content, port):
        q_sniff = Queue()
        for i in self.interfaces:
            if port == int(i.split("_")[2]):
                continue
            sniff_p = Process(target=SimpleSwitch.__sniff_pkt, args=(self, i, q_sniff))
            sniff_p.start()
        send_p = Process(target=SimpleSwitch.__send_pkt, args=(self, content, port))
        send_p.start()
        send_p.join()
        # print(q_sniff.qsize())
        try:
            intf, ppkt, stateHash, newCov = q_sniff.get(timeout=1)
        except:
            intf, ppkt, stateHash, newCov = None, None, None, None  # dropped or bounced
        if newCov == 1:
            print(f"New coverage with {self.cov.found_edge()} edges")
        else:
            # print(self.cov.found_edge())
            pass
        return newCov, intf, ppkt, stateHash

    def control_plane_intake(self, **kwargs):
        self.cov.pre_execute()
        self.control_plane.TakeInput(**kwargs)
        hasNewCov = self.cov.cov_evaluate()
        stateHash = self.api.client.bm_serialize_state()
        return hasNewCov, stateHash

    def __del__(self):
        self.process.kill()
        self.cov.cov_clear_bitmap()
        self.cov.cov_shutdown()
