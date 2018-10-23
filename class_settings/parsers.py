import builtins
import json as json_


def str(value):
    return value


def bool(value):
    value = value.lower()
    if value in ["true", "t", "1", "yes", "y"]:
        return True
    elif value in ["false", "f", "0", "no", "n"]:
        return False
    else:
        raise ValueError


def int(value):
    return builtins.int(value)


def float(value):
    return builtins.float(value)


def json(value):
    return json_.loads(value)
