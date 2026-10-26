from __future__ import annotations

import re
from typing import TYPE_CHECKING

from markdown import Markdown
from markdown.preprocessors import Preprocessor

if TYPE_CHECKING:
    from md_condition.extension import ConditionExtension


class ConditionSyntaxError(ValueError, AssertionError):
    """Malformed ``#if`` / ``#else`` / ``#endif`` blocks.

    Also an ``AssertionError`` for compatibility with <= 0.1.x, which used ``assert``.
    """


class ConditionPreprocessor(Preprocessor):
    RE_START = re.compile(r"<!--- #if (.*?) -->")
    RE_END = re.compile(r"<!--- #endif -->")
    RE_ELSE = re.compile(r"<!--- #else -->")

    def __init__(self, md: Markdown, extension: ConditionExtension) -> None:
        super().__init__(md)
        self.symbol = extension.getConfig("symbol")

    def run(self, lines: list[str]) -> list[str]:
        new_lines = []

        block_start = None  # 1-based line of the open #if; None outside a block
        seen_else = False
        keep = True
        for number, line in enumerate(lines, start=1):
            start = self.RE_START.match(line)
            if start:
                if block_start is not None:
                    raise ConditionSyntaxError(
                        f"line {number}: nested #if is not supported "
                        f"(block opened at line {block_start})"
                    )
                block_start = number
                seen_else = False
                # `#if A B` is true when the configured symbol is one of the listed names
                keep = self.symbol in start.group(1).split()
                continue
            if self.RE_ELSE.match(line):
                if block_start is None:
                    raise ConditionSyntaxError(f"line {number}: #else without #if")
                if seen_else:
                    raise ConditionSyntaxError(
                        f"line {number}: duplicate #else in block opened at line {block_start}"
                    )
                seen_else = True
                keep = not keep
                continue
            if self.RE_END.match(line):
                if block_start is None:
                    raise ConditionSyntaxError(f"line {number}: #endif without #if")
                block_start = None
                keep = True
                continue
            if keep:
                new_lines.append(line)

        if block_start is not None:
            raise ConditionSyntaxError(f"line {block_start}: #if is never closed with #endif")

        return new_lines
