"""Directives inside code fences (code review: docs showing md-condition syntax)."""

import textwrap

import markdown
import pytest

from md_condition import ConditionExtension, ConditionSyntaxError


def preprocess(source: str, symbol="DEBUG") -> str:
    md = markdown.Markdown(extensions=[ConditionExtension(symbol=symbol)])
    lines = textwrap.dedent(source).split("\n")
    return "\n".join(md.preprocessors["condition"].run(lines))


@pytest.mark.parametrize(
    "source",
    [
        pytest.param(
            """\
            ```md
            <!--- #else -->
            ```""",
            id="lone_else",
        ),
        pytest.param(
            """\
            ```md
            <!--- #endif -->
            ```""",
            id="lone_endif",
        ),
        pytest.param(
            """\
            ```md
            <!--- #if DEBUG -->
            only the opening line
            ```""",
            id="unclosed_if",
        ),
        pytest.param(
            """\
            ```md
            <!--- #if RELEASE -->
            hidden?
            <!--- #else -->
            shown?
            ```""",
            id="unclosed_if_with_else",
        ),
        pytest.param(
            """\
            ~~~
            <!--- #else -->
            ~~~""",
            id="tilde_fence",
        ),
        pytest.param(
            """\
            ```md
            <!--- #if DEBUG -->
            unterminated fence at end of input""",
            id="unterminated_fence",
        ),
    ],
)
def test_malformed_directives_in_fence_are_kept_verbatim(source: str) -> None:
    assert preprocess(source) == textwrap.dedent(source)


def test_well_formed_block_in_fence_is_applied() -> None:
    # Conditional code samples keep working, as in 0.1.x
    source = """\
        ```python
        <!--- #if DEBUG -->
        log_level = "debug"
        <!--- #else -->
        log_level = "info"
        <!--- #endif -->
        ```"""
    assert preprocess(source) == '```python\nlog_level = "debug"\n```'
    assert preprocess(source, symbol="RELEASE") == '```python\nlog_level = "info"\n```'


def test_malformed_lines_inside_a_fenced_block_are_text() -> None:
    source = """\
        ```
        <!--- #if DEBUG -->
        <!--- #if NESTED -->
        <!--- #else -->
        <!--- #else -->
        <!--- #endif -->
        ```"""
    # nested #if is text; the 2nd #else is a duplicate and therefore text in the else branch
    assert preprocess(source) == "```\n<!--- #if NESTED -->\n```"


def test_fence_markers_must_match_to_close() -> None:
    source = """\
        ````md
        ```
        <!--- #if DEBUG -->
        ```
        still inside the 4-backtick fence
        ````"""
    assert preprocess(source) == textwrap.dedent(source)


def test_outer_block_hides_whole_fence() -> None:
    source = """\
        <!--- #if RELEASE -->
        ```md
        <!--- #else -->
        ```
        <!--- #endif -->
        after"""
    assert preprocess(source) == "after"


def test_fence_does_not_hide_errors_outside_it() -> None:
    with pytest.raises(ConditionSyntaxError, match="line 4: #else without #if"):
        preprocess(
            """\
            ```md
            <!--- #else -->
            ```
            <!--- #else -->"""
        )


def test_end_to_end_with_fenced_code() -> None:
    md = markdown.Markdown(extensions=["fenced_code", ConditionExtension(symbol="DEBUG")])
    html = md.convert("```md\n<!--- #else -->\n```")
    assert "&lt;!--- #else --&gt;" in html


def test_error_message_includes_the_line() -> None:
    # Line numbers can be offset by MkDocs front matter, so the text must be findable
    with pytest.raises(
        ConditionSyntaxError, match=r"line 2: #endif without #if: '<!--- #endif -->'"
    ):
        preprocess("text\n<!--- #endif -->")


@pytest.mark.parametrize(
    ("symbol", "condition"),
    [
        pytest.param(2024, "2024", id="int"),
        pytest.param(1.5, "1.5", id="float"),
        pytest.param(True, "True", id="bool"),
        pytest.param([2024, "DEBUG"], "2024", id="int_in_list"),
    ],
)
def test_yaml_scalar_symbols(symbol, condition: str) -> None:
    # YAML turns `symbol: 2024` / `symbol: yes` into int / bool
    assert preprocess(f"<!--- #if {condition} -->\nyes\n<!--- #endif -->", symbol=symbol) == "yes"


def test_false_symbol_is_not_treated_as_empty() -> None:
    assert preprocess("<!--- #if False -->\nyes\n<!--- #endif -->", symbol=False) == "yes"
