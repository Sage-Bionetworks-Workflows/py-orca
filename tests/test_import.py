from importlib import import_module


def test_import():
    module = import_module("orca")
    assert module
