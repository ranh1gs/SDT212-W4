user: this cache thread is ancient, but do you remember the TTL offhand?
lead: not off the top of my head, it changed at some point. check the cache policy doc under docs/, that one is authoritative.
user: right. and a miss raises rather than returning None?
lead: yes, KeyError on a miss. that part has not changed.
user: thanks
lead: np
