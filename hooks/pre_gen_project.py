"""Validate the cookiecutter context before the project is generated.

Cookiecutter renders this file with Jinja before it runs it. The context is rendered as JSON inside a raw string
(`load_context`), so quotes, backslashes and new lines in user values cannot break the Python syntax of this file.
"""

from __future__ import annotations

import json
import keyword
import re
import sys

REPO_NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
# GitHub user and organization names: letters, digits and hyphens, at most 39 characters.
GITHUB_USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")
# Free text goes into TOML basic strings, YAML and Dockerfile labels. These characters would need escaping there.
FORBIDDEN_TEXT_CHARS = {'"': "double quote", "\\": "backslash", "\n": "new line", "\r": "carriage return"}
FREE_TEXT_KEYS = ("project_name", "author_name", "project_description")
# The generated project depends on these packages. A package with the same name would shadow them.
SHADOWED_PACKAGE_NAMES = frozenset(
    {
        "azureml",
        "click",
        "dotenv",
        "jsonargparse",
        "lightning",
        "mlflow",
        "numpy",
        "pandas",
        "psutil",
        "pyarrow",
        "pydantic",
        "pydantic_settings",
        "pytest",
        "sklearn",
        "torch",
        "tqdm",
        "yaml",
    }
)


def load_context() -> dict[str, str]:
    """Return the rendered cookiecutter context.

    Returns:
        The cookiecutter context.

    """
    return json.loads(r"""{{ cookiecutter | jsonify }}""")  # type: ignore[no-any-return]


def validate_text(key: str, value: str) -> list[str]:
    """Return errors for free text that contains characters that need escaping in the generated files.

    Args:
        key: The context key, for the error message.
        value: The value.

    Returns:
        A list of error messages. The list is empty when the value is valid.

    """
    found = [name for char, name in FORBIDDEN_TEXT_CHARS.items() if char in value]
    if not found:
        return []
    return [
        f"{key} {value!r} contains a {', '.join(found)}. Remove it: {key} must not contain '\"', '\\' or new lines."
    ]


def validate(
    package_name: str,
    repo_name: str,
    github_username: str | None = None,
    repo_url: str | None = None,
    texts: dict[str, str] | None = None,
) -> list[str]:
    """Return a list of validation errors for the given values.

    Args:
        package_name: The Python package name.
        repo_name: The repository (directory) name.
        github_username: The GitHub user or organization. `None` skips the check.
        repo_url: The repository URL. `None` skips the check.
        texts: Free-text values (project name, author, description) by key. `None` skips the check.

    Returns:
        A list of error messages. The list is empty when all values are valid.

    """
    errors: list[str] = []
    if not package_name.isidentifier():
        errors.append(
            f"package_name {package_name!r} is not a valid Python identifier. "
            "Use only letters, digits and underscores, and do not start with a digit."
        )
    if keyword.iskeyword(package_name) or keyword.issoftkeyword(package_name):
        errors.append(f"package_name {package_name!r} is a Python keyword. Use a different name.")
    if package_name in SHADOWED_PACKAGE_NAMES or package_name in sys.stdlib_module_names:
        errors.append(
            f"package_name {package_name!r} is the name of a standard library module or of a dependency. "
            "Imports of that module would load your package. Use a different name."
        )
    if not REPO_NAME_PATTERN.match(repo_name):
        errors.append(
            f"repo_name {repo_name!r} is not valid. "
            "Use only lowercase letters, digits and hyphens, and start with a letter or a digit."
        )
    if github_username is not None and not GITHUB_USERNAME_PATTERN.match(github_username):
        errors.append(
            f"github_username {github_username!r} is not a valid GitHub user or organization name. "
            "Use 1 to 39 letters, digits or hyphens, and start with a letter or a digit."
        )
    if repo_url is not None and (not repo_url or any(char in repo_url for char in ('"', "\\", " ", "\n", "\r", "\t"))):
        errors.append(f"repo_url {repo_url!r} is not valid. It must not be empty or contain spaces, '\"' or '\\'.")
    for key, value in (texts or {}).items():
        errors.extend(validate_text(key, value))
    return errors


def main() -> None:
    """Validate the context and exit with status 1 if a value is not valid."""
    context = load_context()
    errors = validate(
        package_name=context["package_name"],
        repo_name=context["repo_name"],
        github_username=context["github_username"],
        repo_url=context["repo_url"],
        texts={key: context[key] for key in FREE_TEXT_KEYS},
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)  # noqa: T201
        sys.exit(1)


if __name__ == "__main__":
    main()
