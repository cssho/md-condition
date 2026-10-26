# md-condition

This is an extension to [Python-Markdown](https://python-markdown.github.io)
which allows conditional compilations to be inserted into the text.

[![PyPI version](https://badge.fury.io/py/md-condition.svg)](https://badge.fury.io/py/md-condition)

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
  `md_condition.ConditionSyntaxError` with the offending line number.

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
