import sqlite3
from pathlib import Path

from open_dam_integry.datasette.export import export_to_sqlite


def test_export_to_sqlite_creates_tables(tmp_path: Path):
    db_path = tmp_path / "opendamintegry.db"
    samples_dir = Path("data/samples")
    out = export_to_sqlite(db_path, samples_dir)
    assert out.exists()
    conn = sqlite3.connect(out)
    try:
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = {row[0] for row in cur.fetchall()}
        # At minimum, metadata table should exist; sample CSVs add more if present
        assert "metadata" in tables
        # If sample CSVs are present in repo, check one expected table
        if (samples_dir / "inclinometers.csv").exists():
            assert "inclinometers" in tables
    finally:
        conn.close()
