from __future__ import unicode_literals, absolute_import
import re

from markdown.preprocessors import Preprocessor


class ConditionPreprocessor(Preprocessor):

    RE_START = re.compile(r'<!--- #if .* -->')
    RE_END = re.compile(r'<!--- #endif -->')

    def run(self, lines):
        new_lines = []
        symbol = self.extension.getConfig('condition')
        re_symbol_start = re.compile(r'<!--- #if .*' + symbol + r'.* -->')
        matching = False
        symbol_matching = False
        for line in lines:
            if not matching:
                match_start = RE_START.match(line)
                if match_start:
                    matching = True
                    symbol_match_start = re_symbol_start.match(line)
                    if match_symbol_start:
                        symbol_matching = True
            else:
                match_end = RE_END.match(line)
                if match_end and match_start.group() == match_end.group():
                    matching = False
                    symbol_matching = False
                    continue
            if not matching or symbol_matching:
                new_lines.append(line)
        return new_lines