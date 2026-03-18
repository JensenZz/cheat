from importlib import import_module


def test_package_imports():
    module = import_module("auto_ops")
    assert module.__package__ == "auto_ops"
