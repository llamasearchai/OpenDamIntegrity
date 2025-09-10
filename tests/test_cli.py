from typer.testing import CliRunner
from open_dam_integry.cli import app


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "OpenDamIntegry v" in result.stdout

