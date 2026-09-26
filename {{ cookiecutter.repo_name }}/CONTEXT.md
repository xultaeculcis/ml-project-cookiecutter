# CONTEXT

> The orientation document for this ML project. Agents and new team members read it first. Keep it short and correct.
> When a decision changes an entry here, update the entry in the same pull request.

## Problem

TODO: One paragraph. Describe the modeling task, the real-world decision that it supports, and the result that is
good enough to ship.

## Task framing

- Task type: TODO (classification, detection, segmentation, regression, forecasting, ...)
- Inputs: TODO
- Targets and labels: TODO (definition, and where the labeling rules are)
- Class and threshold definitions: TODO

## Data

- Datasets and their location: TODO
- Splits (train, validation, test) and how they are made: TODO
- Known risks of leakage, imbalance and drift: TODO

## Metric and target

- Primary metric: TODO (and the reason for this metric)
- Current baseline: TODO
- Target to beat: TODO
- Secondary metrics and constraints (latency, model size, ...): TODO

## Experiment tracking

- Tracker: MLflow. Local store: `sqlite:///mlflow.db` (`make mlflow-ui`). Shared server: TODO
- Run names and tags: TODO
- Current best run: TODO
- Results and analysis: `docs/dev-logs/`

## How to run

- Set up: `make init-project`
- Train: `uv run {{cookiecutter.repo_name}} train --config configs/train.yaml`
- Evaluate: `uv run {{cookiecutter.repo_name}} evaluate --config configs/evaluate.yaml`
- Predict: `uv run {{cookiecutter.repo_name}} predict --config configs/predict.yaml`
{%- if cookiecutter.ml_stack == "lightning" %}
- Train with LightningCLI: `uv run {{cookiecutter.repo_name}} lightning fit --config configs/lightning/fit.yaml`
{%- endif %}
- Tests: `make test`
- Lint and types: `make lint` and `make type-check`

## Decisions

The architecture decision records are in `docs/adr/`. The project terms and the label definitions are in
`docs/glossary.md`.
