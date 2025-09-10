# OpenDamIntegry

## About
Advanced Python system that combines geotechnical monitoring, structural analysis, and predictive modeling to ensure the physical integrity of tailings dams via continuous monitoring and stability assessment.

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

## Suggested topics (GitHub)
- geotechnical, stability, dam, InSAR, piezometer, inclinometer, FEA, VTK, pydantic, typer, datasette, openai, machine-learning

