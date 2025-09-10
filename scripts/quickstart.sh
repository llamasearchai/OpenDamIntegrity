#!/usr/bin/env bash
set -euo pipefail

echo "==> Creating venv and installing dev + llm extras"
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .[dev,llm]

echo "==> CLI version"
odintegry version

echo "==> Running smoke test"
odintegry smoke

echo "==> Starting API (background)"
uvicorn open_dam_integry.api:app --host 127.0.0.1 --port 8000 &
PID=$!
sleep 1
echo "==> Health check"
curl -sSf http://127.0.0.1:8000/health | jq . || true
kill $PID || true

echo "==> Done"

