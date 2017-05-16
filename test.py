import re
import unittest
import textwrap
import markdown
from md_condition.extension import ConditionExtension


class TestCondition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.md = markdown.Markdown(extensions=[ConditionExtension(symbol='DEBUG')])

    def assertExpectedMarkdown(self, md_input, expected_output):
        output = self.md.convert(textwrap.dedent(md_input))
        expected = textwrap.dedent(expected_output)

        try:
            self.assertEqual(output, expected)
        except AssertionError as e:
            raise AssertionError('\n' + re.sub("' != '", '\n!=\n', e.message))

    def test_single(self):
        md_input = """\
            # 1
            <!--- #if DEBUG -->
            DEBUG
            <!--- #endif -->
            # 2
            <!--- #if RELEASE -->
            RELEASE
            <!--- #endif -->
            # 3"""
        expected_result = """\
            <h1>1</h1>
            <p>DEBUG</p>
            <h1>2</h1>
            <h1>3</h1>"""
        self.assertExpectedMarkdown(md_input, expected_result)

    def test_double(self):
        md_input = """\
            # 1
            <!--- #if DEBUG RELEASE -->
            DEBUG RELEASE
            <!--- #endif -->
            # 2
            <!--- #if RELEASE -->
            RELEASE
            <!--- #endif -->
            # 3"""
        expected_result = """\
            <h1>1</h1>
            <p>DEBUG RELEASE</p>
            <h1>2</h1>
            <h1>3</h1>"""
        self.assertExpectedMarkdown(md_input, expected_result)