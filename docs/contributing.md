# Contributing

Project structure and tool usage is highly opinionated within this project. As the times change, so do the best
practices. I will try to keep the project up to date with the latest tools and practices.

The goal of this project is to make it easier to start, structure, reproduce, maintain and later deploy
an ML project. The stuff in it is based on my own experiences and might not suit your needs. If you think something
should be done differently, feel free to create an issue or fork the repo for your own usage. It's an MIT license,
so you can do whatever the hell you want with it.

Creating pull requests and filing issues is welcome. I'd love to hear what works for you and what does not.
Although I cannot promise to not close them if I disagree with you.

## Work on the template

### Set up the environment

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/), `git` and `make`.

2. Create the environment and install the `pre-commit` hooks:

    ```shell
    make env
    ```

3. Run `make help` to see all targets.

### Repository layout

- `cookiecutter.json`: the options and their prompts.
- `hooks/pre_gen_project.py`: checks `package_name` and `repo_name` before generation.
- `hooks/post_gen_project.py`: removes the files of the options that are not selected (the `REMOVAL_TABLE` list),
    runs `git init` and makes the initial commit.
- `{{ cookiecutter.repo_name }}/`: the template of the generated project.
- `tests/`: the tests of the template.
- `docs/`: this documentation.
- `.github/workflows/`: the CI of the template.
- `.github/scripts/update_template_deps.py`: updates the tool versions inside the template.

### Rules for template files

- The template files contain Jinja. For small differences between options, use
    `{% if cookiecutter.<option> == "..." %}` in the file.
- When an option adds or removes whole files or directories, create the files in the template and add their paths to
    `REMOVAL_TABLE` in `hooks/post_gen_project.py`. Add the paths to the tests in `tests/test_options.py`.
- Wrap GitHub Actions and Azure Pipelines expressions (`${{ ... }}`) in
    `{% raw %}...{% endraw %}`.
- The generated project must pass `make pc` on the first run. Rendered Markdown must not change when `mdformat`
    formats it.

### Run the tests

- `make test`: the fast tests. They generate projects and check the files. They do not install dependencies.
- `make test-all`: all tests, including the `slow` tests. The slow tests run `make init-project`, `make pc`,
    `make docs` and `make test` in generated projects, and test `cruft create`. They need network access and take
    several minutes.
- `make pc`: the `pre-commit` hooks of the template repository.
- `make docs`: build this documentation.

### Template CI

The `project-creation-checks` workflow runs on each push to `main` and on each pull request to `main`:

- The `project-checks` job generates projects for Python 3.11, 3.12, 3.13 and 3.14, each with 4 option sets:
    `default`, `lightning-azure-nodocker`, `torch-azureml-noagentdocs` and `nostack-noci-zizmorsarif`. In each project
    it runs `make init-project`, `make pc`, `make docs` and `make test`.
- The `docker-build` job builds the Docker image of the default project for each Python version.

The `pr` workflow runs the `pre-commit` hooks and the fast tests of the template repository.

### Template dependency updates

Dependabot cannot read the files in the template directory, because they contain Jinja. The `template-deps-update`
workflow updates them instead. It runs on the first day of each month at 06:00 UTC, and you can start it by hand.

1. It generates a project and runs `pre-commit autoupdate` in it.
2. It copies the new hook revisions and the matching `ruff==` pin back to the template.
3. It runs `gha-update` on the template workflows.
4. It opens a pull request.

A pull request that the default `GITHUB_TOKEN` opens does not start the CI checks. To run the checks, create the
`TEMPLATE_DEPS_UPDATE_TOKEN` repository secret: a fine-grained personal access token with read and write access to
contents and pull requests.

To run the update locally:

```shell
uv run python .github/scripts/update_template_deps.py
```

Dependabot updates the root `uv.lock` and the root GitHub Actions. To update the root GitHub Actions by hand, run
`make gha-update`.
