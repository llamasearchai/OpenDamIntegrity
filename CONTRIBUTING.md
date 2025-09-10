# Contributing to OpenDamIntegry

Thanks for your interest in contributing!

Ways to help
- Report bugs and suggest features via issues
- Improve documentation and examples
- Contribute code via pull requests

Workflow
- Fork the repo and create a feature branch
- Ensure tests pass: `make test`
 - Run quality checks: `make lint` (optional types: `make type`)
- Run smoke validations: `make smoke` and `make smoke-api`
- Open a pull request with a clear description

Style
- Python 3.10+
- Black formatting, Ruff linting
- Prefer small, focused PRs with tests

Local tips
- Use `make format` to auto-format and apply quick lint fixes.
- API checks without binding a port: `make smoke-api` (uses FastAPI in-process TestClient).
- Live API run: `make api-run` (requires `uvicorn`).
- Optional LLM: install `[llm]` extras and set `OPENAI_API_KEY` to exercise live agent responses; otherwise deterministic fallback is used.

Security
- Please do not include sensitive information in issues or PRs. See SECURITY.md for reporting vulnerabilities.
