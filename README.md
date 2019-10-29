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
<!--- #endif --->

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

## MkDocs Integration

In your mkdocs.yml add this to markdown_extensions.

```yaml
markdown_extensions:
  - md_condition:
      symbol: DEBUG
```
