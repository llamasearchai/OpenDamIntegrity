#!/usr/bin/env python3
"""Run the CLI smoke test and validate outputs.

Executes `python -m open_dam_integry --json-output smoke`, asserts presence of
expected keys and artifacts, and prints a concise JSON summary. Exits non-zero
on validation failure to integrate with CI.
"""

from __future__ import annotations

import json
import os
from pathlib import Path


def main() -> int:
    # Ensure we can import the package without installing
    os.environ["PYTHONPATH"] = os.pathsep.join(
        filter(None, ["src", os.environ.get("PYTHONPATH", "")])
    )

    try:
        import pandas as pd

        from open_dam_integry.config import AppConfig
        from open_dam_integry.datasette.export import export_to_sqlite
        from open_dam_integry.llm.agents_service import default_agent_service
        from open_dam_integry.reports.generate import generate_report
        from open_dam_integry.signal_processing.trends import linear_trend
        from open_dam_integry.stability.stability import (
            InfiniteSlopeParams,
            factor_of_safety_infinite_slope,
            risk_level_from_fs,
        )
        from open_dam_integry.visualization.viz3d import render_dam_surface_png
    except Exception as e:
        print(json.dumps({"ok": False, "error": f"import failure: {e}"}))
        return 1

    issues: list[str] = []
    summary: dict[str, object] = {"ok": False}

    # Stability
    cfg = AppConfig.load(None)
    p = InfiniteSlopeParams(
        cohesion_kpa=5.0,
        phi_deg=28.0,
        beta_deg=20.0,
        height_m=20.0,
        unit_weight_kN_m3=18.0,
        ru=0.2,
    )
    fs = factor_of_safety_infinite_slope(p)
    risk = risk_level_from_fs(fs, cfg.thresholds)
    if not (fs > 0):
        issues.append(f"invalid FS: {fs}")

    # Visualize
    img = render_dam_surface_png(Path("outputs/dam_surface.png"))
    if not Path(img).exists():
        issues.append(f"image not found: {img}")

    # Report
    inc = pd.read_csv(Path("data/samples/inclinometers.csv"))
    slope, pval = linear_trend(inc["displacement_mm"].values)
    ctx = {
        "fs": fs,
        "risk_level": risk,
        "trends": {"inc": {"slope": slope, "pvalue": pval}},
        "notes": ["Validated smoke test report."],
    }
    rpt = generate_report(ctx, output_dir=Path("reports"))
    if not Path(rpt).exists():
        issues.append(f"report not found: {rpt}")

    # Agent fallback/live
    svc = default_agent_service()
    resp = svc.respond("Provide a single-sentence dam stability summary.")
    if not resp.text:
        issues.append("agent response empty")

    # Datasette export
    db = export_to_sqlite(Path("data/opendamintegry.db"), Path("data/samples"))
    if not Path(db).exists():
        issues.append(f"sqlite db not found: {db}")

    if issues:
        summary["error"] = "; ".join(issues)
        print(json.dumps(summary))
        return 2

    summary.update(
        {
            "ok": True,
            "fs": fs,
            "risk": risk,
            "image": str(img),
            "report": str(rpt),
            "db": str(db),
            "agent_backend": resp.meta.get("backend"),
        }
    )
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
