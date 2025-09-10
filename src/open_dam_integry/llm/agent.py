"""LLM integration helpers (OpenAI) with graceful fallback.

This module uses the OpenAI Python SDK if available and OPENAI_API_KEY is set.
It provides deterministic fallbacks if the SDK or key is unavailable.
"""
from __future__ import annotations

import os
from typing import Any, Mapping, Optional

try:
    # OpenAI Python SDK v1+
    import openai  # type: ignore

    _OPENAI_AVAILABLE = True
except Exception:  # pragma: no cover - optional
    openai = None  # type: ignore
    _OPENAI_AVAILABLE = False


def _call_openai(prompt: str, model: Optional[str] = None, temperature: float = 0.2) -> Optional[str]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not (_OPENAI_AVAILABLE and api_key):
        return None
    # Prefer environment variable for model selection; provide a small default
    model = model or os.getenv("OAI_MODEL", "gpt-4o-mini")

    try:
        # New SDK style: client = openai.OpenAI(); client.chat.completions.create
        client = openai.OpenAI(api_key=api_key)  # type: ignore[attr-defined]
        resp = client.chat.completions.create(  # type: ignore[attr-defined]
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful domain expert in tailings dam monitoring."},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=300,
        )
        content = resp.choices[0].message.content if resp and resp.choices else None
        return content
    except Exception:
        # Best-effort fallback to older API shape if present
        try:
            resp = openai.ChatCompletion.create(  # type: ignore[attr-defined]
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful domain expert in tailings dam monitoring."},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=300,
            )
            content = resp["choices"][0]["message"]["content"]
            return str(content)
        except Exception:
            return None


def explain_stability(fs: float, risk_level: str, thresholds: Any) -> str:
    """Return a short explanation for the computed stability state.

    Uses OpenAI if configured; otherwise deterministic domain logic.
    """
    prompt = (
        "Provide a concise, engineer-friendly explanation (<= 120 words) of the dam stability "
        f"given factor-of-safety {fs:.3f} and risk level '{risk_level}'. "
        "Explain why this level applies relative to typical threshold bands and suggest a next check."
    )
    llm_text = _call_openai(prompt)
    if llm_text:
        return llm_text.strip()

    # Deterministic fallback
    t = thresholds
    band = (
        f"NORMAL (>= {t.normal_fs_min})" if fs >= t.normal_fs_min else
        f"WATCH (>= {t.watch_fs_min})" if fs >= t.watch_fs_min else
        f"WARNING (>= {t.warning_fs_min})" if fs >= t.warning_fs_min else
        f"ALERT (>= {t.alert_fs_min})" if fs >= t.alert_fs_min else
        "EMERGENCY (< alert minimum)"
    )
    suggestions = {
        "NORMAL": "Continue routine monitoring; review weekly trends.",
        "WATCH": "Increase monitoring frequency; check pore pressures and rainfall forecasts.",
        "WARNING": "Plan mitigation; inspect drainage and slopes; validate sensor health.",
        "ALERT": "Initiate response plan; reduce loads; prepare for possible evacuation.",
        "EMERGENCY": "Execute emergency procedures immediately; ensure personnel safety.",
    }
    suggestion = suggestions.get(risk_level, "Review data quality and assumptions; reassess promptly.")
    return (
        f"Computed FS={fs:.3f} maps to {risk_level} based on configured bands ({band}). {suggestion}"
    )


def explain_report_context(context: Mapping[str, Any]) -> str:
    """Generate a brief LLM note summarizing the report context (or a deterministic fallback)."""
    fs = context.get("fs")
    risk = context.get("risk_level", "UNKNOWN")
    trends = context.get("trends", {})
    trend_summ = ", ".join(
        f"{k}: slope={v.get('slope', 0):.6f}, p={v.get('pvalue', 1):.3g}" for k, v in trends.items()
    )
    prompt = (
        "Summarize dam status using the following: "
        f"FS={fs}, risk='{risk}', trends=[{trend_summ}]. "
        "Be specific but concise (<= 120 words); mention if trends suggest deteriorating conditions."
    )
    llm_text = _call_openai(prompt)
    if llm_text:
        return llm_text.strip()
    return (
        f"Summary: FS={fs} with risk '{risk}'. Trends: {trend_summ or 'no trend data'}. "
        "Monitor for changes; reassess after significant precipitation or loading."
    )

