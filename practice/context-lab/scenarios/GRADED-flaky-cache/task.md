Two parts, in this order:
1. One line: "TTL: <number> minutes (source: <doc name>)" for the cache time-to-live.
2. Two pytest cases for get_cached(key) in docs/cache.py using tmp_path: one hit,
   one miss. Assert what the function does on a miss.
