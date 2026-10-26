# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

`python` on this machine is the Windows Store stub, not a real interpreter. Run everything through `uv`:

- Tests: `uv run --no-project --with markdown --with pytest pytest -v test.py` (tests live in the root `test.py`, not a `tests/` dir)
- Single test: append `-k test_single_else`
- Lint (the CI gate that fails builds): `uv run --no-project --with flake8 flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics`
- CI also runs flake8 with `--max-line-length=127 --max-complexity=10` as warnings only

## Code

- Target modern Python 3. Py2-isms (`from __future__`, `super(Cls, self)`) may be modernized; CI's pinned Python 3.7 is outdated.
- The whole extension is a single `Preprocessor` in `md_condition/preprocessor.py`, registered at priority 50. `makeExtension` in `__init__.py` is what lets `md_condition` work as a string name in MkDocs `markdown_extensions`.
- Known behaviors to keep in mind (don't change them silently, since they're user-visible):
  - The symbol is interpolated into a regex unescaped and matched as a substring (`.*DEBUG.*`), so `DEBUG` also matches `#if DEBUG_X`.
  - Nested `#if` blocks are not supported. `validate` only checks that the counts of `#if` and `#endif` are equal.
  - Unbalanced blocks raise `AssertionError` from an `assert` statement (stripped under `python -O`). The tests rely on `AssertionError`.
- `test.py`'s `assertExpectedMarkdown` uses `e.message` (Python 2 only), so a failing comparison raises `AttributeError` and hides the diff. Read the raw assertion if a test fails that way.

## Release

1. Bump `version` in `setup.py` and commit.
2. Create a GitHub release with tag `v<version>`. `.github/workflows/pythonpublish.yml` builds and uploads to PyPI (secrets `PYPI_USERNAME`/`PYPI_PASSWORD`).
