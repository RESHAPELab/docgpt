import sys
from pathlib import Path

_SRC_PATH = Path(__file__).parents[1].joinpath("src")

sys.path.append(_SRC_PATH.as_posix())
