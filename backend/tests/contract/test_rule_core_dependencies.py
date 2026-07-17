from importlib import import_module

import pytest


@pytest.mark.parametrize(
    "module_name",
    [
        "fitz",
        "docx",
        "pptx",
        "PIL",
        "numpy",
        "rapidocr_onnxruntime",
        "httpx",
        "networkx",
    ],
)
def test_rule_core_dependency_can_be_imported(module_name: str) -> None:
    import_module(module_name)
