.DEFAULT_GOAL := help
SHELL := /bin/bash

MLFLOW_TRACKING_URI ?= sqlite:///mlflow.db
# One BLAS/OpenMP thread per pytest-xdist worker, so parallel workers do not oversubscribe the CPU.
TEST_ENV := OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^\.PHONY: ([0-9a-zA-Z_-]+).*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-30s - %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

.PHONY: help  ## Print this help message
help:
	@cat $(MAKEFILE_LIST) | python3 -c "$$PRINT_HELP_PYSCRIPT"

# Environment

.PHONY: env  ## Create or update the local environment with all dependency groups (creates uv.lock if missing)
env:
	uv sync --all-groups

.PHONY: setup-pre-commit  ## Install the pre-commit git hooks
setup-pre-commit:
	uv run pre-commit install

.PHONY: init-project  ## Initialize a freshly generated project (env + pre-commit hooks)
init-project:
	$(MAKE) env
	$(MAKE) setup-pre-commit

.PHONY: lock  ## Update uv.lock after editing dependencies in pyproject.toml
lock:
	uv lock

.PHONY: upgrade  ## Upgrade all locked dependencies to the latest allowed versions
upgrade:
	uv lock --upgrade

# Code quality

.PHONY: format  ## Fix lint issues and format code with ruff
format:
	uv run ruff check --fix .
	uv run ruff format .

.PHONY: lint  ## Check lint and formatting with ruff (no changes)
lint:
	uv run ruff check .
	uv run ruff format --check .

.PHONY: type-check  ## Run mypy on src and tests
type-check:
	uv run mypy src tests

.PHONY: test  ## Run tests in parallel, without slow and gpu tests
test:
	$(TEST_ENV) uv run pytest -m "not slow and not gpu" -n auto

.PHONY: test-all  ## Run all tests in parallel, including slow and gpu tests
test-all:
	$(TEST_ENV) uv run pytest -n auto

.PHONY: testcov  ## Run tests with coverage (HTML + XML reports, fails below the threshold)
testcov:
	@rm -rf htmlcov
	$(TEST_ENV) uv run pytest -m "not slow and not gpu" -n auto --cov --cov-report=term --cov-report=html --cov-report=xml

.PHONY: pc  ## Run all pre-commit hooks on all files
pc:
	uv run pre-commit run --all-files

# Documentation

.PHONY: docs  ## Build the documentation
docs:
	uv run --group docs mkdocs build --strict

.PHONY: docs-serve  ## Serve the documentation locally with live reload
docs-serve:
	uv run --group docs mkdocs serve

# Experiment tracking

.PHONY: mlflow-ui  ## Start the MLflow UI (MLFLOW_TRACKING_URI, default sqlite:///mlflow.db)
mlflow-ui:
	uv run mlflow ui --backend-store-uri $(MLFLOW_TRACKING_URI)

.PHONY: mlflow-gc  ## Permanently remove deleted MLflow runs and experiments
mlflow-gc:
	MLFLOW_TRACKING_URI=$(MLFLOW_TRACKING_URI) uv run mlflow gc --backend-store-uri $(MLFLOW_TRACKING_URI)

# Analysis

.PHONY: lab  ## Start JupyterLab
lab:
	uv run --group analysis jupyter lab

# Cleanup

.PHONY: clean  ## Remove caches and build artifacts
clean:
	find . -type d -name __pycache__ -not -path "./.venv/*" -prune -exec rm -rf {} +
	find . -type f -name '*.py[co]' -not -path "./.venv/*" -delete
	rm -rf .cache .pytest_cache .mypy_cache .ruff_cache .hypothesis
	rm -rf htmlcov .coverage .coverage.* coverage.xml
	rm -rf build dist *.egg-info
	rm -rf docs-site

# Extra targets (docker-*, aml-*, ...) live in mk/*.mk; `make help` lists them too.
-include mk/*.mk
