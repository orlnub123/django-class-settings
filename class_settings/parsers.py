import builtins
import json as json_


def str(value):
    return value


def bool(value):
    if value.lower() in ["true", "t", "yes", "y", "on", "1"]:
        return True
    elif value.lower() in ["false", "f", "no", "n", "off", "0"]:
        return False
    else:
        raise ValueError("Could not convert {!r} to bool".format(value))


def int(value, base=10):
    return builtins.int(value, base)


def float(value):
    return builtins.float(value)


def json(value):
    return json_.loads(value)
