class Missing:
    def __bool__(self):
        return False


missing = Missing()


def normalize_prefix(prefix):
    if prefix is None:
        return prefix
    if prefix.islower() and not prefix.endswith("_"):
        prefix += "_"
    return prefix.upper()
