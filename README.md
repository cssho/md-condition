# md-condition

This is an extension to [Python-Markdown](https://python-markdown.github.io)
which allows conditional compilations to be inserted into the text.

[![PyPI](https://img.shields.io/pypi/v/md-condition)](https://pypi.org/project/md-condition/)
[![CI](https://github.com/cssho/md-condition/actions/workflows/pythonapp.yml/badge.svg?branch=master)](https://github.com/cssho/md-condition/actions/workflows/pythonapp.yml)
[![Python](https://img.shields.io/python/required-version-toml?tomlFilePath=https://raw.githubusercontent.com/cssho/md-condition/master/pyproject.toml)](https://pypi.org/project/md-condition/)
[![License](https://img.shields.io/pypi/l/md-condition)](LICENSE)
[![Downloads](https://static.pepy.tech/badge/md-condition/month)](https://pepy.tech/project/md-condition)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Install
This module can now be installed using `pip`.

```
$ pip install md-condition
```

## Usage

The syntax for use within your Markdown files is

```md
<!--- #if DEBUG -->
# md-condition DEBUG
<!--- #else -->
not DEBUG
<!--- #endif -->

<!--- #if RELEASE -->
# md-condition RELEASE
<!--- #else -->
not RELEASE
<!--- #endif -->
```

```html
<h1>md-condition DEBUG</h1>
<p>not RELEASE</p>
```

### Rules

- `symbol` defines one or more symbols: `DEBUG`, `DEBUG RELEASE`, `DEBUG|RELEASE`, or a list
  `[DEBUG, RELEASE]`. With no `symbol` configured, every `#if` is false.
- `<!--- #if A B -->` is true when any defined symbol is exactly one of the listed names
  (`DEBUG` does not match `DEBUG_X`). Names are separated by spaces and/or `|`, so
  `#if A | B` and `#if A|B` mean the same.
- `#else` is optional; nested `#if` blocks are not supported.
- Malformed blocks (unclosed `#if`, stray `#else` / `#endif`, duplicate `#else`, nesting) raise
  `md_condition.ConditionSyntaxError` with the offending line number and text.
- Inside fenced code blocks (```` ``` ```` / `~~~`), complete `#if` … `#endif` blocks still apply
  (conditional code samples), but malformed directives are left as text, so docs can show
  md-condition syntax without breaking the build.

## MkDocs Integration

In your mkdocs.yml add this to markdown_extensions.

```yaml
markdown_extensions:
  - md_condition:
      symbol: DEBUG
```

To define several symbols at once:

```yaml
markdown_extensions:
  - md_condition:
      symbol: [DEBUG, RELEASE]
```
