# Changelog

All notable changes to this project will be documented in this file.

## [0.1.2] - 2025-09-10
- Build: Add smoke validators (CLI, API) and Makefile targets
- CI: Matrix for 3.10/3.11/3.12; format, lint, test, smoke
- Docs: README usage and expected outputs for smoke/api
- Docs: CONTRIBUTING updates (workflow, pre-commit, API/LLM notes)
- Dev: Add release workflow and helper targets; pre-commit config
- Build: Split mypy into `make type`; keep `make lint` fast
- Chore: Bump version to 0.1.2

## [0.1.1] - 2025-09-10
- Docs: Update README with OpenAI Agents SDK details
- CI: Add GitHub Actions workflow
- Build: Move Dockerfile to Python 3.11

## [0.1.0] - 2025-09-09
- Init: Project scaffold with core functionality (ingest, stability, reports)
- Feat: LLM (OpenAI) explanations and Datasette export/serve
- Docs: Add WARP.md and quickstart notes
