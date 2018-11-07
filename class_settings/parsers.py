import builtins
import functools


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


int = int
float = float
complex = complex


# Sequence types


list = _sequence_parser(list)
tuple = _sequence_parser(tuple)


# Text sequence types


str = str


# Binary sequence types


bytes = bytes
bytearray = bytearray


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
    import json

    return json.loads(value)
