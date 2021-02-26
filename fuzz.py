from multiprocessing import Process, Value
from const import MAX_INSTANCES, PORT_COUNT, PRIORITY_QUEUE, STOP_THRESHOLD, REDIS_CONN1
from switch import SimpleSwitch
from corpus import import_seed, get_one_mutated, new_cov
from n4j import save
import time
import pickle
from mutable_types import *
from ipv4 import *

# Init
M = []
for i in range(MAX_INSTANCES):
    M.append(SimpleSwitch(index=i+10, port_count=PORT_COUNT))
import_seed()


def state_changed(_hash):
    if REDIS_CONN1.exists(_hash):
        return False
    REDIS_CONN1.set(_hash, b'1')
    return True


counter = Value('i', 0)


# Fuzz!
def fuzz(m: SimpleSwitch, i: int):
    non_unique_cnt = 0
    prev_state_hash = "Init"
    fp = open(f"neo_file/{i}.n4j", "a+")
    while 1:
        port, content, is_cp = get_one_mutated()
        if not is_cp:
            has_new_cov, intf, pkt, stateHash = m.send_pkt(content, port)
        else:
            c = pickle.loads(content)
            for k in c:
                c[k].mutate()
            has_new_cov, stateHash = m.control_plane_intake(**c)

        if has_new_cov:
            non_unique_cnt = 0
            new_cov(port, content, is_cp)
        else:
            non_unique_cnt += 1
            if non_unique_cnt > STOP_THRESHOLD:
                cstate = PRIORITY_QUEUE.pop()
                if cstate:
                    if type(cstate) != bytes:
                        cstate = cstate.encode("latin-1")
                    vid = m._id
                    del m
                    time.sleep(0.5)
                    stateFile = b"state/" + cstate
                    m = SimpleSwitch(index=vid+10, port_count=PORT_COUNT, state_file_loc=stateFile.decode("latin-1"))

        if stateHash and state_changed(stateHash):
            PRIORITY_QUEUE.push(stateHash, 100)

        # Save to neo4j
        save(
             prev_state_hash,
             stateHash if stateHash else prev_state_hash,
             (port, content, is_cp),
             (intf, pkt, False) if not is_cp else (None, None, True),
             fp
         )
        if stateHash:
            prev_state_hash = stateHash
        global counter
        with counter.get_lock():
            counter.value += 1


for i in range(MAX_INSTANCES):
    p = Process(target=fuzz, args=(M[i], i))
    p.start()


while 1:
    print(f"========= Records: {counter.value} =========")
    time.sleep(2)
