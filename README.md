# OpenDamIntegry

[![CI](https://github.com/llamasearchai/OpenDamIntegrity/actions/workflows/ci.yml/badge.svg)](https://github.com/llamasearchai/OpenDamIntegrity/actions/workflows/ci.yml)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)

## About
Advanced Dam Monitoring System with OpenAI Agents SDK integration that combines geotechnical monitoring, structural analysis, and predictive modeling to ensure the physical integrity of tailings dams via continuous monitoring and stability assessment. Repository: https://github.com/llamasearchai/OpenDamIntegrity

Features
- Multi-sensor ingestion: inclinometers, piezometers, settlement plates, and InSAR (CSV) data
- Signal processing: Butterworth filtering, wavelet denoising (with PyWavelets fallback to Savitzky-Golay)
- Slope stability: real-time factor-of-safety using an infinite slope method and configurable thresholds
- FEA integration: adapters for FEniCS/DOLFINx and PyNastran with a simplified elastic fallback
- Weather API integration: Open-Meteo archive API for precipitation correlation
- Machine learning: MLP (scikit-learn) with optional XGBoost, feature extraction from sensor trends
- Alerts: email (SMTP) and SMS (Twilio) with env-based configuration
- Reporting: Jinja2-based HTML reports for compliance and communication
- Visualization: 3D dam surface rendering via VTK, with matplotlib fallback
- LLM integration: OpenAI Agents/Assistants SDK with safe fallbacks to chat and deterministic text
- API + CLI: FastAPI service with /health, /stability, /agent/respond, and a Typer CLI
- Tooling: uv + Hatch build backend, tox (tox-uv) for tests, pytest, black, ruff, mypy

Project layout
- src/open_dam_integry/: package source
- data/samples/: example CSV data for quick start
- config/opendamintegry.toml: default configuration
- tests/: basic unit tests (pytest)

Quick start (with uv)
1) Create a virtual environment and install in editable mode with dev extras:
   - uv venv
   - uv pip install -e .[dev]
2) Run the CLI:
   - odintegry version
   - odintegry stability --c-kpa 8 --phi-deg 30 --beta-deg 18 --height-m 15 --gamma-k-n-m3 18.5 --ru 0.15
   - odintegry visualize --output outputs/dam_surface.png
   - odintegry report
   - odintegry agent "Summarize current dam stability considerations"
   - odintegry api --host 0.0.0.0 --port 8000

Environment configuration
- Copy `.env.example` to `.env` and adjust values as needed. At minimum, set `OPENAI_API_KEY` if you want live LLM responses.

Running tests
- tox -q
  or
- pytest -q

Building the package (Hatch)
- hatch build

Alerts configuration
- Email (SMTP) environment variables:
  - SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM (optional)
- Twilio (SMS) environment variables:
  - TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM

Notes
- Heavy optional stacks (VTK, XGBoost, PyNastran, DOLFINx) are offered via extras in pyproject.toml
- Core functionality is complete and runs without optional stacks; advanced backends will be used automatically if installed.

## OpenAI Agents Integration

OpenDamIntegry integrates the OpenAI Agents (Assistants v2) SDK with safe fallbacks.

- Install with LLM extras (and optionally dev):
  - uv pip install -e '.[llm]'
- Configure environment variables:
  - `OPENAI_API_KEY`: required to enable OpenAI-backed responses
  - Optional tuning:
    - `OAI_MODEL` (default `gpt-4o-mini`)
    - `OAI_ASSISTANT_ID` (reuse an existing Assistant; otherwise created on-the-fly)
    - `OAI_ASSISTANT_INSTRUCTIONS` (override default domain instructions)
    - `OAI_REQUEST_TIMEOUT_S` (soft timeout for Assistants polling; default 15.0)
- CLI usage:
  - `odintegry agent "How do FS thresholds relate to risk?"`
- Diagnostic status (no network calls):
  - `odintegry agent-status` prints whether the OpenAI client is initialized, the configured model, and the current timeout.
- API usage:
  - POST `/agent/respond` with JSON: `{ "prompt": "..." }`
  - Example:
    - `curl -s -X POST http://127.0.0.1:8000/agent/respond -H 'Content-Type: application/json' -d '{"prompt":"Summarize current dam stability considerations"}'`
- Behavior and fallbacks:
  - Uses Assistants v2 first; falls back to Chat Completions; if OpenAI is not configured, returns a deterministic, helpful response.
  - Timeouts are bounded via `OAI_REQUEST_TIMEOUT_S` to keep requests responsive.
  - No training data is stored; responses are generated per request only.

## FastAPI service

- Run locally:
  - odintegry api --host 0.0.0.0 --port 8000
- Endpoints:
  - GET `/health`
  - POST `/stability`
  - POST `/agent/respond`

Security
- Optional API key gate: set `ODI_API_KEY` to require the header `X-API-Key: <value>` for all endpoints.
  - Example: `ODI_API_KEY=secret uvicorn open_dam_integry.api:app`
  - Curl: `curl -H 'X-API-Key: secret' http://127.0.0.1:8000/health`
- Always place the API behind TLS (reverse proxy or gateway) when exposed publicly.

Quality and safety
- Deterministic fallback responses when LLM unavailable ensure predictable behavior.
- Bounded timeouts on LLM calls avoid long-running requests and improve reliability.
- Optional API key enforcement helps secure endpoints in production.
- No PII is logged. Control verbosity via `LOG_LEVEL`.

## Docker

- Build:
  - docker build -t opendamintegry:latest .
- Run API:
  - docker run --rm -p 8000:8000 -e OPENAI_API_KEY=... opendamintegry:latest


## Suggested topics (GitHub)
- geotechnical, stability, dam, InSAR, piezometer, inclinometer, FEA, VTK, pydantic, typer, datasette, openai, machine-learning
