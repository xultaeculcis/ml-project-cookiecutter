"""Copies README.md to index.md.

Also discovers all blocks and generates a list of them in the docs under
the Blocks Catalog heading.
"""

from __future__ import annotations

from pathlib import Path

import mkdocs_gen_files

readme_path = Path("README.md")
docs_index_path = Path("index.md")

with Path.open(readme_path) as readme:
    with mkdocs_gen_files.open(docs_index_path, "w") as generated_file:
        for line in readme:
            if line.startswith("Visit the full docs [here]("):
                continue  # prevent linking to itself
            generated_file.write(line)

    mkdocs_gen_files.set_edit_path(Path(docs_index_path), readme_path)
