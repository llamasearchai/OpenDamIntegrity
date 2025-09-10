# Development

Local setup
- make venv
- make dev

Quality checks
- Lint: `make lint` (ruff, black)
- Type check (optional): `make type` (mypy)
- Tests: `make test` (pytest)

Release
- Bump version in `pyproject.toml` and `src/open_dam_integry/__init__.py`
- Build: `hatch build`
- Publish (PyPI): `python -m pip install twine && twine upload dist/*` (requires credentials)
- Docker: `docker build -t opendamintegry:<version> .`

Contributing
- See CONTRIBUTING.md for guidelines.

