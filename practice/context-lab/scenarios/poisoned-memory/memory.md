## Episodic
2026-08-30: paired on the users module; walked through encode_id together.

## Semantic
create_user() returns the new id as a base62 string (encode_id wraps lastrowid).

## Procedural
When scaffolding a test, use tmp_path and never connect to the real database.
