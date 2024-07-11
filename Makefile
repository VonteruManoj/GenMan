SHELL:=/bin/bash
SILENT:=@
VERBOSE:=no

serve:
	@poetry run uvicorn src.main:app --proxy-headers --host 0.0.0.0 --port 8055 --reload
.PHONY: serve

isort:
	@poetry run isort .
.PHONY: isort

black:
	@poetry run black .
.PHONY: black

flake8:
	@poetry run flake8 .
.PHONY: flake8

test:
	@poetry run pytest
.PHONY: test

container-test:
	@cd ../zt_local && docker compose exec ai-service python -m pytest --cov --cov-fail-under=80 --verbose --timeout=30
.PHONY: container-test

test-coverage:
	@poetry run pytest --cov --cov-fail-under=80
.PHONY: test-coverage

pre-commit: isort black flake8 container-test
.PHONY: pre-commit

pre-commit-no-test: isort black flake8
.PHONY: pre-commit-ct