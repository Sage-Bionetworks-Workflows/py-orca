from unittest.mock import MagicMock

import pytest
from sevenbridges.http.error_handlers import maintenance_sleeper, rate_limit_sleeper

from orca.services.sevenbridges import client
from orca.services.sevenbridges.client import init_client


def test_for_an_error_when_using_unrecognized_api_endpoints():
    with pytest.raises(ValueError):
        init_client("foo", "bar")
    with pytest.raises(ValueError):
        init_client("https://foo.sbgenomics.com/v2", "bar")
    with pytest.raises(ValueError):
        init_client("https://api.sbgenomics.com/v1", "bar")


def test_for_an_error_when_using_invalid_authentication_token():
    with pytest.raises(ValueError):
        init_client("https://api.sbgenomics.com/v2", 123)  # type: ignore
    with pytest.raises(ValueError):
        init_client("https://api.sbgenomics.com/v2", "")


def test_that_the_default_error_handlers_are_used(mocker):
    mock: MagicMock
    mock = mocker.patch.object(client, "Api", autospec=True)
    init_client("https://api.sbgenomics.com/v2", "foo")
    _, kwargs = mock.call_args
    assert "error_handlers" in kwargs
    handlers = kwargs["error_handlers"]
    assert maintenance_sleeper in handlers
    assert rate_limit_sleeper in handlers
