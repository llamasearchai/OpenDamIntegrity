# Installation

Requirements
- Python 3.10+
- macOS/Linux/Windows

Using uv (recommended)
1) Create venv and install dev tools:
   - uv venv
   - uv pip install -e .[dev]
2) Optional extras:
   - LLM: uv pip install -e '.[llm]'
   - Viz: uv pip install -e '.[viz]'
   - FEA: uv pip install -e '.[fea]'
   - Reports: uv pip install -e '.[reports]'

Using pip
- python -m venv .venv && . .venv/bin/activate
- pip install -e .[dev]

Docker
- Build: docker build -t opendamintegry:latest .
- Run API: docker run --rm -p 8000:8000 -e OPENAI_API_KEY=... opendamintegry:latest

Build artifacts
- Hatch build: hatch build
- Wheels and sdist appear in dist/

