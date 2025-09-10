# API Reference

Run locally
- `odintegry api --host 0.0.0.0 --port 8000`

Auth
- Optional API key gate: set `ODI_API_KEY`. Client must send header `X-API-Key: <value>`.

Endpoints
- GET `/health`
  - 200 JSON: `{ "status": "ok", "version": "<semver>" }`
- POST `/stability`
  - Body JSON: `{ "c_kpa": float, "phi_deg": float, "beta_deg": float, "height_m": float, "gamma_k_n_m3": float, "ru": float }`
  - 200 JSON: `{ "fs": float, "risk": "normal|watch|warning|alert" }`
- POST `/agent/respond`
  - Body JSON: `{ "prompt": "..." }`
  - Behavior: Uses OpenAI Assistants when configured, falls back to deterministic local responses otherwise.

Examples
- `curl -s http://127.0.0.1:8000/health`
- `curl -s -X POST http://127.0.0.1:8000/stability -H 'Content-Type: application/json' -d '{"c_kpa":8,"phi_deg":30,"beta_deg":18,"height_m":15,"gamma_k_n_m3":18.5,"ru":0.15}'`

