from const import NEO4J_CONN
from py2neo import Graph, Node, Relationship
from corpus import hash_packet

PacketOf = Relationship.type("PacketOf")
ResultOf = Relationship.type("ResultOf")


def save(prev_state_hash, curr_state_hash, pkt_obj, fp):
    fp.write(f"{prev_state_hash},{curr_state_hash},{hash_packet(*pkt_obj)}\n")


def _save(prev_state_hash, curr_state_hash, pkt_obj):
    prevStateNode = Node("State", hash=prev_state_hash)
    currStateNode = Node("State", hash=curr_state_hash)
    pkt = Node("Packet", hash=pkt_obj)
    NEO4J_CONN.merge(PacketOf(prevStateNode, pkt) | ResultOf(pkt, currStateNode), "Packet", "hash")


if __name__ == '__main__':
    import os
    for i in os.listdir("neo_file"):
        with open(f"neo_file/{i}") as fp:
            x = fp.read().split("\n")
            for j in x:
                u = j.split(",")
                if len(u) == 3:
                    prev = u[0]
                    curr = u[1]
                    pkt = u[2]
                    _save(prev, curr, pkt)
