.DEFAULT_GOAL := help

DATA_DIR=data
SHELL=/bin/bash

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-10s - %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:  ## Prints help message
	@python3 -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

.PHONY: env  # Setup uv env and packages
env:
	uv sync --all-groups
	uv run pre-commit install

.PHONY: test
test:  ## Runs pytest
	uv run pytest -v tests/

.PHONY: docs
docs:  ## Build the documentation
	uv run mkdocs build

.PHONY: pc
pc:  ## Runs pre-commit hooks
	uv run pre_commit run --all-files

.PHONY: clean
clean:  ## Cleans artifacts
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -rf .cache
	rm -rf flame
	rm -rf htmlcov
	rm -rf .pytest_cache
	rm -rf *.egg-info
	rm -f .coverage
	rm -f .coverage.*
	rm -f coverage.*
	rm -rf build
	rm -rf perf.data*
	rm -rf .mypy_cache
	rm -rf .benchmark
	rm -rf .hypothesis
	rm -rf docs-site
