"""Optional memory backend over an open-source memory library, local only.

This optional practice backend uses a local model to extract notes and retrieve
relevant memories. The base lab and graded assignment use the file backend.

Local configuration only: a local Ollama model for extraction, a local embedder,
and a local on-disk vector store. No account, no API key, no paid tier. Pull the
embedder model named in EMBED_MODEL below, then run this file's caller through
uv with the extra dependencies:

    uv run --with-requirements ../requirements-mem0.txt python3 ../context_lab.py <scenario> --memory-backend mem0

If the library or its local models are absent, context_lab.py stops with a clear
message. The file backend remains available through --memory-backend file.

Contrast with the flat file: the flat file loads every note; this backend seeds
the library from memory.md, then returns only the notes the library retrieves for
the current task.
"""

from __future__ import annotations

import os
import pathlib
import sys

try:
    from mem0 import Memory
except ImportError as exc:
    Memory = None
    _MEM0_IMPORT_ERROR = exc
else:
    _MEM0_IMPORT_ERROR = None

# Read overrides when connecting, after context_lab has loaded the local .env.
LLM_MODEL = "qwen2.5:3b"
EMBED_MODEL = "nomic-embed-text"
STORE_DIR = str(pathlib.Path.home() / ".context-lab-mem0")
OLLAMA_BASE = "http://localhost:11434"


def _local_config() -> dict:
    return {
        "llm": {
            "provider": "ollama",
            "config": {
                "model": os.environ.get("MEM_LLM", LLM_MODEL),
                "ollama_base_url": os.environ.get("MEM_OLLAMA_BASE", OLLAMA_BASE),
                "temperature": 0.1,
            },
        },
        "embedder": {
            "provider": "ollama",
            "config": {
                "model": os.environ.get("MEM_EMBEDDER", EMBED_MODEL),
                "ollama_base_url": os.environ.get("MEM_OLLAMA_BASE", OLLAMA_BASE),
            },
        },
        "vector_store": {
            "provider": "chroma",
            "config": {
                "collection_name": "context_lab",
                "path": os.environ.get("MEM_STORE", STORE_DIR),
            },
        },
    }


class Mem0Backend:
    def __init__(self, path: pathlib.Path):
        self.path = path
        config = _local_config()
        llm_model = config["llm"]["config"]["model"]
        embed_model = config["embedder"]["config"]["model"]
        self._log("1/4 · Connect to local memory")
        self._log(f"Extract facts: {llm_model} through local Ollama.", detail=True)
        self._log(
            f"Search by meaning: {embed_model} embeddings in local Chroma.",
            detail=True,
        )
        self._log(
            "Chroma keyword-search and spaCy notices concern optional features; "
            "this demo uses semantic search.",
            detail=True,
        )
        self._log(
            "A 'multiple PostHog clients' notice concerns diagnostic telemetry queues.",
            detail=True,
        )
        if Memory is None:  # surfaced by context_lab.render_memory
            raise ImportError(
                "the memory library is not installed; see requirements-mem0.txt"
            ) from _MEM0_IMPORT_ERROR

        self.agent_id = "context-lab"
        try:
            self.memory = Memory.from_config(config)
        except Exception as exc:  # config or local-model failure
            raise ImportError(
                f"the memory library could not start with a local configuration ({exc}); "
                f"check that Ollama is running and `ollama pull {embed_model}` has been done"
            ) from exc
        self._log("Connected. Saved memories persist between runs.", detail=True)

    @staticmethod
    def _log(message: str, *, detail: bool = False) -> None:
        # Progress goes to stderr so --show-context --raw stays safe to pipe.
        prefix = "  " if detail else "\n[mem0] "
        print(prefix + message, file=sys.stderr, flush=True)

    @staticmethod
    def _preview(text: str) -> str:
        text = " ".join(text.split())
        return text if len(text) <= 120 else text[:117] + "..."

    def _seed(self) -> None:
        self._log(f"2/4 · Read notes from {self.path.name}")
        text = self.path.read_text(encoding="utf-8")
        notes = [
            line.strip() for line in text.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        self._log(
            f"{len(notes)} note lines; headings and blank lines are skipped.",
            detail=True,
        )
        self._log("3/4 · Extract and store useful facts")
        self._log(
            "The local model reads each line. Mem0 can add, update, or skip a fact.",
            detail=True,
        )
        for index, line in enumerate(notes, 1):
            self._log(f"Note {index}/{len(notes)}: {self._preview(line)}", detail=True)
            added = self.memory.add(line, agent_id=self.agent_id)
            if isinstance(added, dict):
                events = [
                    row.get("event") for row in added.get("results", [])
                    if isinstance(row, dict)
                ]
                changes = [
                    f"{events.count(event)} {label}"
                    for event, label in [
                        ("ADD", "added"), ("UPDATE", "updated"), ("DELETE", "deleted")
                    ]
                    if event in events
                ]
                self._log(
                    ", ".join(changes) if changes else "No memory change returned.",
                    detail=True,
                )
        self._log(
            "Editing memory.md changes the input for this run; it does not clear the saved store.",
            detail=True,
        )

    def render(self, task_text: str) -> str:
        self._seed()
        self._log("4/4 · Search for memories relevant to this task")
        self._log(f"Task: {self._preview(task_text)}", detail=True)
        self._log(
            f"Search scope: {self.agent_id}; retrieve up to 5 matches by meaning.",
            detail=True,
        )
        hits = self.memory.search(
            task_text, filters={"agent_id": self.agent_id}, top_k=5
        )
        results = hits.get("results", hits) if isinstance(hits, dict) else hits
        lines = [str(r.get("memory", r)) for r in results] if results else []
        noun = "memory" if len(lines) == 1 else "memories"
        self._log(f"Retrieved {len(lines)} {noun}.", detail=True)
        for index, line in enumerate(lines, 1):
            self._log(f"{index}. {self._preview(line)}", detail=True)
        if not lines:
            self._log("The context will record that no matching memory was found.", detail=True)
            return "(the memory library retrieved nothing for this task)"
        self._log("These retrieved facts become the MEMORY block in the model context.", detail=True)
        return "retrieved by the memory library for this task:\n" + "\n".join(f"- {ln}" for ln in lines)
