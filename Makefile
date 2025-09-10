SHELL := /bin/bash

.PHONY: help venv install dev lint type format test smoke smoke-json smoke-api api-run datasette-export datasette-serve dist tag clean docker-build docker-run

help:
	@echo "Targets: venv, install, dev, lint, type, format, test, smoke, smoke-json, smoke-api, api-run, datasette-export, datasette-serve, dist, tag, clean"

venv:
	python -m venv .venv && . .venv/bin/activate && pip install -U pip

install:
	. .venv/bin/activate && pip install -e .

dev:
	. .venv/bin/activate && pip install -e .[dev,llm]

lint:
	. .venv/bin/activate && ruff check . && black --check .

type:
	. .venv/bin/activate && mypy src

format:
	. .venv/bin/activate && ruff check --fix . && black .

test:
	. .venv/bin/activate && pytest -q

smoke:
	. .venv/bin/activate && PYTHONPATH=src python scripts/validate_smoke.py

smoke-json:
	. .venv/bin/activate && python -m open_dam_integry --json-output smoke

smoke-api:
	. .venv/bin/activate && PYTHONPATH=src python scripts/smoke_api.py

api-run:
	. .venv/bin/activate && python -m open_dam_integry api --host 0.0.0.0 --port 8000

datasette-export:
	. .venv/bin/activate && python -m open_dam_integry --json-output datasette-export

datasette-serve:
	. .venv/bin/activate && python -m open_dam_integry --json-output datasette-serve || true

dist:
	python -m build

tag:
	@VER=$$(sed -n "s/^version = \"\(.*\)\"/\1/p" pyproject.toml | head -n1); \
	if [ -z "$$VER" ]; then echo "Version not found in pyproject.toml"; exit 1; fi; \
	echo "Tagging v$$VER"; \
	git tag v$$VER; \
	git show v$$VER --quiet

clean:
	rm -rf .venv .pytest_cache .ruff_cache .tox dist build reports outputs

docker-build:
	docker build -t opendamintegry:$(shell sed -n 's/version = "\(.*\)"/\1/p' pyproject.toml | head -n1) .

docker-run:
	docker run --rm -p 8000:8000 opendamintegry:$(shell sed -n 's/version = "\(.*\)"/\1/p' pyproject.toml | head -n1)
