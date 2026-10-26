---
name: release
description: Release a new md-condition version to PyPI — bump setup.py, verify, push, and create the GitHub release that triggers the publish workflow. Usage: /release <version>
disable-model-invocation: true
---

Release version `$ARGUMENTS` (e.g. `0.1.9`, no `v` prefix). If empty, read the current `version` in `setup.py` and ask which version to release.

1. Preconditions: on `master`, working tree clean, `git pull` up to date. `git tag` must not already contain `v$ARGUMENTS`. Stop and report if any fail.
2. Set `version='$ARGUMENTS'` in `setup.py`.
3. Verify — both must pass before continuing:
   - `uv run --no-project --with markdown --with pytest pytest -v test.py`
   - `uv run --no-project --with flake8 flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics`
4. Commit `setup.py` with message `Bump version to $ARGUMENTS`, then `git push origin master`.
5. Summarize commits since the previous tag (`git log <prev-tag>..HEAD --oneline`) as release notes, and show them to the user for confirmation before creating the release.
6. `gh release create v$ARGUMENTS --target master --title v$ARGUMENTS --notes "<notes>"`. This fires `.github/workflows/pythonpublish.yml`, which uploads to PyPI.
7. Report the release URL and check the publish run with `gh run list --workflow pythonpublish.yml --limit 1`.
