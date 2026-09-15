# Cache policy (docs/, current)

Entries live for 10 minutes (TTL). A read past the TTL is treated as a miss.
A miss raises KeyError. Never return a sentinel on a miss.
