# Overview

OpenDamIntegry is an advanced Python system for tailings dam integrity monitoring, analysis, and prediction. It integrates multi-sensor ingest, signal processing, stability analysis, optional FEA adapters, machine learning, alerting, reporting, and an LLM assistant, exposed via a CLI and FastAPI service.

Key components
- Ingest: CSV readers for inclinometers, piezometers, settlement plates, InSAR; weather API client
- Processing: detrending, filtering, feature extraction
- Stability: infinite-slope factor of safety and risk banding
- FEA: adapters for FEniCS/DOLFINx and PyNastran with a simplified elastic fallback
- ML: scikit-learn models with optional XGBoost extras
- Alerts: SMTP email and Twilio SMS
- Reports: Jinja2 HTML templates for compliance-ready reports
- LLM: OpenAI Agents/Assistants integration with safe fallbacks
- API/CLI: FastAPI endpoints and Typer CLI for operations

Roadmap
- Scenario modeling: transient analyses and what-if configurations
- Data sources: streaming ingest, sensor calibration workflows
- Visualization: richer 3D views with interactive overlays
- Benchmarks: representative datasets and performance tracking

