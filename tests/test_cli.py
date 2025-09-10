from typer.testing import CliRunner

from open_dam_integry.cli import app


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "OpenDamIntegry v" in result.stdout


def test_cli_agent_fallback():
    runner = CliRunner()
    # Ensure no API key so deterministic backend is used
    result = runner.invoke(app, ["agent", "hello"], env={"OPENAI_API_KEY": ""})
    assert result.exit_code == 0
    assert "deterministic" in result.stdout


def test_cli_agent_status():
    runner = CliRunner()
    result = runner.invoke(app, ["agent-status"])
    assert result.exit_code == 0
    # Should print a dict-like with keys including model
    assert "model" in result.stdout
