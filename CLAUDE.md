# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

`python` on this machine is the Windows Store stub, not a real interpreter. Run everything through `uv` (dev deps live in the `dev` dependency group of `pyproject.toml`):

- Tests: `uv run pytest` (single test: `-k single_else`)
- Lowest supported Markdown: `uv run --isolated --python 3.10 --with "markdown==3.2.*" pytest`
- Lint/format (CI fails on either): `uv run ruff check .` and `uv run ruff format --check .`
- Build: `uv build`. The version comes from the latest git tag via setuptools-scm; there is no version field to edit.

## Code

- Python >=3.10, Markdown >=3.2. Markdown 3.0/3.1 can't import on modern Python (they need `pkg_resources`).
- master is protected by a ruleset: changes go through PRs, and the `ci-ok` check (aggregates lint + the test matrix) must pass.
- The whole extension is a single `Preprocessor` in `md_condition/preprocessor.py`, registered at priority 50. `makeExtension` in `__init__.py` is what lets `md_condition` work as a string name in MkDocs `markdown_extensions`.
- Known behaviors to keep in mind (don't change them silently, since they're user-visible):
  - The symbol is interpolated into a regex unescaped and matched as a substring (`.*DEBUG.*`), so `DEBUG` also matches `#if DEBUG_X`.
  - Nested `#if` blocks are not supported. `validate` only checks that the counts of `#if` and `#endif` are equal.
  - Unbalanced blocks raise `AssertionError` from an `assert` statement (stripped under `python -O`). The tests rely on `AssertionError`.

## Release

Create a GitHub release with tag `v<version>` (use `/release`). `.github/workflows/pythonpublish.yml` builds with the tag as the version and uploads to PyPI via Trusted Publishing (OIDC, GitHub environment `pypi`; no API token secrets).
