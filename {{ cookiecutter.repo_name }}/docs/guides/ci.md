# CI and automation

This page describes the CI pipelines and the automated updates of this project, and the setup that each one needs.
{%- if cookiecutter.ci_provider == "github" %}

## GitHub Actions

### Pull request checks (`.github/workflows/pr.yaml`)

The workflow runs on each pull request to `main`. You can also start it by hand (`workflow_dispatch`). A new push to
the same pull request cancels the previous run.

- The `code-quality` job runs all `pre-commit` hooks except `pytest-check`.
- The `tests` job runs `pytest -m "not slow and not gpu" -n auto` with coverage. It writes a coverage summary to the
    job summary and uploads `junit.xml` and `coverage.xml` as the `test-results` artifact.

Both jobs run `uv sync --locked --all-groups`. The jobs fail if `uv.lock` does not match `pyproject.toml`. Run
`make lock` and commit `uv.lock` to fix this.

### Nightly checks (`.github/workflows/nightly.yaml`)

The workflow runs every day at 03:00 UTC. It runs all `pre-commit` hooks except `pytest-check`, and all tests except
the `gpu` tests. It includes the `slow` tests.

To require the checks before a merge, add a branch protection rule (or a ruleset) for `main` and select the
`Code quality (pre-commit)` and `Tests` checks.
{%- if cookiecutter.ml_stack in ["torch", "lightning"] %}

### CUDA wheels in CI

On Linux, `uv sync` installs `torch` from the PyTorch CUDA index. The `torch` wheel and its NVIDIA dependencies are
several GB. Each job downloads them (or restores them from the uv cache), which adds minutes to each run and uses a
large part of the 10 GB GitHub Actions cache limit. Before `uv sync`, each job runs a "Free disk space" step that
removes preinstalled SDKs (.NET, Android, GHC, CodeQL), so the wheels fit on the runner disk.

The unit tests do not need a GPU. If no machine of the project needs CUDA, change the `pytorch-cu130` index URL in
`pyproject.toml` to the CPU index (`https://download.pytorch.org/whl/cpu`) and run `make lock`. The CPU wheels are
much smaller. This also changes local installs, because CI installs from the same `uv.lock`.
{%- endif %}
{%- elif cookiecutter.ci_provider == "azure" %}

## Azure Pipelines

The pipeline definition is `.azure-pipelines/pr-pipeline.yaml`. It runs on pull requests to `main` and has two
stages that run in parallel:

- `pre_commit` runs all `pre-commit` hooks except `pytest-check`.
- `tests` runs `pytest -m "not slow and not gpu" -n auto` with coverage. It publishes the JUnit test results and the
    Cobertura coverage report to the pipeline run.

Both stages run `uv sync --locked --all-groups`. The stages fail if `uv.lock` does not match `pyproject.toml`. Run
`make lock` and commit `uv.lock` to fix this. The pipeline caches the uv packages and the `pre-commit` environments
with `Cache@2`.

### Setup

1. In Azure DevOps, create a pipeline from the existing YAML file `.azure-pipelines/pr-pipeline.yaml`.
2. If the code is in Azure Repos, the `pr:` trigger in YAML has no effect. Add a build validation policy to the `main`
    branch that runs this pipeline.
3. If the code is on GitHub, the `pr:` trigger works. Install the Azure Pipelines GitHub app for the repository.

### Parameters

- `env` (`dev`, `staging` or `prod`, default `dev`): the pipeline sets it as the `ENVIRONMENT` variable for the tests.
- `uvVersion` (in `.azure-pipelines/steps/uv-env-create.yaml`): the pinned uv version that the pipeline installs.
    Change it when you change the uv version that the team uses.
{%- if cookiecutter.ml_stack in ["torch", "lightning"] %}

### CUDA wheels in CI

On Linux, `uv sync` installs `torch` from the PyTorch CUDA index. The `torch` wheel and its NVIDIA dependencies are
several GB. Each stage downloads them (or restores them from the cache), which adds minutes to each run. Microsoft-hosted
agents have limited free disk space. If a stage fails with "No space left on device", use a self-hosted agent or
remove unused SDKs before `uv sync`.
{%- endif %}
{%- else %}

## CI pipelines

The project has no CI pipeline. To add one, generate a new project from the template with `ci_provider=github` or
`ci_provider=azure`, and copy the pipeline files. Before you open a pull request, run the checks locally:

```shell
make pc
make test
```
{%- endif %}
{%- if cookiecutter.ci_provider != "github" and (cookiecutter.dependabot == "yes" or cookiecutter.lock_update_workflow == "yes") %}

## GitHub-only files

These files work only when the repository is on GitHub. If the repository is not on GitHub (for example on Azure
Repos), delete them. A repository on GitHub can use them with {% if cookiecutter.ci_provider == "azure" %}Azure Pipelines{% else %}any CI{% endif %}.
{% if cookiecutter.dependabot == "yes" %}
- `.github/dependabot.yaml`
{%- endif %}
{%- if cookiecutter.lock_update_workflow == "yes" %}
- `.github/workflows/lock-files-update.yaml`
{%- endif %}
{%- endif %}
{%- if cookiecutter.dependabot == "yes" %}

## Dependabot (`.github/dependabot.yaml`)

Dependabot opens update pull requests every week for:

- GitHub Actions.
- Python dependencies in `uv.lock`.
{%- if cookiecutter.docker == "yes" %}
- Docker base images in `Dockerfile`. Dependabot does not propose major or minor updates of the `python` image,
    because the Python version must match `.python-version` and `requires-python`. Change it by hand.
{%- endif %}

Minor and patch updates are grouped into one pull request per ecosystem. Dependabot waits 7 days after a release
before it proposes the release. This lowers the risk of a compromised release.

Dependabot works only for repositories on GitHub.
{%- endif %}
{%- if cookiecutter.lock_update_workflow == "yes" %}

## Monthly lock file update (`.github/workflows/lock-files-update.yaml`)

The workflow runs on the first day of each month at 00:00 UTC. You can also start it by hand. It does these steps:

1. It runs `pre-commit autoupdate` to update the hook revisions.
2. It sets the `ruff` pin in the `dev` group to the version of the `ruff` `pre-commit` hook.
3. It runs `uv lock --upgrade`.
4. It opens a pull request from the `chore/lock-files-update` branch with the `dependencies` label.

The workflow does not request a reviewer. GitHub rejects a review request (HTTP 422) when the reviewer is the owner of
the token that opens the pull request, or is an organization. To request a review, set `reviewers` (a user who does
not own `LOCK_UPDATE_TOKEN`) or `team-reviewers` in the `Create a pull request` step. The workflow file has a
commented example.

Setup:

1. In the repository settings, go to "Actions", "General", "Workflow permissions". Select "Allow GitHub Actions to
    create and approve pull requests".
2. Optional: create the `LOCK_UPDATE_TOKEN` repository secret. A pull request that the default `GITHUB_TOKEN` opens
    does not start other workflows, so the CI checks do not run on it. Use a fine-grained personal access token
    (contents: read and write, pull requests: read and write) or a GitHub App token. Without the secret, close and
    reopen the pull request to start the checks.
{%- endif %}
{%- if cookiecutter.zizmor == "pre-commit" %}

## Workflow security checks (zizmor)

The `zizmor` `pre-commit` hook checks the GitHub Actions workflows for security problems. It runs when a file under
`.github/` changes. It works on private repositories and needs no setup.
{%- elif cookiecutter.zizmor == "workflow-sarif" %}

## Workflow security checks (`.github/workflows/zizmor-security-check.yaml`)

The workflow runs [zizmor](https://docs.zizmor.sh) on each push to `main` and on each pull request. It uploads the
results as SARIF to GitHub code scanning. You see the findings in the "Security" tab.

Code scanning on a private repository needs GitHub Advanced Security (GitHub Code Security). Without it, the upload
step fails. For a private repository without it, use the `zizmor` `pre-commit` hook instead: generate a project with
`zizmor=pre-commit` and copy the hook from `.pre-commit-config.yaml`.
{%- endif %}
{%- if cookiecutter.docker == "yes" %}

## Docker image

The `Dockerfile` builds a multi-stage image:

- The `builder` stage uses a pinned uv image and `python:{{ cookiecutter.python_version }}-slim-trixie`. It installs
    the locked runtime dependencies without the dev groups (`uv sync --locked --no-dev`). The dependencies are in a
    separate layer, so a code change does not install them again.
- The `runtime` stage copies the virtual environment, `src/` and `configs/`. It runs as the non-root user `app`. The
    default command is `{{ cookiecutter.repo_name }} --help`.

`.dockerignore` keeps `.env`, data, tests, docs and caches out of the build context. The build needs `uv.lock`.

The CI pipelines do not build the image. To build and run it locally, read
[Using Makefile commands](makefile-usage.md).
{%- endif %}

## Secrets

{%- if cookiecutter.lock_update_workflow == "yes" %}

- `LOCK_UPDATE_TOKEN` (optional, GitHub repository secret): the token for the monthly lock file update pull
    request. Read "Monthly lock file update" above.
{%- else %}

The CI pipelines need no secrets.
{%- endif %}

Do not put secrets in the pipeline files or in `configs/`. Use the secret store of the CI provider.
