---
name: release
description: "Release a new md-condition version to PyPI — verify master, then create the GitHub release whose tag sets the version and triggers the publish workflow. Usage: /release <version>"
argument-hint: "<version, e.g. 0.2.0>"
disable-model-invocation: true
---

Release version `$ARGUMENTS` (e.g. `0.1.9`, no `v` prefix). If empty, show the latest tag (`git describe --tags --abbrev=0`) and ask which version to release.

The version comes from the git tag via setuptools-scm, so there is no file to bump.

1. Preconditions: on `master`, working tree clean, `git pull` up to date. `git tag` must not already contain `v$ARGUMENTS`. The latest `ci-ok` run on master must be green (`gh run list --branch master --workflow pythonapp.yml --limit 1`). Stop and report if any fail.
2. Verify locally — both must pass:
   - `uv run pytest`
   - `uv run ruff check .` and `uv run ruff format --check .`
3. Summarize commits since the previous tag (`git log <prev-tag>..HEAD --oneline`) as release notes. If the release contains user-visible behavior changes, add a "Breaking changes / migration" section. Show the notes to the user for confirmation before creating the release.
4. `gh release create v$ARGUMENTS --target master --title v$ARGUMENTS --notes-file <notes>`. Publishing the release fires `.github/workflows/pythonpublish.yml` (`release: published`; a draft does not).
5. The publish job runs in the `pypi` environment, which only accepts `v*` tags and **waits for the user's approval**. Report the release URL and the run (`gh run list --workflow pythonpublish.yml --limit 1`), and tell the user to approve it in the Actions UI. Do not approve it yourself.
