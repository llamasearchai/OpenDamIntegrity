from pathlib import Path

from open_dam_integry.config import AppConfig


def test_config_default_loads_repo_config():
    cfg = AppConfig.load(None)
    # Values from config/opendamintegry.toml
    assert cfg.project.name == "OpenDamIntegry"
    assert cfg.thresholds.normal_fs_min == 1.3


def test_config_missing_returns_defaults(tmp_path: Path):
    missing = tmp_path / "nope.toml"
    cfg = AppConfig.load(missing)
    default = AppConfig()
    assert cfg == default
