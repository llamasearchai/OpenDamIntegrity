SHELL := /bin/bash

.PHONY: help venv install dev lint test smoke clean docker-build docker-run

help:
	@echo "Targets: venv, install, dev, lint, test, smoke, clean"

venv:
	python -m venv .venv && . .venv/bin/activate && pip install -U pip

install:
	. .venv/bin/activate && pip install -e .

dev:
	. .venv/bin/activate && pip install -e .[dev,llm]

lint:
	. .venv/bin/activate && ruff check . && black --check . && mypy src

test:
	. .venv/bin/activate && pytest -q

smoke:
	. .venv/bin/activate && odintegry smoke

clean:
	rm -rf .venv .pytest_cache .ruff_cache .tox dist build reports outputs

docker-build:
	docker build -t opendamintegry:$(shell sed -n 's/version = "\(.*\)"/\1/p' pyproject.toml | head -n1) .

docker-run:
	docker run --rm -p 8000:8000 opendamintegry:$(shell sed -n 's/version = "\(.*\)"/\1/p' pyproject.toml | head -n1)
