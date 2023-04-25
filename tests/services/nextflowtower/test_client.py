import pytest
from requests.exceptions import HTTPError

from . import responses


def test_that_update_kwargs_updates_an_empty_dictionary(client):
    kwargs = {}
    client.update_kwarg(kwargs, "foo", "bar", 123)
    assert "foo" in kwargs
    assert "bar" in kwargs["foo"]
    assert kwargs["foo"]["bar"] == 123


def test_that_update_kwargs_updates_an_nonempty_dictionary(client):
    kwargs = {"foo": {"baz": 456}}
    client.update_kwarg(kwargs, "foo", "bar", 123)
    assert "bar" in kwargs["foo"]
    assert "baz" in kwargs["foo"]
    assert kwargs["foo"]["bar"] == 123


def test_that_update_kwargs_fails_with_a_nondictionary_under_first_key(client):
    kwargs = {"foo": 123}
    with pytest.raises(ValueError):
        client.update_kwarg(kwargs, "foo", "bar", 123)


def test_that_update_kwargs_fails_with_an_incompatible_type(client):
    kwargs = {"foo": {"bar": None}}
    with pytest.raises(ValueError):
        client.update_kwarg(kwargs, "foo", "bar", 123)


def test_that_get_user_info_works(client, mocker):
    mock = mocker.patch.object(client, "request_json")
    mock.return_value = responses.get_user_info
    response = client.get_user_info()
    mock.assert_called_once()
    assert response == responses.get_user_info["user"]


def test_that_get_user_info_fails_with_nonstandard_response(client, mocker):
    mock = mocker.patch.object(client, "request_json")
    mock.return_value = {"message": "foobar"}
    with pytest.raises(HTTPError):
        client.get_user_info()


def test_that_list_user_workspaces_works(client, mocker):
    mocker.patch.object(client, "get_user_info")
    mock = mocker.patch.object(client, "request_json")
    mock.return_value = responses.get_user_workspaces_and_orgs
    response = client.list_user_workspaces()
    mock.assert_called_once()
    assert len(response) == 2


def test_that_list_user_workspaces_fails_with_nonstandard_response(client, mocker):
    mocker.patch.object(client, "get_user_info")
    mock = mocker.patch.object(client, "request_json")
    mock.return_value = {"message": "foobar"}
    with pytest.raises(HTTPError):
        client.list_user_workspaces()
