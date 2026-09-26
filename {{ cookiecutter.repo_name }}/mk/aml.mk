# Azure ML targets. Included by the main Makefile (`-include mk/*.mk`).
#
# Needs the Azure CLI with the `ml` extension (`az extension add -n ml`) and an `az login` session.
# Set the workspace on the command line or in the environment:
#   make aml-pipeline-run AML_WORKSPACE=my-workspace AML_RESOURCE_GROUP=my-resource-group

AML_WORKSPACE ?=
AML_RESOURCE_GROUP ?=
AML_DIR ?= aml
AML_ENV_FILE ?= $(AML_DIR)/environments/env.yaml
AML_COMPUTE_FILE ?= $(AML_DIR)/compute/cpu-cluster.yaml
AML_COMPONENT_FILE ?= $(AML_DIR)/components/train.yaml
AML_PIPELINE_FILE ?= $(AML_DIR)/pipelines/train-pipeline.yaml
# Extra arguments for `az ml job create`, e.g. AML_JOB_ARGS="--stream".
AML_JOB_ARGS ?=
AML_WS_ARGS = --workspace-name "$(AML_WORKSPACE)" --resource-group "$(AML_RESOURCE_GROUP)"

.PHONY: aml-login-check  ## Checks the Azure login, the az ml extension, AML_WORKSPACE and AML_RESOURCE_GROUP
aml-login-check:
	@test -n "$(AML_WORKSPACE)" || { echo "Set AML_WORKSPACE, e.g. make $@ AML_WORKSPACE=my-workspace"; exit 2; }
	@test -n "$(AML_RESOURCE_GROUP)" || { echo "Set AML_RESOURCE_GROUP, e.g. make $@ AML_RESOURCE_GROUP=my-rg"; exit 2; }
	@az extension show --name ml --output none 2>/dev/null || { echo "Install the extension: az extension add -n ml"; exit 2; }
	@az account show --query "{subscription: name, user: user.name}" --output table || { echo "Run: az login"; exit 2; }

.PHONY: aml-check-definitions  ## Checks that every YAML file under aml/ parses
aml-check-definitions:
	@uv run python -c 'import pathlib, yaml; files = sorted(pathlib.Path("$(AML_DIR)").rglob("*.y*ml")); [yaml.safe_load(f.read_text(encoding="utf-8")) for f in files]; print(f"{len(files)} Azure ML definitions parse.")'

.PHONY: aml-compute-create  ## Creates or updates the compute cluster (AML_COMPUTE_FILE)
aml-compute-create: aml-login-check
	az ml compute create --file $(AML_COMPUTE_FILE) $(AML_WS_ARGS)

.PHONY: aml-env-create  ## Creates a new version of the training environment (AML_ENV_FILE)
aml-env-create: aml-login-check
	az ml environment create --file $(AML_ENV_FILE) $(AML_WS_ARGS)

.PHONY: aml-component-create  ## Registers a new version of the training component (AML_COMPONENT_FILE)
aml-component-create: aml-login-check
	az ml component create --file $(AML_COMPONENT_FILE) $(AML_WS_ARGS)

.PHONY: aml-pipeline-run  ## Submits the training pipeline (AML_PIPELINE_FILE)
aml-pipeline-run: aml-login-check aml-check-definitions
	az ml job create --file $(AML_PIPELINE_FILE) $(AML_WS_ARGS) $(AML_JOB_ARGS)
