import os

import jupytext
from jupyter_core.paths import jupyter_path

__all__ = [
    "convert_ipynb_to_py",
    "convert_py_to_ipynb",
    "convert_source_code_to_ipynb",
    "is_jupyter_kernel_installed",
]


def convert_ipynb_to_py(ipynb_file: str) -> str:
    notebook = jupytext.read(ipynb_file)
    py_contents = jupytext.writes(notebook, fmt="py:percent")
    return py_contents


def convert_py_to_ipynb(py_file: str) -> str:
    notebook = jupytext.read(py_file)
    ipynb_contents = jupytext.writes(notebook, fmt="ipynb")
    return ipynb_contents


def convert_source_code_to_ipynb(source_code: str) -> str:
    notebook = jupytext.reads(source_code, fmt="py:percent")
    ipynb_contents = jupytext.writes(notebook, fmt="ipynb")
    return ipynb_contents


def is_jupyter_kernel_installed(kernel_name):
    for kernel_dir in jupyter_path("kernels"):
        spec_file = os.path.join(kernel_dir, kernel_name, "kernel.json")
        if os.path.exists(spec_file):
            return True
    return False
