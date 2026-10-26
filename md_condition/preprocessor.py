from __future__ import annotations

import re
from typing import TYPE_CHECKING

from markdown import Markdown
from markdown.preprocessors import Preprocessor

if TYPE_CHECKING:
    from md_condition.extension import ConditionExtension


class ConditionPreprocessor(Preprocessor):
    RE_START = re.compile(r"<!--- #if .* -->")
    RE_END = re.compile(r"<!--- #endif -->")
    RE_ELSE = re.compile(r"<!--- #else -->")

    def __init__(self, md: Markdown, extension: ConditionExtension) -> None:
        super().__init__(md)
        symbol = extension.getConfig("symbol")
        self.re_symbol_start = re.compile(r"<!--- #if .*" + symbol + r".* -->")

    def validate(self, lines: list[str]) -> None:
        target_lines_start = []
        target_lines_end = []
        for index, line in enumerate(lines):
            if self.RE_START.match(line):
                target_lines_start.append(f"{index}. {line}")
            if self.RE_END.match(line):
                target_lines_end.append(f"{index}. {line}")

        assert len(target_lines_start) == len(target_lines_end), (
            f"Unbalanced if / endif blocks\n{target_lines_start}\n{target_lines_end}"
        )

    def run(self, lines: list[str]) -> list[str]:
        self.validate(lines)
        new_lines = []

        matching = False
        symbol_matching = False
        for line in lines:
            start_head = False
            if not matching:
                if self.RE_START.match(line):
                    start_head = True
                    matching = True
                    symbol_match_start = self.re_symbol_start.match(line)
                    if symbol_match_start:
                        symbol_matching = True
            else:
                if self.RE_ELSE.match(line):
                    symbol_matching = not symbol_matching
                    continue
                if self.RE_END.match(line):
                    matching = False
                    symbol_matching = False
                    continue
            if not matching or symbol_matching and not start_head:
                new_lines.append(line)

        return new_lines
