"""Command-line interface for OpenDamIntegry using Typer."""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd
import typer
from rich import print

from . import __version__
from .config import AppConfig
from .ingest.sensors import read_inclinometers, read_piezometers, read_settlement
from .ingest.insar import read_insar_csv
from .ingest.weather import fetch_precipitation_series
from .signal_processing.trends import linear_trend
from .stability.stability import (
    InfiniteSlopeParams,
    factor_of_safety_infinite_slope,
    risk_level_from_fs,
)
from .fea.fenics_connector import run_fea_or_fallback
from .fea.pynastran_connector import run_pynastran_or_fallback
from .visualization.viz3d import render_dam_surface_png
from .alerts.notify import notify
from .llm.agent import explain_stability, explain_report_context
from .datasette.export import export_to_sqlite, serve_datasette

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def version() -> None:
    print(f"OpenDamIntegry v{__version__}")


@app.command()
def ingest(
    inclinometer_csv: Path = typer.Argument(..., exists=True, readable=True),
    piezometer_csv: Path = typer.Argument(..., exists=True, readable=True),
    settlement_csv: Path = typer.Argument(..., exists=True, readable=True),
    insar_csv: Path = typer.Argument(..., exists=True, readable=True),
):
    """Load CSVs and print basic stats."""
    inc = read_inclinometers(inclinometer_csv)
    pie = read_piezometers(piezometer_csv)
    setl = read_settlement(settlement_csv)
    insar = read_insar_csv(insar_csv)
    print({
        "inclinometers_rows": len(inc),
        "piezometers_rows": len(pie),
        "settlement_rows": len(setl),
        "insar_rows": len(insar),
    })


@app.command()
def stability(
    c_kpa: float = typer.Option(5.0, help="Cohesion c' in kPa"),
    phi_deg: float = typer.Option(28.0, help="Friction angle in degrees"),
    beta_deg: float = typer.Option(20.0, help="Slope angle in degrees"),
    height_m: float = typer.Option(20.0, help="Soil thickness in meters"),
    gamma_kN_m3: float = typer.Option(18.0, help="Unit weight in kN/m^3"),
    ru: float = typer.Option(0.2, help="Pore pressure ratio u/σn (0-1)"),
    config_path: Optional[Path] = typer.Option(None, help="Path to TOML config"),
):
    """Compute factor of safety using the infinite slope model and print risk level."""
    config = AppConfig.load(config_path)
    p = InfiniteSlopeParams(
        cohesion_kpa=c_kpa,
        phi_deg=phi_deg,
        beta_deg=beta_deg,
        height_m=height_m,
        unit_weight_kN_m3=gamma_kN_m3,
        ru=ru,
    )
    fs = factor_of_safety_infinite_slope(p)
    risk = risk_level_from_fs(fs, config.thresholds)
    print({"factor_of_safety": fs, "risk_level": risk})


@app.command()
def visualize(
    output: Path = typer.Option(Path("outputs/dam_surface.png"), help="Output PNG path"),
    width: int = 100,
    depth: int = 60,
    height: int = 30,
):
    out = render_dam_surface_png(output, width=width, depth=depth, height=height)
    print({"image": str(out)})


@app.command()
def fea(
    backend: str = typer.Option("auto", help="Backend: auto|fenics|pynastran|simplified"),
    height_m: float = 20.0,
    width_m: float = 60.0,
    surcharge_kpa: float = 10.0,
):
    if backend == "fenics":
        res = run_fea_or_fallback(height_m, width_m, surcharge_kpa)
    elif backend == "pynastran":
        res = run_pynastran_or_fallback(height_m, width_m, surcharge_kpa)
    else:
        # auto or simplified both route through FEniCS wrapper which falls back
        res = run_fea_or_fallback(height_m, width_m, surcharge_kpa)
    print(res)


@app.command()
def weather(
    latitude: float,
    longitude: float,
    start_days_ago: int = 7,
):
    end = datetime.utcnow()
    start = end - timedelta(days=start_days_ago)
    df = fetch_precipitation_series(latitude, longitude, start, end)
    print({"rows": len(df), "total_precip_mm": float(df["precipitation"].sum())})


@app.command()
def report(
    c_kpa: float = 5.0,
    phi_deg: float = 28.0,
    beta_deg: float = 20.0,
    height_m: float = 20.0,
    gamma_kN_m3: float = 18.0,
    ru: float = 0.2,
    output_dir: Path = Path("reports"),
    config_path: Optional[Path] = None,
    use_llm: bool = typer.Option(
        False,
        help=(
            "If true, use LLM to add explanatory notes (requires OPENAI_API_KEY "
            "and the openai package installed via the [llm] extra)."
        ),
    ),
):
    config = AppConfig.load(config_path)
    p = InfiniteSlopeParams(
        cohesion_kpa=c_kpa,
        phi_deg=phi_deg,
        beta_deg=beta_deg,
        height_m=height_m,
        unit_weight_kN_m3=gamma_kN_m3,
        ru=ru,
    )
    fs = factor_of_safety_infinite_slope(p)
    risk = risk_level_from_fs(fs, config.thresholds)

    # Example trend placeholders computed from sample data
    # (a real pipeline would compute from live sensor series)
    inc = pd.read_csv(Path("data/samples/inclinometers.csv"))
    slope, pval = linear_trend(inc["displacement_mm"].values)

    context = {
        "fs": fs,
        "risk_level": risk,
        "trends": {"inclinometer_disp": {"slope": slope, "pvalue": pval}},
        "notes": [
            "Stability evaluated via infinite slope method.",
            "Trends computed on sample data for demonstration.",
        ],
    }
    if use_llm:
        llm_note = explain_report_context(context)
        if llm_note:
            context["notes"].append(llm_note)
    from .reports.generate import generate_report

    out = generate_report(context, output_dir=output_dir)
    print({"report": str(out)})


@app.command()
def alert_test(
    level: str = typer.Argument("WATCH"),
    message: str = typer.Argument("Test alert from OpenDamIntegry"),
    email_to: Optional[str] = typer.Option(None),
    sms_to: Optional[str] = typer.Option(None),
    config_path: Optional[Path] = typer.Option(None),
):
    config = AppConfig.load(config_path)
    notify(level, message, config.alerts, email_to=email_to, sms_to=sms_to)
    print({"sent": True})


@app.command()
def explain(
    c_kpa: float = 5.0,
    phi_deg: float = 28.0,
    beta_deg: float = 20.0,
    height_m: float = 20.0,
    gamma_kN_m3: float = 18.0,
    ru: float = 0.2,
    config_path: Optional[Path] = None,
):
    """Use the LLM (if configured) to explain the current stability state.

    Falls back to a deterministic explanation if LLM isn't configured.
    """
    config = AppConfig.load(config_path)
    p = InfiniteSlopeParams(
        cohesion_kpa=c_kpa,
        phi_deg=phi_deg,
        beta_deg=beta_deg,
        height_m=height_m,
        unit_weight_kN_m3=gamma_kN_m3,
        ru=ru,
    )
    fs = factor_of_safety_infinite_slope(p)
    risk = risk_level_from_fs(fs, config.thresholds)
    explanation = explain_stability(fs, risk, config.thresholds)
    print({"factor_of_safety": fs, "risk_level": risk, "explanation": explanation})


@app.command()
def datasette_export(
    db_path: Path = typer.Option(
        Path("data/opendamintegry.db"),
        help="SQLite database path to write",
    ),
    samples_dir: Path = typer.Option(
        Path("data/samples"),
        help="Directory containing sample CSVs",
    ),
):
    """Export sample CSV data into a SQLite database for exploration."""
    out = export_to_sqlite(db_path, samples_dir)
    print({"sqlite_db": str(out)})


@app.command()
def datasette_serve(
    db_path: Path = typer.Option(
        Path("data/opendamintegry.db"),
        help="SQLite database path to serve",
    ),
    port: int = typer.Option(8001, help="Port to serve Datasette on"),
):
    """Serve the SQLite database with Datasette if installed."""
    info = serve_datasette(db_path, port)
    print(info)


if __name__ == "__main__":
    app()
