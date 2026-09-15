# resilience-standard.md  (platform, CURRENT - supersedes older docs)

Outbound HTTP: retry 5 times, exponential backoff from 500ms with jitter
(500ms, 1s, 2s, 4s, 8s). Retry on 429 and 5xx only. This is the standard now.
