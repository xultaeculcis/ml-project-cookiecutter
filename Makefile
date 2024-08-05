.DEFAULT_GOAL := help
pre-commit = pre-commit run --all-files

DATA_DIR=data
SHELL=/bin/bash
# Note that the extra activate is needed to ensure that the activate floats env to the front of PATH
CONDA_ACTIVATE_BASE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate base
CONDA_ACTIVATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate ml-project-cookiecutter

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-45s - %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:  ## Prints help message
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

.PHONY: env
env:  ## Creates local environment and install pre-commit hooks
	$(CONDA_ACTIVATE_BASE) ; conda env create -f ./env.yaml
	$(CONDA_ACTIVATE) ; pre-commit install

.PHONY: test
test:  ## Runs pytest
	pytest -v tests/

.PHONY: docs
docs:  ## Build the documentation
	mkdocs build

.PHONY: pc
pc:  ## Runs pre-commit hooks
	$(pre-commit)

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
