from __future__ import annotations

import re
from pathlib import Path


def replace_placeholders(file_path: Path) -> None:
    content = file_path.read_text()
    placeholders = re.findall(r"<<([A-Za-z.\-_ ]+)>>", content)

    for placeholder in placeholders:
        # Don't use f-strings otherwise Jinja will throw error
        replacement = "{" + "{" + placeholder + "}" + "}"
        content = content.replace(f"<<{placeholder}>>", replacement)

    file_path.write_text(content)


def main() -> None:
    replace_placeholders(Path.cwd() / ".env-sample")
    replace_placeholders(Path.cwd() / ".azure-pipelines/pr-pipeline.yaml")
    replace_placeholders(Path.cwd() / ".azure-pipelines/jobs/test-suite.yaml")
    replace_placeholders(Path.cwd() / ".azure-pipelines/steps/conda-env-create.yaml")
    replace_placeholders(Path.cwd() / ".azure-pipelines/steps/test-suite.yaml")


if __name__ == "__main__":
    main()
