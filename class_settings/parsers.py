import builtins
import json as json_


def str(value):
    return value


def bool(value):
    if value.lower() in ["true", "t", "1", "yes", "y"]:
        return True
    elif value.lower() in ["false", "f", "0", "no", "n"]:
        return False
    else:
        raise ValueError("Could not convert {!r} to bool".format(value))


def int(value, base=10):
    return builtins.int(value, base)


def float(value):
    return builtins.float(value)


def json(value):
    return json_.loads(value)
