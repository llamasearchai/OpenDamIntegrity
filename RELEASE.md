# Release Process

This project uses tag-driven releases via GitHub Actions.

Steps:
1. Ensure the version is bumped in `pyproject.toml` and `src/open_dam_integry/__init__.py`.
2. Update `CHANGELOG.md` with the new version and notes.
3. Validate locally:
   - `make format && make lint`
   - `make test`
   - `make smoke && make smoke-api`
4. Build locally (optional): `python -m build` and inspect `dist/`.
5. Tag and push:
   - `git tag vX.Y.Z`
   - `git push origin vX.Y.Z`
6. GitHub Actions `Release` workflow builds sdist/wheel and attaches them to the GitHub Release.

Notes:
- If you need to re-run a failed release, delete the tag and re-create it after fixes.
- PyPI publishing is not configured; artifacts are attached to the GitHub Release only.

