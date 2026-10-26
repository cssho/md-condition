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
- Syntax rules are documented in README "Rules" and are user-visible; keep README, tests, and code in sync when changing them.
- `ConditionSyntaxError` subclasses both `ValueError` and `AssertionError`; the latter keeps callers from <= 0.1.x (which used `assert`) working. Don't drop it without a major version bump.

## Release

Create a GitHub release with tag `v<version>` (use `/release`). `.github/workflows/pythonpublish.yml` builds with the tag as the version and uploads to PyPI via Trusted Publishing (OIDC, GitHub environment `pypi`; no API token secrets).
