# auth-flow.md

Token refresh retries twice, 10s apart, then forces a full re-login.
The access token is refreshed 30 seconds before expiry.
