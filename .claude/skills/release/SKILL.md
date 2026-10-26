---
name: release
description: "Release a new md-condition version to PyPI — verify master, then create the GitHub release whose tag sets the version and triggers the publish workflow. Usage: /release <version>"
argument-hint: "<version, e.g. 0.2.0>"
disable-model-invocation: true
---

Requested version: `$ARGUMENTS`. If empty, show the latest tag (`git describe --tags --abbrev=0`) and ask which version to release.

The version comes from the git tag via setuptools-scm, so there is no file to bump.

0. Normalize the version before using it anywhere: strip whitespace and **one leading `v`/`V`** (`v0.2.0` → `0.2.0`). Call the result VERSION and the tag `vVERSION` — never prefix `v` to an unnormalized argument. VERSION must be a final PEP 440 release, `X.Y.Z` (`^\d+\.\d+\.\d+$`), and greater than the latest tag; if not, stop and ask. Use VERSION / `vVERSION` in place of `$ARGUMENTS` in every step below.
1. Preconditions: on `master`, working tree clean, `git pull` up to date. `git tag` must not already contain `v$ARGUMENTS`. The latest `ci-ok` run on master must be green (`gh run list --branch master --workflow pythonapp.yml --limit 1`). Stop and report if any fail.
2. Verify locally — both must pass:
   - `uv run pytest`
   - `uv run ruff check .` and `uv run ruff format --check .`
3. Summarize commits since the previous tag (`git log <prev-tag>..HEAD --oneline`) as release notes. If the release contains user-visible behavior changes, add a "Breaking changes / migration" section. Show the notes to the user for confirmation before creating the release.
4. `gh release create v$ARGUMENTS --target master --title v$ARGUMENTS --notes-file <notes>`. Publishing the release fires `.github/workflows/pythonpublish.yml` (`release: published`; a draft does not).
5. The workflow's `build` job re-runs lint + tests and checks the built version equals the tag; then the `publish` job runs in the `pypi` environment, which only accepts `v*` tags and **waits for the user's approval**. Report the release URL and the run (`gh run list --workflow pythonpublish.yml --limit 1`), and tell the user to approve it in the Actions UI. Do not approve it yourself.
