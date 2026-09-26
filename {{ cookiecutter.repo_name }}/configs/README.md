# `configs/`

The committed run configurations. Each config family has exactly one loader: the code that reads it in the CLI.
A family is a directory under `configs/`, or the file name without `.yaml` for a file directly in `configs/`.

- `train` (`train.yaml`): read by `{{cookiecutter.package_name}}.core.configs.TrainConfig`.
    Command: `{{cookiecutter.repo_name}} train --config configs/train.yaml`.
- `evaluate` (`evaluate.yaml`): read by `{{cookiecutter.package_name}}.core.configs.EvaluateConfig`.
    Command: `{{cookiecutter.repo_name}} evaluate --config configs/evaluate.yaml`.
- `predict` (`predict.yaml`): read by `{{cookiecutter.package_name}}.core.configs.PredictConfig`.
    Command: `{{cookiecutter.repo_name}} predict --config configs/predict.yaml`.
{%- if cookiecutter.ml_stack == "lightning" %}
- `lightning` (`lightning/*.yaml`): read by LightningCLI (`{{cookiecutter.package_name}}.lightning.cli.run`).
    Command: `{{cookiecutter.repo_name}} lightning fit --config configs/lightning/fit.yaml`.
{%- endif %}

## Rules

- The pydantic configs reject unknown keys. A typo fails at load time. It is not ignored.
- `tests/unit/test_configs.py` loads every `*.yaml` file here through the loader of its family. A file in a family
    that has no loader fails the test. When you add a family, add its loader to `CONFIG_LOADERS` in that test and
    add it to the list above.
- To add an experiment, add a file to an existing family, for example `configs/train/baseline.yaml` (family `train`).
- Keep secrets out of configs. Secrets go in `.env` and `{{cookiecutter.package_name}}.core.settings`.
{%- if cookiecutter.ml_stack == "lightning" %}
- For LightningCLI configs, `{{cookiecutter.repo_name}} lightning fit --print_config` shows every option with its
    default value.
{%- endif %}
