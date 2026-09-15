# Week 4 practice: the context lab

Course practice material for Week 4. Not graded. Re-run it to experiment.

`context-lab/` assembles a model context from parts on disk, lets you inspect it,
and runs it against a live model. There is no canned output: every run calls a
real model.

## What it does

`context_lab.py <scenario>` reads a scenario folder under `scenarios/`, assembles
one context in a fixed order (a trusted instruction layer, the scenario
instructions, the task, the selected docs each tagged trusted or untrusted, then
optional conversation history and memory), and sends it to a runner.

- `--show-context` shows the assembled context as titled, colour-coded panels
  (trusted, untrusted, or "from earlier work") with a per-block token estimate
  and a budget bar, then stops. Add `--raw` to print the plain text that goes to
  the model instead; `--no-color` turns colour off.
- `--select a.py,b.md` loads only those docs instead of all of them.
- `--trust docs/x.md=untrusted` moves a doc from the trusted layer to the
  external layer.
- `--no-history` / `--no-memory` drop those blocks.

## Scenarios

Each scenario seeds a failure caused by the context, not the prompt wording, and
each has one fixing move:

| scenario | what is wrong | the move that fixes it |
|---|---|---|
| `dump-all` | two docs state different retry rules and nothing says which governs | `--select retry-policy.md` |
| `injected-doc` | a copied release update is tagged as trusted policy and conflicts with the project’s classification rule | `--trust docs/slack-thread.md=untrusted` |
| `stale-history` | an insistent old thread calls the current config file stale | `--no-history` (or a shorter summary) |
| `poisoned-memory` | a long-term note states a fact the source has since changed | edit or delete the wrong line in `memory.md` |

`GRADED-flaky-cache` is held out for the assignment.

## Memory

`--memory-backend file` (default) loads `memory.md` as written. Every note enters
the context; write, select, and forget are edits to that file. The base lab and
the graded assignment run on this backend and the standard library alone.

`--memory-backend mem0` extracts, stores, and retrieves note facts through
[mem0](https://github.com/mem0ai/mem0), an open-source memory library, configured
to run fully locally (no account, no API key):

```
ollama pull nomic-embed-text
uv run --with-requirements context-lab/requirements-mem0.txt python3 context-lab/context_lab.py <scenario> --memory-backend mem0
```

`uv run --with-requirements` installs mem0's dependencies into an ephemeral
environment for that one run; nothing persists in the system Python.
Hardware-gated, never on the graded path; the assignment always uses the file
backend.

The run shows four memory steps: connect, read notes, extract and store facts,
then retrieve up to five task-relevant memories. Progress messages go to stderr;
`--show-context --raw` still prints the model context to stdout. Saved memories
persist between runs; editing `memory.md` does not clear the saved store.

## Running it

The runner is a local choice, set in `.env` (copy `.env.example`):

- `ollama` (default): start Ollama and `ollama pull qwen2.5:3b` first.
- `cli`: Antigravity's `agy`, this cohort's named capable-agent CLI, is the
  built-in default.
- `endpoint`: OpenRouter, this cohort's named hosted option; pass `--model`
  with a current `:free`-tagged model on the command.

A small local model is the one that shows these failures clearly. A capable
agent often resists the injected line and picks the right doc on its own, which
is itself worth pointing out.

Course-wide tooling, provider, disclosure, and ownership rules are on the Canvas
course information page.

## Tests

```
cd context-lab
python3 -m unittest -v tests.test_context_lab
```

These check the assembler (block order, trust tags, token totals, the `--select`
filter, the flag checks). They make no model calls.
