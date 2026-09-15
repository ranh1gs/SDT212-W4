# retry-policy.md

Retry idempotent GETs 3 times. Backoff 1s, 2s, 4s. Never retry a 4xx.
