"""FastAPI application exposing health, stability, and agent endpoints."""

from __future__ import annotations

import logging
import os
import time

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

from .config import AppConfig
from .llm.agents_service import default_agent_service
from . import __version__
from .stability.stability import (
    InfiniteSlopeParams,
    factor_of_safety_infinite_slope,
    risk_level_from_fs,
)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("odintegry.api")

app = FastAPI(title="OpenDamIntegry API", version="1.0")


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Optional API key gate. If `ODI_API_KEY` is set, requests must include X-API-Key.

    - Env: `ODI_API_KEY` (string). If unset/empty, gate is disabled.
    - Header: `X-API-Key: <value>`
    """
    expected = os.getenv("ODI_API_KEY")
    if expected and x_api_key != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.middleware("http")
async def log_requests(request, call_next):  # type: ignore[no-untyped-def]
    start = time.time()
    response = await call_next(request)
    dur_ms = int((time.time() - start) * 1000)
    logger.info(
        "request",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status": response.status_code,
            "ms": dur_ms,
        },
    )
    return response


class StabilityRequest(BaseModel):
    c_kpa: float = 5.0
    phi_deg: float = 28.0
    beta_deg: float = 20.0
    height_m: float = 20.0
    gamma_kN_m3: float = 18.0
    ru: float = 0.2
    config_path: str | None = None


class AgentPrompt(BaseModel):
    prompt: str


@app.get("/health", dependencies=[Depends(require_api_key)])
def health() -> dict:
    return {"status": "ok"}


@app.get("/healthz", dependencies=[Depends(require_api_key)])
def healthz() -> dict:
    """Kubernetes-style health alias."""
    return {"status": "ok"}


@app.post("/stability", dependencies=[Depends(require_api_key)])
def compute_stability(req: StabilityRequest) -> dict:
    config = AppConfig.load(None if req.config_path is None else req.config_path)
    params = InfiniteSlopeParams(
        cohesion_kpa=req.c_kpa,
        phi_deg=req.phi_deg,
        beta_deg=req.beta_deg,
        height_m=req.height_m,
        unit_weight_kN_m3=req.gamma_kN_m3,
        ru=req.ru,
    )
    fs = factor_of_safety_infinite_slope(params)
    risk = risk_level_from_fs(fs, config.thresholds)
    return {"factor_of_safety": fs, "risk_level": risk}


@app.post("/agent/respond", dependencies=[Depends(require_api_key)])
def agent_respond(body: AgentPrompt) -> dict:
    service = default_agent_service()
    resp = service.respond(body.prompt)
    return {"text": resp.text, "meta": resp.meta}


@app.get("/metadata", dependencies=[Depends(require_api_key)])
def metadata() -> dict:
    """Return service metadata: version and LLM integration status."""
    service = default_agent_service()
    return {
        "version": __version__,
        "agent": service.status(),
    }
