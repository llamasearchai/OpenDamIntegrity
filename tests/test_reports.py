from pathlib import Path

from open_dam_integry.reports.generate import generate_report


def test_generate_report_writes_html(tmp_path: Path):
    context = {
        "fs": 1.42,
        "risk_level": "NORMAL",
        "trends": {"inc": {"slope": 0.000123, "pvalue": 0.05}},
        "notes": ["Automated test report."],
    }
    out = generate_report(context, output_dir=tmp_path)
    assert out.exists()
    html = out.read_text(encoding="utf-8")
    # Basic sanity checks
    assert "OpenDamIntegry Report" in html
    assert "Factor of Safety" in html
    assert "NORMAL" in html

