import nbformat
from nbconvert import PythonExporter

__all__ = ["convert_ipynb_to_py"]


def convert_ipynb_to_py(ipynb_file: str) -> str:
    with open(ipynb_file, "r", encoding="utf-8") as nb_file:
        nb_contents = nbformat.read(nb_file, as_version=4)
    exporter = PythonExporter()
    py_contents, _ = exporter.from_notebook_node(nb_contents)
    return py_contents
