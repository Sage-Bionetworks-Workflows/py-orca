from inspect import getmembers, isclass
from types import ModuleType

import pytest
from airflow.models.connection import Connection

from orca.services import base, nextflowtower, sevenbridges, synapse

SERVICES = {
    nextflowtower: "tower://:foo@api.tower.nf/?workspace=bar/baz",
    sevenbridges: "sbg://:foo@api.sbgenomics.com/v2/?project=bar/baz",
    synapse: "syn://:foo@",
}


def get_service_name(service_module: ModuleType) -> str:
    return service_module.__name__.split(".")[-1]


@pytest.fixture()
def services():
    yield [get_service_name(service) for service in SERVICES]


@pytest.fixture(params=SERVICES, ids=get_service_name)
def service(request, patch_os_environ):
    service_module = request.param
    service_classes = getmembers(service_module, isclass)
    service = dict()
    service["module"] = service_module
    service["connection_uri"] = SERVICES[service_module]
    for _, cls in service_classes:
        if issubclass(cls, base.BaseConfig):
            service["config"] = cls
        elif issubclass(cls, base.BaseClientFactory):
            service["client_factory"] = cls
        elif issubclass(cls, base.BaseOps):
            service["ops"] = cls
        elif issubclass(cls, base.BaseOrcaHook):
            service["hook"] = cls
    yield service


def create_config(config_cls, connection_uri):
    connection = Connection(uri=connection_uri)
    config = config_cls.from_connection(connection)
    return config


@pytest.fixture()
def config(service):
    config_cls = service["config"]
    connection_uri = service["connection_uri"]
    config = create_config(config_cls, connection_uri)
    yield config


@pytest.fixture()
def client_factory(service):
    config_cls = service["config"]
    connection_uri = service["connection_uri"]
    client_factory_cls = service["client_factory"]
    config = create_config(config_cls, connection_uri)
    yield client_factory_cls(config)


@pytest.fixture()
def ops(service):
    ops_cls = service["ops"]
    config_cls = service["config"]
    connection_uri = service["connection_uri"]
    config = create_config(config_cls, connection_uri)
    yield ops_cls(config)


@pytest.fixture()
def hook(service, mocker):
    hook_cls = service["hook"]
    connection_uri = service["connection_uri"]
    connection = Connection(uri=connection_uri)
    mocker.patch.object(hook_cls, "get_connection", connection)
    yield hook_cls()
