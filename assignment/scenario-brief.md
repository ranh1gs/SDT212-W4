# Scenario brief: GRADED-flaky-cache

Read this before you start. It describes the scenario; it does not tell you what
is wrong with the context. That is your job.

## The task the model is given

Write two pytest cases for `get_cached(key)` in `docs/cache.py`: one for a hit,
one for a miss, using `tmp_path`. Assert what the function does on a miss.

## What is in the scenario folder

- `docs/cache.py` : the function under test.
- `docs/cache-policy.md` : the written cache policy.
- three more docs about unrelated parts of the system.
- `history.md` : an earlier chat thread about the cache.
- `memory.md` : long-term notes in three sections (episodic, semantic, procedural).

By default `context_lab.py GRADED-flaky-cache` loads all of it.

## The contract you are testing against

`get_cached(key)` returns the cached value on a hit and **raises `KeyError` on a
miss**. That is what `docs/cache.py` and `docs/cache-policy.md` say. Your two
tests should reflect that contract.

## What to hand in

`context-diagnosis.md`, filled in and uploaded to the Week 4 Canvas assignment.
