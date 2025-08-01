.DEFAULT_GOAL := help
ruff-lint = uv run ruff check --fix --preview .
ruff-format = uv run ruff format --preview .
mypy = uv run mypy .
pre-commit = uv run pre-commit run --all-files

DATA_DIR=data
SHELL=/bin/bash

IMAGE_NAME={{cookiecutter.repo_name}}
CONTAINER_NAME={{cookiecutter.repo_name}}
DOCKERFILE_PATH=.

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
	@python3 -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

# Project initialization

.PHONY: setup-pre-commit  ## Installs pre-commit hooks
setup-pre-commit:
	uv run pre-commit install

.PHONY: env  ## Creates local environment and installs pre-commit hooks
env:
	uv sync --all-groups

.PHONY: init-project  ## Runs project initialization - to be used after cookiecutter initialization
init-project:
	make env
	make setup-pre-commit

# Helpers

.PHONY: format  ## Runs code formatting (ruff)
format:
	$(ruff-lint)
	$(ruff-format)

.PHONY: type-check  ## Runs type checking with mypy
type-check:
	uv run pre-commit run --all-files mypy

.PHONY: test  ## Runs pytest
test:
	uv run pytest -v tests/

.PHONY: testcov  ## Runs tests and generates coverage reports
testcov:
	@rm -rf htmlcov
	uv run pytest -v --cov-report html --cov-report xml --cov=src/{{cookiecutter.package_name}} tests/

.PHONY: mpc  ## Runs manual pre-commit stuff
mpc: format type-check test

.PHONY: docs  ## Build the documentation
docs:
	uv run mkdocs build

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
	rm -rf {{cookiecutter.package_name}}/*.so
	rm -rf .mypy_cache
	rm -rf .benchmark
	rm -rf .hypothesis
	rm -rf docs-site

# Dockerfile commands

.PHONY: docker-all  ## Docker default target
docker-all: docker-build docker-run

.PHONY: docker-build  ## Build Docker image - builds image and runs Docker container
docker-build:
	@echo "Building Docker image..."
	docker build -t $(IMAGE_NAME) $(DOCKERFILE_PATH)

.PHONY: docker-run  ## Run Docker container
docker-run:
	@echo "Running Docker container..."
	docker run -d --name $(CONTAINER_NAME) $(IMAGE_NAME)

.PHONY: docker-stop  ## Stop Docker container
docker-stop:
	@echo "Stopping Docker container..."
	docker stop $(CONTAINER_NAME)

.PHONY: docker-rm  ## Remove Docker container
docker-rm:
	@echo "Removing Docker container..."
	docker rm $(CONTAINER_NAME)

.PHONY: docker-rmi  ## Remove Docker image
docker-rmi:
	@echo "Removing Docker image..."
	docker rmi $(IMAGE_NAME)

.PHONY: docker-clean  ## Clean up everything (container and image)
docker-clean: docker-stop docker-rm docker-rmi

.PHONY: docker-rebuild  ## Rebuild and rerun Docker container
docker-rebuild: docker-clean docker-all
