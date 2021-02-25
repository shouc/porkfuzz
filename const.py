import redis
from rpq.RpqQueue import RpqQueue
from py2neo import Graph
import os
from target.baseline import conf


INSTRUMENTED_SWITCH_PATH = "/home/shou/coding/behavioral-model/targets/simple_switch/.libs/simple_switch"
COMPILED_JSON_PROGRAM = "/home/shou/coding/porkfuzz/target/baseline/test.bmv2/test.json"
MAX_INSTANCES = 3
PORT_COUNT = 3
STOP_THRESHOLD = 10
REDIS_CONN1 = redis.Redis(host='localhost', port=6379, db=0)
REDIS_CONN2 = redis.Redis(host='localhost', port=6379, db=1)
PRIORITY_QUEUE = RpqQueue(redis.Redis(host='localhost', port=6379, db=1), 'state_queue')
NEO4J_CONN = Graph("bolt://localhost:7687", password="shou123")
REDIS_CONN1.flushall()
os.system("pkill -f 'simple_switch'")

CONTROL_PLANE_OBJ = conf.ControlPlane


