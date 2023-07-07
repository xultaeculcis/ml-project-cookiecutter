.DEFAULT_GOAL := help
isort = isort .
black = black .
flake8 = flake8 .
autoflake8 = autoflake8 .
mypy = mypy .
pre-commit = pre-commit run --all-files

DATA_DIR=data
SHELL=/bin/bash
# Note that the extra activate is needed to ensure that the activate floats env to the front of PATH
CONDA_ACTIVATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^\.PHONY: ([0-9a-zA-Z_-]+).*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-45s - %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

.PHONY: help  ## Prints help message
help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

.PHONY: conda-lock-win-64  ## Creates conda-lock file for win-64 platform
conda-lock-win-64:
	conda-lock --mamba -k explicit -f ./env.yaml -p win-64 --filename-template "conda-{platform}.lock"

.PHONY: conda-lock-linux-64  ## Creates conda-lock file for linux-64 platform
conda-lock-linux-64:
	conda-lock --mamba -k explicit -f ./env.yaml -p linux-64 --filename-template "conda-{platform}.lock"

.PHONY: conda-lock-osx-arm64  ## Creates conda-lock file for osx-arm64 platform
conda-lock-osx-arm64:
	conda-lock --mamba -k explicit -f ./env.yaml -p osx-arm64 --filename-template "conda-{platform}.lock"

.PHONY: conda-lock-all-platforms  ## Creates conda-lock file for win-64, linux-64 and osx-arm64 platforms
conda-lock-all-platforms:
	conda-lock --mamba -k explicit -f ./env.yaml -p win-64 -p linux-64 -p osx-arm64 --filename-template "conda-{platform}.lock"

.PHONY: conda-install-win-64  ## Creates env from conda-lock file for osx-arm64 platform
conda-install-win-64:
	conda-lock install -n {{cookiecutter.repo_name}} conda-win-64.lock

.PHONY: conda-install-linux-64  ## Creates env from conda-lock file for linux-64 platform
conda-install-linux-64:
	conda-lock install -n {{cookiecutter.repo_name}} conda-linux-64.lock

.PHONY: conda-install-osx-arm64  ## Creates env from conda-lock file for osx-arm64 platform
conda-install-osx-arm64:
	conda-lock install -n {{cookiecutter.repo_name}} conda-osx-arm64.lock

.PHONY: setup-pre-commit  ## Installs pre-commit hooks
setup-pre-commit:
	$(CONDA_ACTIVATE) {{cookiecutter.repo_name}} ; pre-commit install

.PHONY: setup-editable  ## Installs the project in an editable mode
setup-editable:
	$(CONDA_ACTIVATE) {{cookiecutter.repo_name}} ; pip install -e .

.PHONY: setup-local-env-win-64  ## Creates local environment and installs pre-commit hooks for win-64 platform
setup-local-env-win-64: conda-install-win-64 setup-pre-commit setup-editable

.PHONY: setup-local-env-linux-64  ## Creates local environment and installs pre-commit hooks for linux-64 platform
setup-local-env-linux-64: conda-install-linux-64 setup-pre-commit setup-editable

.PHONY: setup-local-env-osx-arm64  ## Creates local environment and installs pre-commit hooks for osx-arm64 platform
setup-local-env-osx-arm64: conda-install-osx-arm64 setup-pre-commit setup-editable

.PHONY: format  ## Runs code formatting (isort, black, flake8)
format:
	$(isort)
	$(black)
	$(flake8)

.PHONY: type-check  ## Runs type checking with mypy
type-check:
	pre-commit run --all-files mypy

.PHONY: test  ## Runs pytest
test:
	pytest -v tests/

.PHONY: testcov  ## Runs tests and generates coverage reports
testcov:
	@rm -rf htmlcov
	pytest -v --cov-report html --cov-report xml --cov=zf-powerbi-mongo tests/

.PHONY: mpc  ## Runs manual pre-commit stuff
mpc: format type-check test

.PHONY: docs  ## Build the documentation
docs:
	mkdocs build

.PHONY: pc  ## Runs pre-commit hooks
pc:
	$(pre-commit)

.PHONY: clean  ## Cleans artifacts
clean:
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
	rm -rf zf-powerbi-mongo/*.so
	rm -rf .mypy_cache
	rm -rf .benchmark
	rm -rf .hypothesis
	rm -rf docs-site
