import textwrap

import markdown
import pytest

from md_condition import ConditionExtension, ConditionSyntaxError


@pytest.fixture
def md() -> markdown.Markdown:
    return markdown.Markdown(extensions=[ConditionExtension(symbol="DEBUG")])


def convert(md: markdown.Markdown, source: str) -> str:
    return md.convert(textwrap.dedent(source))


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        pytest.param(
            """\
            # 1
            <!--- #if DEBUG -->
            DEBUG
            <!--- #endif -->
            # 2
            <!--- #if RELEASE -->
            RELEASE
            <!--- #endif -->
            # 3""",
            "<h1>1</h1>\n<p>DEBUG</p>\n<h1>2</h1>\n<h1>3</h1>",
            id="single",
        ),
        pytest.param(
            """\
            # 1
            <!--- #if DEBUG -->
            DEBUG
            <!--- #else -->
            not DEBUG
            <!--- #endif -->
            # 2
            <!--- #if RELEASE -->
            RELEASE
            <!--- #else -->
            not RELEASE
            <!--- #endif -->
            # 3""",
            "<h1>1</h1>\n<p>DEBUG</p>\n<h1>2</h1>\n<p>not RELEASE</p>\n<h1>3</h1>",
            id="single_else",
        ),
        pytest.param(
            """\
            # 1
            <!--- #if DEBUG RELEASE -->
            DEBUG RELEASE
            <!--- #endif -->
            # 2
            <!--- #if RELEASE -->
            RELEASE
            <!--- #endif -->
            # 3""",
            "<h1>1</h1>\n<p>DEBUG RELEASE</p>\n<h1>2</h1>\n<h1>3</h1>",
            id="double",
        ),
        pytest.param(
            """\
            # 1
            <!--- #if DEBUG RELEASE -->
            DEBUG RELEASE
            <!--- #else -->
            else DEBUG RELEASE
            <!--- #endif -->
            # 2
            <!--- #if RELEASE -->
            RELEASE
            <!--- #else -->
            not RELEASE
            <!--- #endif -->
            # 3""",
            "<h1>1</h1>\n<p>DEBUG RELEASE</p>\n<h1>2</h1>\n<p>not RELEASE</p>\n<h1>3</h1>",
            id="double_else",
        ),
    ],
)
def test_condition(md: markdown.Markdown, source: str, expected: str) -> None:
    assert convert(md, source) == expected


@pytest.mark.parametrize(
    ("symbol", "condition", "kept"),
    [
        pytest.param("DEBUG", "DEBUG_X", False, id="no_prefix_match"),
        pytest.param("DEBUG", "MY_DEBUG", False, id="no_suffix_match"),
        pytest.param("DEBUG_X", "DEBUG_X", True, id="exact"),
        pytest.param("C++", "C++", True, id="regex_metachars"),
        pytest.param("C++", "CXX", False, id="regex_metachars_no_match"),
        pytest.param("", "DEBUG", False, id="empty_symbol_matches_nothing"),
        pytest.param("", "A | B", False, id="empty_symbol_ignores_separators"),
        pytest.param("", "| A |", False, id="empty_symbol_edge_separators"),
        # Issue #7: `|`-separated names, with or without spaces
        pytest.param("THAT", "THIS | THAT | OTHER", True, id="pipe_spaced"),
        pytest.param("THAT", "THIS|THAT|OTHER", True, id="pipe_compact"),
        pytest.param("THAT", "THIS|THATX|OTHER", False, id="pipe_whole_name"),
        pytest.param("OTHER", "THIS THAT|OTHER", True, id="mixed_separators"),
    ],
)
def test_symbol_is_matched_as_whole_name(symbol: str, condition: str, kept: bool) -> None:
    md = markdown.Markdown(extensions=[ConditionExtension(symbol=symbol)])
    output = md.convert(f"<!--- #if {condition} -->\nyes\n<!--- #else -->\nno\n<!--- #endif -->")
    assert output == ("<p>yes</p>" if kept else "<p>no</p>")


ISSUE_6_SOURCE = """\
# 1
<!--- #if DEBUG -->
DEBUG
<!--- #else -->
No DEBUG
<!--- #endif -->
# 2
<!--- #if RELEASE -->
RELEASE
<!--- #else -->
No RELEASE
<!--- #endif -->"""


@pytest.mark.parametrize(
    ("symbol", "debug", "release"),
    [
        # Issue #6: multiple defined symbols, each usable as its own condition
        pytest.param("DEBUG RELEASE", True, True, id="space_separated"),
        pytest.param("DEBUG|RELEASE", True, True, id="pipe_separated"),
        pytest.param(["DEBUG", "RELEASE"], True, True, id="list"),
        pytest.param(("DEBUG",), True, False, id="tuple"),
        pytest.param("RELEASE", False, True, id="single"),
        pytest.param([], False, False, id="empty_list"),
        pytest.param(None, False, False, id="none"),
    ],
)
def test_multiple_symbols(symbol, debug: bool, release: bool) -> None:
    md = markdown.Markdown(extensions=[ConditionExtension(symbol=symbol)])
    expected = "<h1>1</h1>\n<p>{}</p>\n<h1>2</h1>\n<p>{}</p>".format(
        "DEBUG" if debug else "No DEBUG", "RELEASE" if release else "No RELEASE"
    )
    assert md.convert(ISSUE_6_SOURCE) == expected


def test_multiple_symbols_any_listed_name_matches() -> None:
    md = markdown.Markdown(extensions=[ConditionExtension(symbol=["DEBUG", "STAGING"])])
    assert md.convert("<!--- #if RELEASE STAGING -->\nyes\n<!--- #endif -->") == "<p>yes</p>"


@pytest.mark.parametrize(
    ("source", "message"),
    [
        pytest.param(
            """\
            <!--- #if DEBUG RELEASE -->
            # 1""",
            "line 1: #if is never closed",
            id="missing_endif",
        ),
        pytest.param(
            """\
            <!--- #if DEBUG RELEASE -->
            # 1
            <!--- #endif -->
            <!--- #endif -->""",
            "line 4: #endif without #if",
            id="extra_endif",
        ),
        pytest.param(
            """\
            # 1
            <!--- #else -->""",
            "line 2: #else without #if",
            id="else_without_if",
        ),
        pytest.param(
            """\
            <!--- #if DEBUG -->
            <!--- #else -->
            <!--- #else -->
            <!--- #endif -->""",
            "line 3: duplicate #else",
            id="duplicate_else",
        ),
        pytest.param(
            """\
            <!--- #if DEBUG -->
            <!--- #if RELEASE -->
            <!--- #endif -->
            <!--- #endif -->""",
            "line 2: nested #if is not supported",
            id="nested",
        ),
    ],
)
def test_malformed_blocks(md: markdown.Markdown, source: str, message: str) -> None:
    with pytest.raises(ConditionSyntaxError, match=message):
        convert(md, source)


def test_error_is_still_an_assertion_error(md: markdown.Markdown) -> None:
    # Backward compatibility with <= 0.1.x, which raised via `assert`
    with pytest.raises(AssertionError):
        convert(md, "<!--- #if DEBUG -->")


def test_make_extension_by_name() -> None:
    md = markdown.Markdown(
        extensions=["md_condition"],
        extension_configs={
            "md_condition": {"symbol": "DEBUG"},
        },
    )
    assert md.convert("<!--- #if DEBUG -->\nyes\n<!--- #endif -->") == "<p>yes</p>"


def test_make_extension_by_name_with_list() -> None:
    # MkDocs passes YAML lists through as Python lists
    md = markdown.Markdown(
        extensions=["md_condition"],
        extension_configs={"md_condition": {"symbol": ["DEBUG", "RELEASE"]}},
    )
    assert md.convert("<!--- #if RELEASE -->\nyes\n<!--- #endif -->") == "<p>yes</p>"
