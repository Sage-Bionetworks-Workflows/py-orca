from importlib import import_module

from orca.airflow.provider_info import generate_connection_type, get_provider_info
from orca.services.sevenbridges.hook import SevenBridgesHook


def test_generate_connection_type():
    result = generate_connection_type(SevenBridgesHook)
    module_name, class_name = result["hook-class-name"].rsplit(".", maxsplit=1)
    module = import_module(module_name)
    assert "connection-type" in result
    assert "hook-class-name" in result
    assert isinstance(result["connection-type"], str)
    assert getattr(module, class_name, None) is not None


def test_get_provider_info():
    result = get_provider_info()
    assert "package-name" in result
    assert "versions" in result
    assert "name" in result
    assert "description" in result
    assert "connection-types" in result
    assert len(result["connection-types"]) > 0
