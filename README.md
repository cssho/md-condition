# md-condition

This is an extension to [Python-Markdown](https://pythonhosted.org/Markdown/)
which allows conditional compilations to be inserted into the text.

## Install
This module can now be installed using `pip`.

```
$ pip install markdown-blockdiag
```

## Usage

The syntax for use within your Markdown files is

```md
<!--- #if DEBUG --->
# md-condition
<!--- #endif --->
```

## MkDocs Integration

In your mkdocs.yml add this to markdown_extensions.

```yaml
markdown_extensions:
  - md_condition:
      condition: DEBUG
```