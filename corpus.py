from const import REDIS_CONN1, REDIS_CONN2, PORT_COUNT
import os
import random
import base64
import hashlib
from scapy.all import raw


class Mutator:
    @staticmethod
    def flip_bit(content: bytes):  # max flip is a byte
        cl = len(content)
        flip_pos = random.randint(0, cl - 1)
        content_b = bytearray(content)
        content_b[flip_pos] ^= random.randint(0, 255)
        return bytes(content_b)

    @staticmethod
    def switch_port():
        return random.randint(0, PORT_COUNT - 1)

    @staticmethod
    def concat(content: bytes):
        return content + content

    @staticmethod
    def havoc(content: bytes):
        for i in range(random.randint(0, 20)):
            content = Mutator.flip_bit(content)
        return content

    @staticmethod
    def mutate(port, packet, is_cp) -> (int, bytes, bool):
        method = random.randint(0, 3)
        if method == 0:
            return port, Mutator.flip_bit(packet), is_cp == b'1'
        elif method == 1:
            return Mutator.switch_port(), packet, is_cp == b'1'
        elif method == 2:
            return port, Mutator.concat(packet), is_cp == b'1'
        elif method == 3:
            return Mutator.switch_port(), Mutator.havoc(packet), is_cp == b'1'


def import_seed():
    corpus_files = os.listdir("seed/")
    assert len(corpus_files) > 0, "No seed provided :("
    for i in corpus_files:
        with open(f"seed/{i}", 'rb') as fp:
            info = fp.read()
        info_arr = info.split(b",")  # Port, Packet, For Control Plane?
        assert len(info_arr) == 3, "Malformed Seed"
        REDIS_CONN1.sadd("seed", info)


def get_one_mutated():
    seed = REDIS_CONN1.srandmember("seed")
    assert seed is not None, "Weird, runs out of seed"
    seed_arr = seed.split(b',')
    assert len(seed_arr) == 3, "Weird, malformed seed"
    seed_arr[1] = base64.b64decode(seed_arr[1])
    seed_arr[0] = int(seed_arr[0])
    return Mutator.mutate(*seed_arr)


def serialize(*args):
    v = list(args)
    v[1] = base64.b64encode(raw(args[1]))
    v[2] = b'1' if args[2] else b'0'
    v[0] = str(v[0]).encode('latin-1')
    return b",".join(v)


def new_cov(*args):
    REDIS_CONN1.sadd("seed", serialize(*args))


def hash_packet(*args):
    if args[0] is None:
        return b"BOUNCE_OR_DROPED"
    val = serialize(*args)
    hs = hashlib.sha1(val).hexdigest()
    REDIS_CONN2.set(hs, val)
    return hs


def save_to_neo4j(prev_state_hash, scapy_pkt, res, state_hash):
    pass
