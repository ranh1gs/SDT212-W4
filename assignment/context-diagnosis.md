# Context assembly diagnosis

Name: Serhii Serdiuk
Date: 2026-09-15

Run everything from `../practice/context-lab/`. Scenario: `GRADED-flaky-cache`.

---

## 1. Baseline context

Command: `python3 context_lab.py GRADED-flaky-cache --show-context`

Per-block list and token estimates (paste the budget section):

```
context budget   (estimate, ~4 chars per token)

  TRUSTED INSTRUCTION LAYER                                ██████████████████████    84 tok
  INSTRUCTIONS (scenario)                                  █████████·············    36 tok
  TASK                                                     ████████████████······    62 tok
  SOURCE docs/cache.py [trusted]                           ██████████············    38 tok
  SOURCE docs/cache-policy.md [trusted]                    ███████████···········    42 tok
  SOURCE docs/metrics.md [trusted]                         ███████···············    27 tok
  SOURCE docs/queue.md [trusted]                           ███████···············    28 tok
  SOURCE docs/onboarding.md [trusted]                      ███████···············    26 tok
  CONVERSATION HISTORY                                     ██████████████████████    84 tok
  MEMORY (episodic / semantic / procedural, backend=file)  █████████████·········    51 tok
  ─────────────────────────────────────────────────────────────────────────────────────────
  total                                                              478 tok
```

Total assembled context: ~478 tokens

## 2. Baseline run

Command used: `python3 context_lab.py GRADED-flaky-cache` (runner set in `.env`: `BENCH_RUNNER=cli`, `BENCH_CMD` pointing `agy` at the model `gpt-oss-120b-medium`)

Provenance line:

```
[provenance] response generated live | via configured local CLI command (sh) | temperature 0.2 | scenario=GRADED-flaky-cache | select=all docs | memory-backend=file | 2026-09-15
```

Baseline output (paste it):

````
TTL: 5 minutes (source: docs/cache-policy.md)

```python
import pytest
from docs.cache import get_cached, _store

@pytest.fixture(autouse=True)
def clear_store():
    # Ensure a clean _store before each test
    _store.clear()

def test_get_cached_hit():
    key = "example"
    value = {"data": 123}
    _store[key] = (value, 0)  # timestamp is irrelevant for this test
    assert get_cached(key) == value

def test_get_cached_miss():
    key = "missing_key"
    with pytest.raises(KeyError) as exc:
        get_cached(key)
    assert exc.value.args[0] == key
```
````

## 3. Diagnosis

Failure category (one Week 4 term): Stale memory (a stored fact changed, and the old value is loaded on every session).

Evidence, quoted from the baseline output:

> TTL: 5 minutes (source: docs/cache-policy.md)

Why this category and not another (one or two sentences): The 5-minute value appears only in `memory.md`, whose episodic note is dated 2026-04-18 and was true then; `docs/cache-policy.md` is marked current and says 10 minutes, and the history says the TTL changed and the policy doc is authoritative. It is not memory poisoning because the note was correct when written, and the model even cites the right doc while carrying the old number from memory.

## 4. The one assembly move

Prediction, written before running the move (fix / partial fix / no change, and
why, tied to your diagnosis): Fix, because the 5-minute value lives only in the two stale memory lines, so forgetting them leaves `docs/cache-policy.md` as the only TTL statement in the context and the model should answer 10 minutes.

Move applied: Forget (memory edit): deleted the stale TTL note from `memory.md`.

Exact command or file change:

```
--- a/practice/context-lab/scenarios/GRADED-flaky-cache/memory.md
+++ b/practice/context-lab/scenarios/GRADED-flaky-cache/memory.md
@@ -1,8 +1,6 @@
 ## Episodic
-2026-04-18: shortened the cache TTL to 5 minutes during the latency work.
 
 ## Semantic
-The cache TTL is 5 minutes.
 
 ## Procedural
 When testing cache code, clear the module _store between tests.
```

## 5. Re-run

Provenance line:

```
[provenance] response generated live | via configured local CLI command (sh) | temperature 0.2 | scenario=GRADED-flaky-cache | select=all docs | memory-backend=file | 2026-09-15
```

New output (paste it):

```
TTL: 10 minutes (source: cache-policy.md)
```

New `--show-context` total: ~453 tokens

## 6. Before and after

Result: improved

Prediction check: did the result match your prediction from section 4? (yes /
partially / no, one line): Yes, the TTL line flipped from 5 to 10 minutes as predicted; the re-run stopped after part 1 and did not print the two tests, which is unrelated to the TTL defect.

One concrete before-and-after detail: Before, `TTL: 5 minutes (source: docs/cache-policy.md)`; after, `TTL: 10 minutes (source: cache-policy.md)`, which now matches the policy doc.

Token-count change: from ~478 to ~453 . Why it moved (or stayed flat): A forget removes two short lines, so the memory block dropped from 51 to 26 tokens and the total stayed roughly flat.

---

## AI-use disclosure

- Tools and models used (name each, or "none"): Claude Code (Claude Fable 5.1) polished text; the two live runs used `gpt-oss-120b-medium` through the `agy` CLI (Antigravity). Trial runs with the agy default model and Gemini 3.6 Flash answered 10 minutes, so the baseline was recorded with `gpt-oss-120b-medium`, which showed the defect.
- What they produced that I kept: the recorded outputs, the `memory.md` edit, and the draft text of sections 3, 4 and 6.
- What I changed or rejected: I read the draft and confirmed the category and the quoted evidence against `scenario-brief.md` and the lecture slides.
- How I checked the result: compared the TTL line and the token totals of the two recorded runs against `docs/cache-policy.md`.
