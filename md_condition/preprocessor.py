from __future__ import unicode_literals, absolute_import
import re

from markdown.preprocessors import Preprocessor


class ConditionPreprocessor(Preprocessor):

    RE_START = re.compile(r'<!--- #if .* -->')
    RE_END = re.compile(r'<!--- #endif -->')

    def __init__(self, md, extension):
        super(ConditionPreprocessor, self).__init__(md)
        symbol = extension.getConfig('symbol')
        self.re_symbol_start = re.compile(r'<!--- #if .*' + symbol + r'.* -->')

    def run(self, lines):
        new_lines = []
        
        matching = False
        symbol_matching = False
        for line in lines:
            start_head = False
            if not matching:
                match_start = self.RE_START.match(line)
                if match_start:
                    start_head = True
                    matching = True
                    symbol_match_start = self.re_symbol_start.match(line)
                    if symbol_match_start:
                        symbol_matching = True
            else:
                match_end = self.RE_END.match(line)
                if match_end:
                    matching = False
                    symbol_matching = False
                    continue
            if not matching or symbol_matching and not start_head:
                new_lines.append(line)
        return new_lines