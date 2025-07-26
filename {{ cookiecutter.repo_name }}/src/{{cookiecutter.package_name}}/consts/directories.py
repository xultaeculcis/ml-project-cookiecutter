"""Project directory related consts.

Attributes:
    ROOT_DIR (Path): Package root directory.
    SRC_DIR (Path): Package src directory.
    TESTS_DIR (Path): Package test directory.
    DATA_DIR (Path): Package data directory.

"""

from __future__ import annotations

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
SRC_DIR = ROOT_DIR / "src"
TESTS_DIR = ROOT_DIR / "tests"
DATA_DIR = ROOT_DIR / "data"
