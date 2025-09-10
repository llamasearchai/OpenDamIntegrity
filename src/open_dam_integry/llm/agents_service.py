"""OpenAI Agents/Assistants integration with safe fallbacks.

This module provides a thin service that prefers the OpenAI Assistants v2 API
if available and configured, falls back to chat completions when possible,
and finally provides a deterministic response when no OpenAI API is configured.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any

try:
    import openai  # type: ignore

    _OPENAI_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    openai = None  # type: ignore
    _OPENAI_AVAILABLE = False


DEFAULT_MODEL = os.getenv("OAI_MODEL", "gpt-4o-mini")


@dataclass
class AgentResponse:
    text: str
    meta: dict[str, Any]


class AgentService:
    """Service wrapper around OpenAI Assistants/Chat with fallbacks."""

    def __init__(
        self,
        api_key: str | None | None = None,
        model: str | None | None = None,
        assistant_id: str | None | None = None,
        instructions: str | None | None = None,
        request_timeout_s: float = 15.0,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or DEFAULT_MODEL
        self.assistant_id = assistant_id or os.getenv("OAI_ASSISTANT_ID")
        self.instructions = instructions or os.getenv(
            "OAI_ASSISTANT_INSTRUCTIONS",
            (
                "You are a helpful domain expert in tailings dam monitoring, "
                "stability analysis, and sensor data QA."
            ),
        )
        # Allow timeout override via env
        try:
            env_timeout = float(os.getenv("OAI_REQUEST_TIMEOUT_S", ""))
        except ValueError:
            env_timeout = None
        self.request_timeout_s = env_timeout or request_timeout_s
        self._client = None

        if _OPENAI_AVAILABLE and self.api_key:
            try:
                self._client = openai.OpenAI(api_key=self.api_key)  # type: ignore[attr-defined]
            except Exception:
                self._client = None

    # ---------- Public API ----------
    def is_available(self) -> bool:
        return bool(self._client)

    def respond(self, prompt: str) -> AgentResponse:
        """Generate a response, preferring Assistants API, then Chat, else deterministic."""
        # Try Assistants first
        if self._client:
            try:
                text = self._respond_via_assistants(prompt)
                if text:
                    return AgentResponse(text=text, meta={"backend": "assistants"})
            except Exception:
                # Fall through to chat
                pass

            # Try Chat Completions
            try:
                text = self._respond_via_chat(prompt)
                if text:
                    return AgentResponse(text=text, meta={"backend": "chat"})
            except Exception:
                pass

        # Deterministic fallback
        return AgentResponse(
            text=self._deterministic_response(prompt),
            meta={"backend": "deterministic"},
        )

    def status(self) -> dict[str, Any]:
        """Return a diagnostic status for the service without making network calls."""
        return {
            "openai_imported": _OPENAI_AVAILABLE,
            "client_initialized": bool(self._client),
            "assistant_id_configured": bool(self.assistant_id),
            "model": self.model,
            "timeout_s": self.request_timeout_s,
        }

    # ---------- Backends ----------
    def _respond_via_assistants(self, prompt: str) -> str | None:
        assert self._client is not None
        assistant_id = self.assistant_id
        if not assistant_id:
            # Create a lightweight assistant on the fly
            assistant = self._client.beta.assistants.create(  # type: ignore[attr-defined]
                name="OpenDamIntegry Assistant",
                instructions=self.instructions,
                model=self.model,
            )
            assistant_id = assistant.id
            self.assistant_id = assistant_id

        thread = self._client.beta.threads.create()  # type: ignore[attr-defined]
        self._client.beta.threads.messages.create(  # type: ignore[attr-defined]
            thread_id=thread.id,
            role="user",
            content=prompt,
        )
        run = self._client.beta.threads.runs.create(  # type: ignore[attr-defined]
            thread_id=thread.id, assistant_id=assistant_id
        )

        # Poll for completion with a soft timeout
        deadline = time.time() + self.request_timeout_s
        while time.time() < deadline:
            run = self._client.beta.threads.runs.retrieve(  # type: ignore[attr-defined]
                thread_id=thread.id, run_id=run.id
            )
            if run.status in ("completed", "failed", "cancelled"):
                break
            time.sleep(0.4)

        if getattr(run, "status", None) != "completed":
            return None

        msgs = self._client.beta.threads.messages.list(  # type: ignore[attr-defined]
            thread_id=thread.id
        )
        # Most recent assistant message
        for msg in msgs.data:  # type: ignore[attr-defined]
            if getattr(msg, "role", None) == "assistant" and getattr(msg, "content", None):
                parts = msg.content
                # content can be a list of rich parts
                texts: list[str] = []
                for part in parts:
                    if getattr(part, "type", "") == "text" and getattr(part, "text", None):
                        value = getattr(part.text, "value", None)
                        if value:
                            texts.append(str(value))
                if texts:
                    return "\n".join(texts)
        return None

    def _respond_via_chat(self, prompt: str) -> str | None:
        assert self._client is not None
        resp = self._client.chat.completions.create(  # type: ignore[attr-defined]
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": self.instructions,
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=400,
        )
        return resp.choices[0].message.content if resp and resp.choices else None

    @staticmethod
    def _deterministic_response(prompt: str) -> str:
        preview = prompt.strip().replace("\n", " ")
        if len(preview) > 160:
            preview = preview[:157] + "..."
        return (
            "Agents not available. Deterministic note: "
            f"Received prompt: '{preview}'. "
            "Configure OPENAI_API_KEY to enable LLM responses."
        )


def default_agent_service() -> AgentService:
    return AgentService()
