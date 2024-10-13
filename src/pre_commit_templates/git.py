import subprocess
from pathlib import Path

__all__ = ["get_root"]

_ROOT_COMMAND: tuple[str, ...] = ("git", "rev-parse", "--show-toplevel")


def get_root() -> Path:
    """Gets the root of the current repository."""
    output = subprocess.check_output(_ROOT_COMMAND, text=True)
    return Path(output)
