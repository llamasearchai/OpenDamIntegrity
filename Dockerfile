FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update -y && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md /app/
COPY src /app/src

# Install only runtime deps with optional LLM extras
RUN pip install --upgrade pip && \
    pip install ".[llm]"

EXPOSE 8000

ENV OPENAI_API_KEY="" \
    OAI_MODEL=gpt-4o-mini

CMD ["python", "-m", "uvicorn", "open_dam_integry.api:app", "--host", "0.0.0.0", "--port", "8000"]

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python - << 'PY' || exit 1
import os, json, urllib.request
url = 'http://127.0.0.1:8000/health'
req = urllib.request.Request(url, headers={'X-API-Key': os.getenv('ODI_API_KEY','')})
with urllib.request.urlopen(req, timeout=3) as r:
    data = json.loads(r.read().decode('utf-8'))
    assert data.get('status') == 'ok'
print('ok')
PY

