import json
from const import COMPILED_JSON_PROGRAM


def enum(type_name, *sequential, **named):
    enums = dict(list(zip(sequential, list(range(len(sequential))))), **named)
    reverse = dict((value, key) for key, value in enums.items())

    @staticmethod
    def to_str(x):
        return reverse[x]
    enums['to_str'] = to_str

    @staticmethod
    def from_str(x):
        return enums[x]

    enums['from_str'] = from_str
    return type(type_name, (), enums)


MeterType = enum('MeterType', 'packets', 'bytes')


class MeterArray:
    def __init__(self, name, id_):
        self.name = name
        self.id_ = id_
        self.type_ = None
        self.is_direct = None
        self.size = None
        self.binding = None
        self.rate_count = None

    def meter_str(self):
        return "{0:30} [{1}, {2}]".format(self.name, self.size,
                                          MeterType.to_str(self.type_))


class CounterArray:
    def __init__(self, name, id_):
        self.name = name
        self.id_ = id_
        self.is_direct = None
        self.size = None
        self.binding = None

    def counter_str(self):
        return "{0:30} [{1}]".format(self.name, self.size)


class RegisterArray:
    def __init__(self, name, id_):
        self.name = name
        self.id_ = id_
        self.width = None
        self.size = None

    def register_str(self):
        return "{0:30} [{1}]".format(self.name, self.size)


class State:
    json_obj = None
    counter_arr = []
    meter_arr = []
    register_arr = []

    def __get_json_key(self, _key):
        return self.json_obj.get(_key, [])

    def __init__(self):
        with open(COMPILED_JSON_PROGRAM) as fp:
            self.json_obj = json.load(fp)
        for j_meter in self.__get_json_key("meter_arrays"):
            meter_array = MeterArray(j_meter["name"], j_meter["id"])
            if "is_direct" in j_meter and j_meter["is_direct"]:
                meter_array.is_direct = True
                meter_array.binding = j_meter["binding"]
            else:
                meter_array.is_direct = False
                meter_array.size = j_meter["size"]
            meter_array.type_ = MeterType.from_str(j_meter["type"])
            meter_array.rate_count = j_meter["rate_count"]
            self.meter_arr.append(meter_array)

        for j_counter in self.__get_json_key("counter_arrays"):
            counter_array = CounterArray(j_counter["name"], j_counter["id"])
            counter_array.is_direct = j_counter["is_direct"]
            if counter_array.is_direct:
                counter_array.binding = j_counter["binding"]
            else:
                counter_array.size = j_counter["size"]
            self.counter_arr.append(counter_array)

        for j_register in self.__get_json_key("register_arrays"):
            register_array = RegisterArray(j_register["name"], j_register["id"])
            register_array.size = j_register["size"]
            register_array.width = j_register["bitwidth"]
            self.register_arr.append(register_array)

    def get_counter_info(self, name) -> MeterArray:
        for i in self.counter_arr:
            if i.name == name:
                return i

    def get_meter_info(self, name) -> MeterArray:
        for i in self.meter_arr:
            if i.name == name:
                return i

    def get_register_info(self, name) -> MeterArray:
        for i in self.register_arr:
            if i.name == name:
                return i
