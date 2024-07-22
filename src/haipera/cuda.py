import subprocess
import re
from typing import Optional, Tuple

__all__ = ["get_cuda_version"]


def get_cuda_version() -> Optional[Tuple[int, int]]:
    try:
        output = subprocess.check_output(["nvcc", "--version"]).decode("utf-8")
        version = re.search(r"release (\S+),", output)
        if version:
            version = version.group(1)
            major, minor = version.split(".")
            return int(major), int(minor)
    except Exception:
        return None
