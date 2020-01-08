import itertools


def takefirst(iterable, key=None):
    """
    Works like itertools.groupby, but only
    returns the first instance matching the key.
    """
    keys = set()

    for key, group in itertools.groupby(iterable, key):
        for item in group:
            if key not in keys:
                keys.add(key)
                yield item
