import pytest

from orca.errors import ConfigError, UnexpectedMatchError
from orca.services.sevenbridges import SevenBridgesOps
from orca.services.sevenbridges.models import TaskStatus


@pytest.mark.usefixtures("patch_os_environ")
class TestWithEmptyEnv:
    def test_that_constructions_from_creds_works(self, config, mock_api_init):
        SevenBridgesOps(config).client
        mock_api_init.assert_called_once()

    def test_for_error_when_constructing_from_config_without_project(
        self, config, mock_api_init
    ):
        config.project = None
        with pytest.raises(ConfigError):
            SevenBridgesOps(config).project

    def test_that_the_client_is_used_to_get_a_task(self, mock_task, mock_ops):
        mock_ops.client.tasks.query.return_value = [mock_task]
        result = mock_ops.get_task("foo", "bar")
        assert result == "123"

    def test_that_none_is_returned_when_no_matches(self, mock_task, mock_ops):
        mock_task.name = "something"
        mock_ops.client.tasks.query.return_value = [mock_task]
        result = mock_ops.get_task("foo", "bar")
        assert result is None

    def test_that_none_is_returned_when_many_matches(self, mock_task, mock_ops):
        mock_ops.client.tasks.query.return_value = [mock_task, mock_task]
        with pytest.raises(UnexpectedMatchError):
            mock_ops.get_task("foo", "bar")

    def test_for_an_error_when_matching_task_has_diff_app(self, mock_task, mock_ops):
        mock_task.app = "something"
        mock_ops.client.tasks.query.return_value = [mock_task]
        with pytest.raises(UnexpectedMatchError):
            mock_ops.get_task("foo", "bar")

    def test_that_the_client_is_used_to_draft_a_task(self, mock_ops):
        mock_ops.draft_task("foo", "bar", {})
        mock_ops.client.tasks.create.assert_called_once()

    def test_that_existing_tasks_are_returned(self, mock_ops, mock_task, mocker):
        get_task_mock = mocker.patch.object(mock_ops, "get_task")
        get_task_mock.return_value = mock_task
        result = mock_ops.draft_task("foo", "bar", {})
        assert result == mock_task

    def test_that_the_client_is_used_to_launch_a_task(self, mock_ops):
        mock_ops.launch_task("foo")
        mock_task = mock_ops.client.tasks.get.return_value
        mock_task.run.assert_called_once()

    def test_that_the_client_is_used_to_create_a_task(self, mock_ops, mocker):
        draft_task_mock = mocker.patch.object(mock_ops, "draft_task")
        launch_task_mock = mocker.patch.object(mock_ops, "launch_task")
        mock_ops.create_task("foo", "bar", {})
        draft_task_mock.assert_called_once()
        launch_task_mock.assert_called_once()

    def test_that_the_client_is_used_to_get_a_task_status(self, mock_ops, mocker):
        mock_task = mocker.Mock()
        mock_task.status = "DRAFT"
        mock_ops.client.tasks.get.return_value = mock_task
        status = mock_ops.get_task_status("foo")
        mock_ops.client.tasks.get.assert_called_once()
        assert status == TaskStatus("DRAFT")
