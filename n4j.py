from const import NEO4J_CONN
from py2neo import Graph, Node, Relationship
from corpus import hash_packet

InputOf = Relationship.type("InputOf")
ResultOf = Relationship.type("ResultOf")


def save(prev_state_hash, curr_state_hash, pkt_obj, result_obj, fp):
    fp.write(f"{prev_state_hash},{curr_state_hash},{hash_packet(*pkt_obj)},{hash_packet(*result_obj)}\n")


def _save(prev_state_hash, curr_state_hash, in_pkt, out_pkt):
    prevStateNode = Node("State", hash=prev_state_hash)
    currStateNode = Node("State", hash=curr_state_hash)
    in_pkt = Node("Packet", hash=in_pkt)
    out_pkt = Node("Packet", hash=out_pkt)
    print(1)
    print(NEO4J_CONN.merge(InputOf(prevStateNode, in_pkt) |
                           ResultOf(in_pkt, currStateNode) |
                           ResultOf(in_pkt, out_pkt), "Packet", "hash"))


if __name__ == '__main__':
    import os
    for i in os.listdir("neo_file"):
        with open(f"neo_file/{i}") as fp:
            print(fp)
            x = fp.read().split("\n")
            for j in x:
                u = j.split(",")
                if len(u) == 4:
                    prev = u[0]
                    curr = u[1]
                    in_pkt = u[2]
                    out_pkt = u[3]
                    _save(prev, curr, in_pkt, out_pkt)
        break
