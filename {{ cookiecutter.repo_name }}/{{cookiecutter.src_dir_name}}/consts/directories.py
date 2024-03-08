from __future__ import annotations

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
TESTS_DIR = ROOT_DIR / "tests"
DATA_DIR = ROOT_DIR / "data"
SRC_DIR = ROOT_DIR / "{{cookiecutter.src_dir_name}}"
