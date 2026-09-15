_store = {}

def get_cached(key):
    if key not in _store:
        raise KeyError(key)      # a miss raises
    value, ts = _store[key]
    return value
