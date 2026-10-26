import textwrap

import markdown
import pytest

from md_condition import ConditionExtension


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
    "source",
    [
        pytest.param(
            """\
            <!--- #if DEBUG RELEASE -->
            # 1""",
            id="missing_endif",
        ),
        pytest.param(
            """\
            <!--- #if DEBUG RELEASE -->
            # 1
            <!--- #endif -->
            <!--- #endif -->""",
            id="extra_endif",
        ),
    ],
)
def test_unbalanced(md: markdown.Markdown, source: str) -> None:
    with pytest.raises(AssertionError, match="Unbalanced if / endif blocks"):
        convert(md, source)


def test_make_extension_by_name() -> None:
    md = markdown.Markdown(
        extensions=["md_condition"],
        extension_configs={
            "md_condition": {"symbol": "DEBUG"},
        },
    )
    assert md.convert("<!--- #if DEBUG -->\nyes\n<!--- #endif -->") == "<p>yes</p>"
