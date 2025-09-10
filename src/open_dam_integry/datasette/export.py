"""Datasette export and serving helpers.

Exports project CSV data into a SQLite DB and optionally serves it with Datasette.
"""

from __future__ import annotations

import sqlite3
import subprocess
from pathlib import Path

import pandas as pd


def export_to_sqlite(db_path: Path | str, samples_dir: Path | str) -> Path:
    db_path = Path(db_path)
    samples_dir = Path(samples_dir)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    try:
        # Load known sample CSVs if present
        csv_map = {
            "inclinometers": samples_dir / "inclinometers.csv",
            "piezometers": samples_dir / "piezometers.csv",
            "settlement_plates": samples_dir / "settlement_plates.csv",
            "insar": samples_dir / "insar.csv",
        }
        for table, path in csv_map.items():
            if path.exists():
                df = pd.read_csv(path)
                df.to_sql(table, conn, if_exists="replace", index=False)
        # Simple metadata table
        conn.execute("CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT)")
        conn.execute(
            "INSERT OR REPLACE INTO metadata(key, value) VALUES (?, ?)",
            ("source", "OpenDamIntegry sample export"),
        )
        conn.commit()
    finally:
        conn.close()
    return db_path


def serve_datasette(db_path: Path | str, port: int = 8001) -> dict[str, str | int | bool]:
    """Run `datasette` on the given SQLite DB if installed.

    Returns an info dict with either error or invocation details.
    """
    db_path = Path(db_path)
    if not db_path.exists():
        return {"served": False, "error": f"DB not found: {db_path}"}
    # Check datasette availability
    try:
        subprocess.run(["datasette", "--version"], check=True, capture_output=True)
    except Exception:
        return {
            "served": False,
            "error": "datasette is not installed. Install via extras: '.[datasette]'",
        }

    try:
        # Start server (foreground). Users can Ctrl-C to stop.
        # We avoid shell=True and keep command explicit.
        cmd = [
            "datasette",
            "serve",
            str(db_path),
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ]
        subprocess.run(cmd, check=True)
        return {"served": True, "db": str(db_path), "port": port}
    except subprocess.CalledProcessError as e:
        return {"served": False, "error": f"datasette serve failed: {e}"}
