import itertools


def takefirst(iterable, key=None):
    """
    Returns iterable containing the first
    instance of each item matching the key func.
    """
    keys = set()

    for key, group in itertools.groupby(iterable, key):
        for item in group:
            if key not in keys:
                keys.add(key)
                yield item
