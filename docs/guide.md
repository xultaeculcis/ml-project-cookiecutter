# Getting started

This guide tells you how to create a project from the template, what the project contains and how to keep it up to
date with the template.

## Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/). uv runs `cookiecutter` and `cruft` with `uvx`, so
    you do not install them. uv also installs the Python version of the project.
- `git`. Configure your identity (`git config --global user.name ...` and `git config --global user.email ...`).
    Without an identity, the template cannot make the initial commit. It then only stages the files.
- `make` and `bash`, for the `make` targets of the generated project. On Windows, use WSL.
- [Cookiecutter](https://cookiecutter.readthedocs.io/) 2.6 or newer. `uvx cookiecutter` gets the latest version.

## Create a project

Run:

```shell
uvx cookiecutter gh:xultaeculcis/ml-project-cookiecutter
```

Cookiecutter asks for each option. Push Enter to accept the default value. To create a project without questions,
give the values on the command line:

```shell
uvx cookiecutter gh:xultaeculcis/ml-project-cookiecutter --no-input \
    project_name="My ML project" ml_stack=lightning ci_provider=github
```

Before it generates the project, the template checks the names:

- `package_name` must be a valid Python identifier. It must not be a Python keyword, a standard library module
    (for example `logging`) or a dependency of the project (for example `mlflow`, `torch` or `yaml`).
- `repo_name` must contain only lowercase letters, digits and hyphens, and must start with a letter or a digit.
- `github_username` must be a valid GitHub user or organization name: 1 to 39 letters, digits or hyphens.
- `project_name`, `author_name` and `project_description` must not contain `"`, `\` or new lines. These values go
    into `pyproject.toml`, `mkdocs.yml` and the `Dockerfile`. Other characters, for example `:` or `'`, are fine.

If a name is not valid, cookiecutter stops and shows the error.

## Options

The first option in each list is the default.

| Option                 | Default                                            | Choices                                                                                       | Effect                                                                                                                                                                               |
| ---------------------- | -------------------------------------------------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `project_name`         | `project-name`                                     | Any text without `"`, `\`, or new lines                                                       | The project title in `README.md`, the docs and the package metadata.                                                                                                                 |
| `repo_name`            | `project_name`, slugified with `-`                 | Lowercase letters, digits, `-`                                                                | The directory name, the console script name and the Docker image name.                                                                                                               |
| `package_name`         | `project_name`, slugified with `_`                 | A Python identifier                                                                           | The package in `src/`.                                                                                                                                                               |
| `author_name`          | `xultaeculcis`                                     | Any text without `"`, `\`, or new lines                                                       | The author in `pyproject.toml`, `LICENSE` and the docs copyright.                                                                                                                    |
| `github_username`      | `author_name`, slugified, at most 39 characters    | A GitHub user or organization: letters, digits, `-`                                           | The owner in the default `repo_url`.                                                                                                                                                 |
| `repo_url`             | `https://github.com/<github_username>/<repo_name>` | A URL without spaces, `"` or `\`                                                              | The `origin` git remote, the package URLs and the docs repository link.                                                                                                              |
| `project_description`  | `A short description of the project`               | Any text without `"`, `\`, or new lines                                                       | The description in `README.md`, `pyproject.toml` and the docs.                                                                                                                       |
| `python_version`       | `3.13`                                             | `3.13`, `3.12`, `3.14`, `3.11`                                                                | `.python-version`, `requires-python`, the `ruff` target version and the Docker base image. With `3.14`, the modules do not use `from __future__ import annotations`.                 |
| `license`              | `MIT`                                              | `MIT`, `Apache 2.0`, `BSD-3-Clause`, `Beerware`, `GLWTS`, `Proprietary`, `Empty license file` | The `LICENSE` file and the SPDX `license` field. `Proprietary` adds the `Private :: Do Not Upload` classifier. `Empty license file` makes an empty `LICENSE` and no `license` field. |
| `ml_stack`             | `sklearn`                                          | `sklearn`, `torch`, `lightning`, `none`                                                       | The ML dependencies. See [ML stacks](#ml-stacks).                                                                                                                                    |
| `ci_provider`          | `github`                                           | `github`, `azure`, `none`                                                                     | `github`: `.github/workflows/pr.yaml` and `nightly.yaml`. `azure`: `.azure-pipelines/`. `none`: no CI pipeline.                                                                      |
| `dependabot`           | `yes`                                              | `yes`, `no`                                                                                   | `.github/dependabot.yaml` for GitHub Actions, `uv.lock` and (with `docker=yes`) the Docker base images. For repositories on GitHub only; kept with every `ci_provider`.              |
| `lock_update_workflow` | `yes`                                              | `yes`, `no`                                                                                   | `.github/workflows/lock-files-update.yaml`: a monthly `uv lock --upgrade` and `pre-commit autoupdate` pull request. For repositories on GitHub only; kept with every `ci_provider`.  |
| `zizmor`               | `pre-commit`                                       | `pre-commit`, `workflow-sarif`, `no`                                                          | `pre-commit`: a `zizmor` hook. `workflow-sarif`: `.github/workflows/zizmor-security-check.yaml`. `no`: no `zizmor` check.                                                            |
| `docker`               | `yes`                                              | `yes`, `no`                                                                                   | `Dockerfile`, `.dockerignore` and `mk/docker.mk`.                                                                                                                                    |
| `azure_ml`             | `no`                                               | `no`, `yes`                                                                                   | `aml/`, `.amlignore`, `mk/aml.mk`, `docs/guides/azure-ml.md` and the `azureml-mlflow` dependency.                                                                                    |
| `agent_docs`           | `yes`                                              | `yes`, `no`                                                                                   | `CLAUDE.md`, `CONTEXT.md`, `docs/glossary.md` and `docs/adr/`.                                                                                                                       |

### ML stacks

- `sklearn`: adds `scikit-learn`.
- `torch`: adds `torch` and `src/<package_name>/utils/torch.py` (`get_device`, `set_gpu_power_limit_if_needed`).
- `lightning`: adds `torch`, `lightning` and `jsonargparse[signatures]`. It also adds `src/<package_name>/lightning/`
    (a LightningCLI runner, an MLflow config callback, an example model and data module), `configs/lightning/fit.yaml`,
    the `lightning` CLI command and `docs/api_ref/lightning.md`.
- `none`: only the base dependencies (`numpy`, `pandas`, `mlflow`, `pydantic` and some others).

All stacks include MLflow, click, pydantic and pydantic-settings.

#### GPU and PyTorch wheels

With `torch` or `lightning`, uv installs `torch` on Linux from the PyTorch CUDA 13.0 index (`pytorch-cu130`). These
wheels need an NVIDIA driver version 580 or newer. On macOS and Windows, uv installs the default wheels from PyPI.
To use a different CUDA version, change the index in `pyproject.toml` of the generated project and run `make lock`.

The CUDA wheels of `torch` and its NVIDIA dependencies are several GB. Each CI job downloads them (or restores them
from the uv cache), which adds minutes to each run. The GitHub workflows of a `torch` or `lightning` project remove
preinstalled SDKs from the runner before `uv sync`, so the wheels fit on the disk. If no machine needs CUDA, change
the index URL to `https://download.pytorch.org/whl/cpu` and run `make lock`.

## Generated project

This is the project for the default options, with `project_name="My ML project"`. The comments show the files that
depend on an option.

```text
my-ml-project/
├── .github/                      <- ci_provider, dependabot, lock_update_workflow, zizmor
│   ├── dependabot.yaml           <- dependabot=yes
│   └── workflows/
│       ├── lock-files-update.yaml  <- lock_update_workflow=yes
│       ├── nightly.yaml          <- ci_provider=github
│       └── pr.yaml               <- ci_provider=github
├── configs/                      <- Run configs (YAML), validated by pydantic models.
│   ├── README.md
│   ├── evaluate.yaml
│   ├── predict.yaml
│   └── train.yaml
├── data/                         <- Local data. Git ignores the content, except the .gitkeep files.
│   ├── analysis/
│   ├── auxiliary/
│   ├── inference/
│   ├── interim/
│   ├── processed/
│   └── raw/
├── docs/                         <- MkDocs documentation.
│   ├── adr/                      <- agent_docs=yes
│   ├── api_ref/                  <- API reference (mkdocstrings).
│   ├── dev-logs/
│   │   └── log.md
│   ├── glossary.md               <- agent_docs=yes
│   ├── guides/                   <- Setup, Makefile, tests, CLI, configs, experiment tracking, CI, contributing.
│   └── index.md
├── mk/
│   └── docker.mk                 <- docker=yes
├── notebooks/
├── src/
│   └── my_ml_project/
│       ├── __init__.py
│       ├── __main__.py           <- `python -m my_ml_project`
│       ├── py.typed
│       ├── cli/
│       │   └── entrypoint.py     <- The click CLI: train, evaluate, predict.
│       ├── consts/               <- Directories, seed, MLflow defaults and other constants.
│       ├── core/
│       │   ├── configs.py        <- Pydantic models for the run configs.
│       │   └── settings.py       <- Lazy settings from the environment and .env.
│       └── utils/                <- Logging, MLflow, seed and JSON serialization helpers.
├── tests/
│   ├── conftest.py               <- Markers from the directory, network block for unit tests.
│   ├── e2e/
│   ├── integration/
│   └── unit/
├── .dockerignore                 <- docker=yes
├── .env-sample                   <- Copy it to .env.
├── .gitignore
├── .pre-commit-config.yaml
├── .python-version
├── CLAUDE.md                     <- agent_docs=yes
├── CONTEXT.md                    <- agent_docs=yes
├── Dockerfile                    <- docker=yes
├── LICENSE
├── Makefile
├── README.md
├── mkdocs.yml
└── pyproject.toml
```

Other options add these files:

- `ci_provider=azure`: `.azure-pipelines/` (`pr-pipeline.yaml`, `jobs/`, `steps/`).
- `zizmor=workflow-sarif`: `.github/workflows/zizmor-security-check.yaml`.
- `azure_ml=yes`: `aml/`, `.amlignore`, `mk/aml.mk` and `docs/guides/azure-ml.md`.
- `ml_stack=torch` or `ml_stack=lightning`: `src/<package_name>/utils/torch.py` and its test.
- `ml_stack=lightning`: `src/<package_name>/lightning/`, `tests/unit/lightning/`, `configs/lightning/` and
    `docs/api_ref/lightning.md`.

If no file is left in `.github/` or `mk/`, the template removes the directory.

## What the template does after generation

1. It removes the files of the options that you did not select.
2. It runs `git init` with the `main` branch.
3. It adds the `origin` remote with the `repo_url` value.
4. It stages all files and makes the `Initial commit` commit. If your git identity is not configured, it shows a
    warning and leaves the files staged. The project is not deleted.
5. It shows the next steps.

## Next steps

1. Go to the project directory:

    ```shell
    cd my-ml-project
    ```

2. Create the environment, create `uv.lock` and install the `pre-commit` hooks:

    ```shell
    make init-project
    ```

3. Commit the lock file:

    ```shell
    git add uv.lock
    git commit -m "Add uv.lock"
    ```

4. Copy `.env-sample` to `.env` and set the values:

    ```shell
    cp .env-sample .env
    ```

5. Run the checks:

    ```shell
    make pc
    make test
    ```

6. Create the remote repository (the `repo_url` value) and push:

    ```shell
    git push -u origin main
    ```

7. Read the guides of the project: run `make docs-serve` and open <http://127.0.0.1:8000>.

To see all `make` targets, run `make help`.

## CI setup notes

### GitHub Actions

- `pr.yaml` runs the `pre-commit` hooks and the tests on each pull request to `main`. `nightly.yaml` runs all hooks
    and all tests except `gpu` tests every day at 03:00 UTC.
- The monthly lock file update workflow opens a pull request. In the repository settings, go to "Actions",
    "General", "Workflow permissions" and select "Allow GitHub Actions to create and approve pull requests".
- A pull request that the default `GITHUB_TOKEN` opens does not start other workflows. To run the CI checks on the
    lock file update pull request, create the `LOCK_UPDATE_TOKEN` repository secret: a fine-grained personal access
    token (contents and pull requests: read and write) or a GitHub App token.
- The lock file update workflow does not request a reviewer. GitHub rejects a review request (HTTP 422) when the
    reviewer owns the token that opens the pull request, or is an organization. The workflow file has a commented
    `reviewers` example.
- `dependabot.yaml` and the lock file update workflow work only on GitHub. They are also generated with
    `ci_provider=azure` or `none`, because a repository on GitHub can use Azure Pipelines. Delete them if the
    repository is not on GitHub.

### zizmor

- `zizmor=pre-commit`: the `zizmor` `pre-commit` hook checks the workflows when a file in `.github/` changes. It works
    on private repositories.
- `zizmor=workflow-sarif`: a workflow uploads the results to GitHub code scanning as SARIF. On a private repository,
    code scanning needs GitHub Advanced Security (GitHub Code Security). Without it, the upload step fails.
- `zizmor=no`: no `zizmor` check.

### Azure Pipelines

- Create a pipeline in Azure DevOps from `.azure-pipelines/pr-pipeline.yaml`. For Azure Repos, add a build validation
    branch policy on `main`, because Azure Repos ignores the `pr:` trigger in YAML.
- The `uvVersion` parameter in `.azure-pipelines/steps/uv-env-create.yaml` pins the uv version. Change it when the
    team changes the uv version.
- The `env` pipeline parameter (`dev`, `staging` or `prod`) becomes the `ENVIRONMENT` variable of the tests.

### Docker

- The image uses `python:<python_version>-slim-trixie` and a pinned `ghcr.io/astral-sh/uv` image. The runtime stage
    has only the runtime dependencies, `src/` and `configs/`, and runs as the non-root user `app`.
- The build needs `uv.lock`. Run `make init-project` (or `uv lock`) before `make docker-build`.
- With `dependabot=yes`, Dependabot proposes patch updates of the base image. Change the Python minor version by hand.

## Keep a project up to date with the template

[cruft](https://cruft.github.io/cruft/) records the template commit that a project uses. It can then apply the later
changes of the template to the project.

### Create a project with cruft

1. Create the project:

    ```shell
    uvx cruft create https://github.com/xultaeculcis/ml-project-cookiecutter
    ```

2. Commit `.cruft.json`. The template makes the initial commit before cruft writes `.cruft.json`, so you must commit
    it yourself:

    ```shell
    cd my-ml-project
    git add .cruft.json
    git commit -m "Add cruft state"
    ```

### Link an existing project

If you created the project with `cookiecutter`, link it to the template:

```shell
uvx cruft link https://github.com/xultaeculcis/ml-project-cookiecutter
```

Enter the same values that you used when you created the project. Then commit `.cruft.json`.

### Update a project

1. Check if the project uses the latest template:

    ```shell
    uvx cruft check
    ```

2. Make sure that the working tree has no uncommitted changes.

3. Apply the template changes:

    ```shell
    uvx cruft update
    ```

4. Examine the changes. If a change does not apply, cruft writes a `.rej` file. Merge these changes by hand and
    remove the `.rej` files.

5. Run `make env`, `make pc` and `make test`. Then commit the changes and `.cruft.json`.

`cruft` uses only the files that are committed in the template repository.

Keep `[tool.cruft] skip = [".git"]` in `pyproject.toml`. The post-generation hook runs `git init` also in the
temporary copies that `cruft update` generates, and without this setting the update fails with
`ChangesetUnicodeError`. Add other paths to `skip` that `cruft update` must not change.
