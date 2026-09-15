"""Console rendering for the context lab. Standard library only.

Colour turns itself off when the output is piped or redirected, when NO_COLOR is
set, or when --no-color is passed. The point of the pretty view is to make the
assembled context legible on a projector: each block titled, its trust tag
colour-coded, and the token budget shown as a proportional bar.
"""

from __future__ import annotations

import os
import shutil
import sys

_FORCE_PLAIN = False


def set_plain(plain: bool) -> None:
    global _FORCE_PLAIN
    _FORCE_PLAIN = plain


def _color_on() -> bool:
    if _FORCE_PLAIN or os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty()


class C:
    @staticmethod
    def _w(code: str, s: str) -> str:
        return f"\033[{code}m{s}\033[0m" if _color_on() else s

    dim = staticmethod(lambda s: C._w("2", s))
    bold = staticmethod(lambda s: C._w("1", s))
    cyan = staticmethod(lambda s: C._w("36", s))
    amber = staticmethod(lambda s: C._w("33", s))
    green = staticmethod(lambda s: C._w("32", s))
    red = staticmethod(lambda s: C._w("31", s))
    grey = staticmethod(lambda s: C._w("90", s))


def width() -> int:
    return min(shutil.get_terminal_size((84, 24)).columns, 92)


def rule(title: str = "", ch: str = "─") -> str:
    w = width()
    if not title:
        return C.grey(ch * w)
    label = f" {title} "
    left = 2
    right = max(0, w - left - len(label))
    return C.grey(ch * left) + C.bold(label) + C.grey(ch * right)


TRUST_STYLE = {
    "trusted": lambda: C.cyan("trusted"),
    "untrusted": lambda: C.amber("untrusted · quote as data"),
    "stale until checked": lambda: C.dim("from earlier work · stale until checked"),
}


def block_panel(label: str, trust: str, text: str, tokens: int) -> str:
    tag = TRUST_STYLE.get(trust, lambda: C.dim(trust))()
    head = f"{C.bold(label)}   {tag}   {C.grey(f'~{tokens} tok')}"
    body = "\n".join("    " + line for line in text.splitlines())
    return f"{C.grey('┌─')} {head}\n{body}\n{C.grey('└' + '─' * (width() - 1))}"


def budget_table(rows: list[tuple[str, str, int]], total: int) -> str:
    """rows: (label, trust, tokens). Rendered with a proportional bar."""
    name_w = max((len(r[0]) for r in rows), default=20)
    bar_w = 22
    peak = max((t for _, _, t in rows), default=1) or 1
    out = [C.bold("context budget") + C.grey("   (estimate, ~4 chars per token)"), ""]
    for label, trust, n in rows:
        fill = max(1, round(bar_w * n / peak)) if n else 0
        bar = "█" * fill + C.grey("·" * (bar_w - fill))
        bar = C.amber(bar) if trust == "untrusted" else C.cyan(bar) if trust == "trusted" else C.dim(bar)
        out.append(f"  {label:<{name_w}}  {bar}  {n:>4} tok")
    out.append("  " + C.grey("─" * (name_w + bar_w + 12)))
    out.append(f"  {C.bold('total'):<{name_w + 9}}  {C.bold(f'{total:>4} tok')}")
    return "\n".join(out)


def provenance_box(provenance_line: str, fields: dict[str, str]) -> str:
    lines = [C.bold("this run")]
    for k, v in fields.items():
        lines.append(f"  {C.grey(k + ':'):<16} {v}")
    lines.append("")
    lines.append(C.grey("copy this line into your write-up:"))
    lines.append(f"  {provenance_line}")
    return "\n".join(lines)


def ok(msg: str) -> str:
    return f"{C.green('✔')} {msg}"


def err(msg: str) -> str:
    return f"{C.red('✘')} {msg}"


def hint(msg: str) -> str:
    return C.dim(f"  hint: {msg}")
