import builtins
import functools
import json as json_


def _get_parser(parser):
    is_builtin = parser in vars(builtins).values()
    is_class = isinstance(parser, type)
    if is_builtin and is_class and parser.__name__ in globals():
        parser = globals()[parser.__name__]
    return parser


def _sequence_parser(type):
    @functools.wraps(type)
    def parser(value, separator=",", subparser=None):
        items = map(builtins.str.strip, value.split(separator))
        if subparser is not None:
            subparser = _get_parser(subparser)
            items = map(subparser, items)
        return type(items)

    return parser


# Numeric types


def int(value, base=10):
    return builtins.int(value, base)


def float(value):
    return builtins.float(value)


def complex(value):
    return builtins.complex(value)


# Sequence types


list = _sequence_parser(list)
tuple = _sequence_parser(tuple)


# Text sequence types


def str(value):
    return value


# Binary sequence types


def bytes(value, encoding, errors="strict"):
    return builtins.bytes(value, encoding, errors)


def bytearray(value, encoding, errors="strict"):
    return builtins.bytearray(value, encoding, errors)


# Set types


set = _sequence_parser(set)
frozenset = _sequence_parser(frozenset)


# Mapping types


def dict(value, separator=",", itemseparator="=", keyparser=None, valueparser=None):
    items = map(builtins.str.strip, value.split(separator))
    keys, values = zip(
        *(map(builtins.str.strip, item.split(itemseparator)) for item in items)
    )
    if keyparser is not None:
        keyparser = _get_parser(keyparser)
        keys = map(keyparser, keys)
    if valueparser is not None:
        valueparser = _get_parser(valueparser)
        values = map(valueparser, values)
    return builtins.dict(zip(keys, values))


# Other types


def bool(value):
    if value.lower() in ["true", "t", "yes", "y", "on", "1"]:
        return True
    elif value.lower() in ["false", "f", "no", "n", "off", "0"]:
        return False
    else:
        raise ValueError("Could not convert {!r} to bool".format(value))


# Custom


def json(value):
    return json_.loads(value)
