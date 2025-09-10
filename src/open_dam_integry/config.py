"""Top-level config and data models for OpenDamIntegry."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

try:  # Python 3.11+
    import tomllib  # type: ignore[attr-defined]
except Exception:  # pragma: no cover - for Python 3.10 fallback
    import tomli as tomllib  # type: ignore[no-redef]


class Thresholds(BaseModel):
    normal_fs_min: float = Field(1.3, description="Minimum factor of safety for normal operations")
    watch_fs_min: float = Field(1.2, description="Minimum factor of safety for watch level")
    warning_fs_min: float = Field(1.1, description="Minimum factor of safety for warning level")
    alert_fs_min: float = Field(1.0, description="Minimum factor of safety for alert level")


class AlertsConfig(BaseModel):
    email_enabled: bool = False
    sms_enabled: bool = False


class WeatherConfig(BaseModel):
    provider: str = "open-meteo"
    latitude: float = 0.0
    longitude: float = 0.0


class ProjectConfig(BaseModel):
    name: str = "OpenDamIntegry"


class AppConfig(BaseModel):
    project: ProjectConfig = ProjectConfig()
    thresholds: Thresholds = Thresholds()
    alerts: AlertsConfig = AlertsConfig()
    weather: WeatherConfig = WeatherConfig()

    @staticmethod
    def load(path: Path | None = None) -> AppConfig:
        if path is None:
            # Default path relative to repo root: <root>/src/open_dam_integry/config.py -> parents[2] == <root>
            candidate = Path(__file__).resolve().parents[2] / "config" / "opendamintegry.toml"
        else:
            candidate = Path(path)
        if not candidate.exists():
            return AppConfig()
        data = tomllib.loads(candidate.read_text(encoding="utf-8"))
        return AppConfig.model_validate(data)
