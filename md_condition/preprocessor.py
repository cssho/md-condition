from __future__ import annotations

import re
from collections.abc import Iterable
from typing import TYPE_CHECKING

from markdown import Markdown
from markdown.preprocessors import Preprocessor

if TYPE_CHECKING:
    from md_condition.extension import ConditionExtension


class ConditionSyntaxError(ValueError, AssertionError):
    """Malformed ``#if`` / ``#else`` / ``#endif`` blocks.

    Also an ``AssertionError`` for compatibility with <= 0.1.x, which used ``assert``.
    """


class _Block:
    """State of the innermost open ``#if`` block (or none) within one scope."""

    def __init__(self) -> None:
        self.start: int | None = None  # 1-based line number of the open #if
        self.start_line = ""
        self.seen_else = False
        self.keep = True
        # Fence scope only: (raw line, kept) since the #if, flushed on #endif or rolled back
        self.buffer: list[tuple[str, bool]] = []


class ConditionPreprocessor(Preprocessor):
    RE_START = re.compile(r"<!--- #if (.*?) -->")
    RE_END = re.compile(r"<!--- #endif -->")
    RE_ELSE = re.compile(r"<!--- #else -->")
    RE_NAME = re.compile(r"[^\s|]+")  # names are separated by whitespace and/or `|`
    RE_FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})")
    RE_FENCE_CLOSE = re.compile(r"^[ \t]*(`{3,}|~{3,})[ \t]*$")

    def __init__(self, md: Markdown, extension: ConditionExtension) -> None:
        super().__init__(md)
        # `symbol` is a string ("DEBUG", "DEBUG RELEASE", "DEBUG|RELEASE"), a list of them,
        # or a YAML scalar such as 2024 (stringified)
        symbol = extension.getConfig("symbol")
        values: Iterable[object]
        if symbol is None:
            values = []
        elif isinstance(symbol, (list, tuple, set, frozenset)):
            values = symbol
        else:
            values = [symbol]
        self.symbols = {name for value in values for name in self.RE_NAME.findall(str(value))}

    def run(self, lines: list[str]) -> list[str]:
        """Strip excluded lines and directives.

        Outside code fences, malformed blocks raise. Inside a fence, directives form their
        own scope so docs can show md-condition syntax: well-formed blocks are still
        applied (conditional code samples), but malformed directives and an #if left open
        at the end of the fence are kept verbatim as example text.
        """
        new_lines: list[str] = []
        outer = _Block()
        fence: str | None = None  # marker of the open code fence, e.g. "```"
        inner = _Block()

        def emit(line: str) -> None:
            if outer.keep:
                new_lines.append(line)

        for number, line in enumerate(lines, start=1):
            if fence is None:
                opened = self.RE_FENCE.match(line)
                if opened:
                    fence = opened.group(1)
                    inner = _Block()
                    emit(line)
                elif not self._directive(outer, number, line, strict=True):
                    emit(line)
            elif self._closes_fence(line, fence):
                fence = None
                for raw, _ in inner.buffer:  # #if still open: roll back to verbatim text
                    emit(raw)
                inner = _Block()
                emit(line)
            elif inner.start is None:
                if self._directive(inner, number, line, strict=False):
                    inner.buffer = [(line, False)]  # #if opened; buffer until #endif
                else:
                    emit(line)
            else:
                consumed = self._directive(inner, number, line, strict=False)
                if inner.start is None:  # #endif: emit what the block kept
                    for raw, kept in inner.buffer:
                        if kept:
                            emit(raw)
                    inner.buffer = []
                else:
                    inner.buffer.append((line, inner.keep and not consumed))

        if inner.start is not None:  # fence never closed: same rollback as above
            for raw, _ in inner.buffer:
                emit(raw)
        if outer.start is not None:
            raise self._error(outer.start, outer.start_line, "#if is never closed with #endif")

        return new_lines

    def _directive(self, block: _Block, number: int, line: str, *, strict: bool) -> bool:
        """Apply a directive line to ``block``; return True if it was consumed as one.

        Malformed directives raise in strict scope and are left as text otherwise.
        """
        start = self.RE_START.match(line)
        if start:
            if block.start is not None:
                return self._malformed(
                    strict,
                    number,
                    line,
                    f"nested #if is not supported (block opened at line {block.start})",
                )
            block.start = number
            block.start_line = line
            block.seen_else = False
            # `#if A B` / `#if A | B` is true when any configured symbol is listed
            block.keep = not self.symbols.isdisjoint(self.RE_NAME.findall(start.group(1)))
            return True
        if self.RE_ELSE.match(line):
            if block.start is None:
                return self._malformed(strict, number, line, "#else without #if")
            if block.seen_else:
                return self._malformed(
                    strict,
                    number,
                    line,
                    f"duplicate #else in block opened at line {block.start}",
                )
            block.seen_else = True
            block.keep = not block.keep
            return True
        if self.RE_END.match(line):
            if block.start is None:
                return self._malformed(strict, number, line, "#endif without #if")
            block.start = None
            block.keep = True
            return True
        return False

    def _malformed(self, strict: bool, number: int, line: str, message: str) -> bool:
        if strict:
            raise self._error(number, line, message)
        return False

    @staticmethod
    def _error(number: int, line: str, message: str) -> ConditionSyntaxError:
        # Line numbers count from the text handed to Markdown (MkDocs strips front matter
        # first), so include the line itself to make it findable
        return ConditionSyntaxError(f"line {number}: {message}: {line.strip()!r}")

    @classmethod
    def _closes_fence(cls, line: str, fence: str) -> bool:
        # CommonMark: same character, at least as long, nothing else on the line
        closing = cls.RE_FENCE_CLOSE.match(line)
        if closing is None:
            return False
        marker = closing.group(1)
        return marker[0] == fence[0] and len(marker) >= len(fence)
