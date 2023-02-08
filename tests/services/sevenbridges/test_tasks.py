import pytest

from orca.errors import OptionalAttrRequiredError, UnexpectedMatch
from orca.services.sevenbridges import SevenBridgesTasks


@pytest.mark.usefixtures("patch_os_environ")
class TestWithEmptyEnv:
    def test_that_constructions_from_creds_works(self, client_creds, api_mock):
        SevenBridgesTasks.from_creds(**client_creds)
        api_mock.assert_called_once()

    def test_for_an_error_when_using_a_project_required_method(self, mock_tasks):
        mock_tasks.project = None
        with pytest.raises(OptionalAttrRequiredError):
            mock_tasks.draft_task("foo", "bar", {})

    def test_that_the_client_is_used_to_get_a_task(self, mock_task, mock_tasks):
        mock_tasks.client.tasks.query.return_value = [mock_task]
        result = mock_tasks.get_task("foo", "bar")
        assert result == "123"

    def test_that_none_is_returned_when_no_matches(self, mock_task, mock_tasks):
        mock_task.name = "something"
        mock_tasks.client.tasks.query.return_value = [mock_task]
        result = mock_tasks.get_task("foo", "bar")
        assert result is None

    def test_that_none_is_returned_when_many_matches(self, mock_task, mock_tasks):
        mock_tasks.client.tasks.query.return_value = [mock_task, mock_task]
        with pytest.raises(UnexpectedMatch):
            mock_tasks.get_task("foo", "bar")

    def test_for_an_error_when_matching_task_has_diff_app(self, mock_task, mock_tasks):
        mock_task.app = "something"
        mock_tasks.client.tasks.query.return_value = [mock_task]
        with pytest.raises(UnexpectedMatch):
            mock_tasks.get_task("foo", "bar")

    def test_that_the_client_is_used_to_draft_a_task(self, mock_tasks):
        mock_tasks.draft_task("foo", "bar", {})
        mock_tasks.client.tasks.create.assert_called_once()

    def test_that_existing_tasks_are_returned(self, mock_tasks, mock_task, mocker):
        get_task_mock = mocker.patch.object(mock_tasks, "get_task")
        get_task_mock.return_value = mock_task
        result = mock_tasks.draft_task("foo", "bar", {})
        assert result == mock_task

    def test_that_the_client_is_used_to_launch_a_task(self, mock_tasks):
        mock_tasks.launch_task("foo")
        mock_task = mock_tasks.client.tasks.get.return_value
        mock_task.run.assert_called_once()

    def test_that_the_client_is_used_to_create_a_task(self, mock_tasks, mocker):
        draft_task_mock = mocker.patch.object(mock_tasks, "draft_task")
        launch_task_mock = mocker.patch.object(mock_tasks, "launch_task")
        mock_tasks.create_task("foo", "bar", {})
        draft_task_mock.assert_called_once()
        launch_task_mock.assert_called_once()

    def test_that_the_client_is_used_to_get_a_task_status(self, mock_tasks):
        status, is_done = mock_tasks.get_task_status("foo")
        mock_tasks.client.tasks.get.assert_called_once()
        assert status == mock_tasks.client.tasks.get.return_value.status
        assert not is_done
