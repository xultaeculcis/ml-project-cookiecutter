.DEFAULT_GOAL := help

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

.PHONY: env
env:  ## Sets up the uv env with all dependency groups and installs pre-commit hooks
	uv sync --all-groups
	uv run pre-commit install

.PHONY: test
test:  ## Runs fast tests (without the slow ones)
	uv run pytest -v -m "not slow" tests/

.PHONY: test-all
test-all:  ## Runs all tests, including slow ones that run uv, pre-commit and cruft in a generated project
	uv run pytest -v tests/

.PHONY: docs
docs:  ## Builds the documentation
	uv run --group docs mkdocs build --strict

.PHONY: pc
pc:  ## Runs pre-commit hooks
	uv run pre-commit run --all-files

.PHONY: clean
clean:  ## Cleans artifacts
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -rf .cache
	rm -rf htmlcov
	rm -rf .pytest_cache
	rm -rf *.egg-info
	rm -f .coverage
	rm -f .coverage.*
	rm -f coverage.*
	rm -rf build
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf docs-site

.PHONY: gha-update
gha-update:  ## Updates the pinned GitHub Actions in the root workflows to the latest SHAs
	uvx gha-update
