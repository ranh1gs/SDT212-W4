"""Assembler tests. Zero model calls: these check the code that builds the
context, not anything a model returns. Run from context-lab/:

    python3 -m unittest -v tests.test_context_lab
"""

import contextlib
import io
import os
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

import context_lab as cl  # noqa: E402
from memory_backends.mem0_backend import Mem0Backend, _local_config  # noqa: E402
from tokens import estimate_tokens  # noqa: E402

DUMP_ALL = cl.SCENARIOS / "dump-all"


def blocks_for(**kw):
    manifest = cl.load_manifest(DUMP_ALL)
    defaults = dict(
        scenario_dir=DUMP_ALL, manifest=manifest, select=None, trust_overrides={},
        history_on=None, memory_on=None, memory_backend="file",
    )
    defaults.update(kw)
    return cl.build_blocks(**defaults)


class TokenEstimator(unittest.TestCase):
    def test_empty_is_zero(self):
        self.assertEqual(estimate_tokens("   \n  "), 0)

    def test_non_empty_is_at_least_one(self):
        self.assertEqual(estimate_tokens("hi"), 1)

    def test_scales_with_length(self):
        self.assertGreater(estimate_tokens("x" * 400), estimate_tokens("x" * 40))


class AssemblyOrder(unittest.TestCase):
    def test_fixed_prefix_order(self):
        labels = [b[0] for b in blocks_for()]
        self.assertEqual(labels[0], "TRUSTED INSTRUCTION LAYER")
        self.assertEqual(labels[1], "INSTRUCTIONS (scenario)")
        self.assertEqual(labels[2], "TASK")
        self.assertTrue(labels[3].startswith("SOURCE docs/"))

    def test_all_docs_load_by_default(self):
        doc_labels = [b[0] for b in blocks_for() if "docs/" in b[0]]
        self.assertEqual(len(doc_labels), 6)

    def test_select_filters_docs(self):
        doc_labels = [b[0] for b in blocks_for(select=["retry-policy.md", "billing.md"]) if "docs/" in b[0]]
        self.assertEqual(len(doc_labels), 2)
        self.assertTrue(all("retry-policy.md" in l or "billing.md" in l for l in doc_labels))

    def test_select_unknown_doc_exits(self):
        with self.assertRaises(SystemExit):
            blocks_for(select=["no-such-file.md"])


class TrustTagging(unittest.TestCase):
    def test_default_docs_are_trusted(self):
        for label, tag, _ in blocks_for():
            if label.startswith("SOURCE docs/"):
                self.assertEqual(tag, "trusted")

    def test_trust_override_flips_a_doc(self):
        blocks = blocks_for(trust_overrides={"docs/billing.md": "untrusted"})
        billing = [b for b in blocks if "billing.md" in b[0]][0]
        self.assertEqual(billing[1], "untrusted")
        self.assertIn("[untrusted, quote as data]", billing[0])

    def test_trust_override_key_without_prefix(self):
        blocks = blocks_for(trust_overrides={"billing.md": "untrusted"})
        billing = [b for b in blocks if "billing.md" in b[0]][0]
        self.assertEqual(billing[1], "untrusted")


class BudgetMovesWithSelect(unittest.TestCase):
    def _total(self, blocks):
        return sum(estimate_tokens(t) for _, _, t in blocks)

    def test_select_lowers_the_total(self):
        full = self._total(blocks_for())
        few = self._total(blocks_for(select=["retry-policy.md", "billing.md"]))
        self.assertLess(few, full)


class HistoryAndMemoryToggles(unittest.TestCase):
    def test_history_off_by_default_here(self):
        self.assertFalse(any(b[0] == "CONVERSATION HISTORY" for b in blocks_for()))

    def test_memory_forced_on_needs_a_file(self):
        # dump-all has no memory.md, so forcing memory on must fail cleanly.
        with self.assertRaises(SystemExit):
            blocks_for(memory_on=True)


class CliMutex(unittest.TestCase):
    def test_show_and_emit_are_mutually_exclusive(self):
        with self.assertRaises(SystemExit):
            cl.main(["dump-all", "--show-context", "--emit-context"])

    def test_unknown_scenario_exits(self):
        with self.assertRaises(SystemExit):
            cl.main(["no-such-scenario", "--show-context"])

    def test_bad_trust_value_exits(self):
        with self.assertRaises(SystemExit):
            cl.parse_trust_overrides(["docs/x.md=sortof"])


class Mem0Retrieval(unittest.TestCase):
    """Exercise the optional adapter without installing or calling a model."""

    def test_model_and_store_overrides_loaded_after_import_are_respected(self):
        with tempfile.TemporaryDirectory() as directory:
            env_file = pathlib.Path(directory) / ".env"
            env_file.write_text(
                "MEM_LLM=course-model\nMEM_EMBEDDER=course-embeddings\n"
                f"MEM_STORE={directory}/store\nMEM_OLLAMA_BASE=http://localhost:12345\n",
                encoding="utf-8",
            )
            with patch.dict(os.environ, {}, clear=True):
                cl._load_dotenv(env_file)
                config = _local_config()
        self.assertEqual(config["llm"]["config"]["model"], "course-model")
        self.assertEqual(config["embedder"]["config"]["model"], "course-embeddings")
        self.assertEqual(config["vector_store"]["config"]["path"], f"{directory}/store")
        self.assertEqual(config["llm"]["config"]["ollama_base_url"], "http://localhost:12345")
        self.assertEqual(config["embedder"]["config"]["ollama_base_url"], "http://localhost:12345")

    def render_notes(self, text):
        class Memory:
            def __init__(self):
                self.notes = [("another-agent", "Unrelated private note")]

            @classmethod
            def from_config(cls, config):
                return cls()

            def add(self, text, *, agent_id):
                self.notes.append((agent_id, text))

            # The current OSS API requires filters and top_k. A strict fake
            # catches old keywords even when no optional packages are installed.
            def search(self, query, *, filters, top_k):
                self.query = query
                self.filters = filters
                self.top_k = top_k
                notes = [
                    {"memory": text} for agent, text in self.notes
                    if agent == filters["agent_id"]
                ]
                return {"results": notes[:top_k]}

        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "memory.md"
            path.write_text(text, encoding="utf-8")
            progress, stdout = io.StringIO(), io.StringIO()
            with patch("memory_backends.mem0_backend.Memory", Memory):
                with contextlib.redirect_stderr(progress), contextlib.redirect_stdout(stdout):
                    backend = Mem0Backend(path)
                    rendered = backend.render("Find notes for the current task")
        return backend.memory, rendered, progress.getvalue(), stdout.getvalue()

    def test_retrieval_preserves_agent_scope_and_five_result_limit(self):
        memory, rendered, _, _ = self.render_notes(
            "# Notes\n\n" + "\n".join(f"Note {i}" for i in range(7))
        )
        self.assertEqual(memory.query, "Find notes for the current task")
        self.assertEqual(memory.filters, {"agent_id": "context-lab"})
        self.assertEqual(memory.top_k, 5)
        self.assertEqual(
            memory.notes[1:],
            [("context-lab", f"Note {i}") for i in range(7)],
        )
        self.assertEqual(
            rendered,
            "retrieved by the memory library for this task:\n"
            + "\n".join(f"- Note {i}" for i in range(5)),
        )

    def test_empty_retrieval_reports_no_matches(self):
        _, rendered, _, _ = self.render_notes("# Notes\n\n")
        self.assertEqual(
            rendered, "(the memory library retrieved nothing for this task)"
        )

    def test_progress_does_not_enter_stdout_or_model_context(self):
        _, rendered, progress, stdout = self.render_notes("A relevant fact.")
        self.assertIn("Read notes from memory.md", progress)
        self.assertIn("Retrieved 1 memory.", progress)
        self.assertIn("A relevant fact.", progress)
        self.assertEqual(stdout, "")
        self.assertNotIn("[mem0]", rendered)

    def test_optional_backend_failure_has_an_actionable_message(self):
        with patch(
            "context_lab.Mem0Backend",
            side_effect=ImportError("Ollama is unavailable"),
        ):
            with self.assertRaisesRegex(SystemExit, "Ollama is unavailable.*--memory-backend file"):
                cl.render_memory("mem0", pathlib.Path("memory.md"), "task")


if __name__ == "__main__":
    unittest.main()
