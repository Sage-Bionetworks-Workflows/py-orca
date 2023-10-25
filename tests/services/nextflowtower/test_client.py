import pytest
from requests.exceptions import HTTPError

from orca.services.nextflowtower import models


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


def test_that_get_user_info_works(client, mocker, get_response):
    expected = get_response("get_user_info")
    mock = mocker.patch.object(client, "request_json")
    mock.return_value = expected
    actual = client.get_user_info()
    mock.assert_called_once()
    assert actual == models.User.from_json(expected["user"])


def test_that_get_user_info_fails_with_400_response(client, mocker):
    mock = mocker.patch.object(client, "request_json")
    mock.return_value = {"message": "foobar"}
    with pytest.raises(HTTPError):
        client.get_user_info()


def test_that_list_user_workspaces_works(client, mocker, get_response):
    mocker.patch.object(client, "get_user_info")
    mock = mocker.patch.object(client, "request_json")
    mock.return_value = get_response("get_user_workspaces_and_orgs")
    response = client.list_user_workspaces()
    mock.assert_called_once()
    assert len(response) == 2


def test_that_list_user_workspaces_fails_with_nonstandard_response(client, mocker):
    mocker.patch.object(client, "get_user_info")
    mock = mocker.patch.object(client, "request_json")
    mock.return_value = {"message": "foobar"}
    with pytest.raises(HTTPError):
        client.list_user_workspaces()


def test_that_get_compute_env_works(client, mocker, get_response):
    mock = mocker.patch.object(client, "request_json")
    mock.return_value = get_response("get_compute_env")
    response = client.get_compute_env("5ykJF", 98765)
    mock.assert_called_once()
    assert response.id == "5ykJF"


def test_that_list_compute_envs_works(client, mocker, get_response):
    mock = mocker.patch.object(client, "request_json")
    mock.return_value = get_response("list_compute_envs")
    response = client.list_compute_envs(98765)
    mock.assert_called_once()
    assert len(response) == 3


def test_that_list_compute_envs_works_with_status_filter(client, mocker, get_response):
    mock = mocker.patch.object(client, "request_json")
    mock.return_value = get_response("list_compute_envs")
    response = client.list_compute_envs(98765, "AVAILABLE")
    mock.assert_called_once()
    assert len(response) == 3


def test_that_create_label_works(client, mocker, get_response):
    mock = mocker.patch.object(client, "request_json")
    mock.return_value = get_response("create_label")
    response = client.create_label("foo", 98765)
    mock.assert_called_once()
    assert response.id == 12345


def test_that_list_labels_works(client, mocker, get_response):
    full_response = get_response("list_labels")
    page_1 = {"totalSize": 5, "labels": full_response["labels"][:3]}
    page_2 = {"totalSize": 5, "labels": full_response["labels"][3:]}
    mock = mocker.patch.object(client, "request_json")
    mock.side_effect = [page_1, page_1, page_2]  # First request is repeated
    actual = client.list_labels(98765)
    expected = [models.Label.from_json(item) for item in full_response["labels"]]
    assert mock.call_count == 3
    assert actual == expected


def test_for_an_error_when_total_size_doesnt_match_items(client, mocker, get_response):
    full_response = get_response("list_labels")
    page_1 = {"totalSize": 4, "labels": full_response["labels"][:3]}
    page_2 = {"totalSize": 4, "labels": full_response["labels"][3:]}
    mock = mocker.patch.object(client, "request_json")
    mock.side_effect = [page_1, page_1, page_2]  # First request is repeated
    with pytest.raises(HTTPError):
        client.list_labels(98765)


def test_that_launch_workflow_works(client, mocker, get_response):
    mock = mocker.patch.object(client, "request_json")
    mock.return_value = get_response("launch_workflow")
    launch_spec = models.LaunchInfo(
        compute_env_id="foo",
        pipeline="bar",
        run_name="foobar",
        work_dir="s3://path",
        profiles=["test"],
    )
    client.launch_workflow(launch_spec)
    mock.assert_called_once()


def test_that_get_workflow_returns_expected_response(client, mocker, get_response):
    response = get_response("get_workflow")
    mock = mocker.patch.object(client, "request_json")
    mock.return_value = response
    actual = client.get_workflow(workspace_id=98765, workflow_id="123456789")
    mock.assert_called_once()
    assert actual == models.Workflow.from_json(response["workflow"])


def test_that_list_workflows_works(client, mocker, get_response):
    mock = mocker.patch.object(client, "request_json")
    mock.return_value = get_response("list_workflows")
    result = client.list_workflows()
    mock.assert_called()
    assert len(result) == 3


def test_that_get_workflow_tasks_works(client, mocker, get_response):
    mock = mocker.patch.object(client, "request_json")
    mock.return_value = get_response("get_workflow_tasks")
    result = client.get_workflow_tasks(workspace_id=98765, workflow_id="123456789")
    mock.assert_called()
    assert len(result) == 4


def test_that_get_task_logs_works(client, mocker, get_response):
    mock = mocker.patch.object(client, "request_json")
    mock.return_value = get_response("get_task_logs")
    result = client.get_task_logs(
        workspace_id=98765, task_id=1, workflow_id="123456789"
    )
    mock.assert_called()
    assert result == "Ciao world!"
