# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

OpenDamIntegry is a Python 3.10+ project with a src/ layout and a Typer-based CLI (odintegry). Tooling uses uv + tox-uv, pytest, ruff, black, mypy, and Hatch (hatchling) for builds.

Common commands
- Setup (uv)
  - uv venv
  - uv pip install -e .[dev]    # add extras as needed: [fea,viz,alerts,reports,ml]
  - Alternative (pip): python -m venv .venv && source .venv/bin/activate && pip install -e .[dev]

- Tests
  - pytest -q
  - tox -q                         # uses tox-uv; env: py310
  - Run a single test:
    - pytest -q tests/test_stability.py::test_infinite_slope_fs_basic
    - or via tox: tox -q -- -k "test_cli_version"

- Lint, format, type-check
  - ruff check .                   # lint
  - ruff check --fix .             # autofix
  - black .                        # format
  - black --check .                # verify formatting
  - mypy src                       # type-check

- Build
  - hatch build

- CLI examples
  - odintegry version
  - odintegry stability --c-kpa 8 --phi-deg 30 --beta-deg 18 --height-m 15 --gamma-k-n-m3 18.5 --ru 0.15
  - odintegry visualize --output outputs/dam_surface.png
  - odintegry weather --latitude 40.0 --longitude -105.0 --start-days-ago 7
  - odintegry fea --backend simplified --height-m 20 --width-m 60 --surcharge-kpa 10
  - odintegry alert_test WATCH "Test alert" --email-to someone@example.com   # requires SMTP/Twilio env vars
  - odintegry report   # writes reports/report_YYYYMMDD_HHMMSS.html
  - odintegry explain  # LLM-backed summary if OPENAI_API_KEY is set (fallbacks otherwise)
  - odintegry datasette-export --db-path data/opendamintegry.db  # export samples to SQLite
  - odintegry datasette-serve --db-path data/opendamintegry.db --port 8001  # serve via Datasette

Architecture overview (big picture)
- CLI (Typer) entrypoint: odintegry (src/open_dam_integry/cli.py)
  - Commands: version, ingest (CSV stats), stability (FS + risk), visualize (PNG), fea (FEA or fallback), weather (Open-Meteo), report (HTML), alert_test (email/SMS).
  - __version__ comes from src/open_dam_integry/__init__.py and is managed by Hatch [tool.hatch.version].

- Configuration (src/open_dam_integry/config.py)
  - AppConfig (Pydantic) aggregates: ProjectConfig, Thresholds, AlertsConfig, WeatherConfig.
  - Loads config/opendamintegry.toml by default (tomllib). If absent, uses defaults.
  - Alerts are controlled by config flags (email_enabled/sms_enabled) and environment variables (SMTP_*, TWILIO_*).

- Ingestion
  - sensors.py: read_inclinometers/read_piezometers/read_settlement parse timestamps to UTC and return DataFrames.
  - insar.py: read_insar_csv for non-raster InSAR CSV: timestamp, lat, lon, los_displacement_mm.
  - weather.py: fetch_precipitation_series from Open-Meteo archive API; DataFrame with UTC hourly precipitation.

- Signal processing
  - filters.py: butter_lowpass_filter (scipy.signal) and wavelet_denoise (PyWavelets if available; Savitzky-Golay fallback).
  - trends.py: linear_trend (slope, p-value via scipy.stats.linregress) and detect_threshold_crossings.

- Stability (src/open_dam_integry/stability/stability.py)
  - Infinite slope factor-of-safety computation; maps FS to risk level using configured thresholds.

- FEA adapters (src/open_dam_integry/fea/)
  - fenics_connector.py and pynastran_connector.py detect optional backends (DOLFINx, PyNastran). If unavailable, both fall back to simplified.pseudo_fea_slope_response.
  - simplified.py provides a closed-form elastic approximation for quick, dependency-light runs.

- Machine learning (src/open_dam_integry/ml/model.py)
  - Feature builder across sensor series; classifier is MLP by default or XGBoost if installed via extras. Models saved to models/risk_model.pkl; predict_risk loads and predicts class.

- Visualization (src/open_dam_integry/visualization/viz3d.py)
  - Renders a 3D dam surface using VTK if available, otherwise matplotlib fallback, writing a PNG to disk.

- Reporting
  - Template at src/open_dam_integry/templates/report.html (Jinja2 HTML).
  - CLI report command expects open_dam_integry.reports.generate.generate_report(context, output_dir) but that module is not present; see Notes below.

- Tests (pytest)
  - tests/test_cli.py (version), tests/test_signal.py (filter), tests/test_stability.py (FS sanity).

Optional extras (pyproject.toml)
- fea: pynastran, meshio
- viz: vtk, mayavi
- alerts: twilio
- ml: xgboost
- reports: weasyprint (optional for PDF; HTML generation relies on Jinja2 which is a core dependency)
- llm: openai (for LLM-backed explanations)
- datasette: datasette (for data exploration via SQLite and Datasette)
- Install example: uv pip install -e .[dev,fea,viz,alerts,ml,reports,llm,datasette]

Configuration and data
- Default config: config/opendamintegry.toml
- Sample CSVs: data/samples/{inclinometers.csv, piezometers.csv, settlement_plates.csv, insar.csv}
- Alerts environment variables
  - SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM
  - TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM

Notes and gotchas
- Report generation: odintegry report renders templates/report.html with Jinja2 and writes a timestamped HTML report to the chosen output directory (default: reports/).
- LLM usage: set OPENAI_API_KEY in your environment and optionally OAI_MODEL (default: gpt-4o-mini). The code falls back to deterministic explanations if not configured.
- Datasette: install via extras and use datasette-export and datasette-serve to explore data locally.
- tox is configured with installer = uv and env_list = py310; it runs pytest -q.
- Formatting/linting settings: line length 100 (black/ruff); ruff targets py310 and selects E,F,I,B,UP,C90; mypy ignores missing imports.

