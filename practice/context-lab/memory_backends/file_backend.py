"""The default memory backend: a plain Markdown file, loaded as-is.

Everything in memory.md enters the context on every run. Write, select, and
forget are literal edits to the file: add a line, delete a line, re-run and
watch the token total move. This is the memory the lab teaches.
"""

from __future__ import annotations

import pathlib
import sys


class FileBackend:
    def __init__(self, path: pathlib.Path):
        self.path = path

    def render(self, task_text: str) -> str:
        try:
            text = self.path.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            sys.exit(f"error: memory file not found: {self.path}")
        # task_text is unused: a flat file loads every note regardless of relevance.
        # That is the point of the contrast with the mem0 backend, which retrieves.
        return text
