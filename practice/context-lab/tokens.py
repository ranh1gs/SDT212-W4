"""A rough token estimator, standard library only.

There is no real tokenizer here on purpose: this week's lab stays dependency-free,
and the teaching point is that context competes for a finite attention budget, not
exact accounting. Every number this module returns is an estimate and is labelled
as one wherever it is printed.

The estimate is len(text) / 4, rounded, floored at 1 for any non-empty text. That
is close enough to typical English-and-code tokenization to make the point on a
projector: adding a block raises the total, selecting fewer blocks lowers it.
"""

from __future__ import annotations


CHARS_PER_TOKEN = 4


def estimate_tokens(text: str) -> int:
    """Estimated token count for one block of text."""
    stripped = text.strip()
    if not stripped:
        return 0
    return max(1, round(len(stripped) / CHARS_PER_TOKEN))


def budget_report(blocks: list[tuple[str, str, str]]) -> str:
    """Render a per-block token estimate table plus a total.

    blocks is a list of (label, trust_tag, text) tuples in assembly order.
    """
    lines = []
    total = 0
    width = max((len(label) for label, _, _ in blocks), default=20)
    for label, trust, text in blocks:
        n = estimate_tokens(text)
        total += n
        lines.append(f"  {label:<{width}}  ~{n:>4} tokens   {trust}")
    rule = "  " + "-" * (width + 30)
    lines.append(rule)
    lines.append(
        f"  {'total assembled context':<{width}}  ~{total:>4} tokens   "
        f"(estimate, ~{CHARS_PER_TOKEN} chars/token)"
    )
    return "\n".join(lines)
