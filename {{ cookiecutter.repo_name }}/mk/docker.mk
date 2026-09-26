# Docker targets. Included by the main Makefile (`-include mk/*.mk`).

IMAGE_NAME ?= {{cookiecutter.repo_name}}
IMAGE_TAG ?= latest
DOCKERFILE ?= Dockerfile
DOCKER_CONTEXT ?= .
# Arguments passed to the container command, e.g. `make docker-run ARGS="train --config configs/train.yaml"`.
ARGS ?=
# Use the local .env file when it exists.
DOCKER_ENV_FILE := $(if $(wildcard .env),--env-file .env,)
# `-t` needs a terminal. Use it only when stdin is a TTY, so the targets also work in CI and in pipes.
DOCKER_TTY := $(shell [ -t 0 ] && echo -it || echo -i)

.PHONY: docker-build  ## Builds the Docker image
docker-build:
	docker build -f $(DOCKERFILE) -t $(IMAGE_NAME):$(IMAGE_TAG) $(DOCKER_CONTEXT)

.PHONY: docker-run  ## Runs the project CLI in a container (pass CLI arguments with ARGS="...")
docker-run:
	docker run --rm $(DOCKER_TTY) $(DOCKER_ENV_FILE) $(IMAGE_NAME):$(IMAGE_TAG) $(if $(ARGS),{{cookiecutter.repo_name}} $(ARGS),)

.PHONY: docker-shell  ## Starts a bash shell in a container
docker-shell:
	docker run --rm $(DOCKER_TTY) $(DOCKER_ENV_FILE) --entrypoint bash $(IMAGE_NAME):$(IMAGE_TAG)

.PHONY: docker-clean  ## Removes the Docker image
docker-clean:
	-docker image rm $(IMAGE_NAME):$(IMAGE_TAG)
