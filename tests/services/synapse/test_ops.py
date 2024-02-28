import pytest
import synapseclient
import pandas as pd
from unittest.mock import MagicMock, patch
from unittest import mock

from orca.errors import ConfigError
from orca.services.synapse import SynapseOps


def test_for_an_error_when_accessing_fs_without_credentials(
    patch_os_environ, syn_project_id
):
    ops = SynapseOps()
    with pytest.raises(ConfigError):
        ops.fs.listdir(syn_project_id)


def test_monitor_evaluation_queue_returns_false_when_there_are_no_new_submissions(
    mocker, mocked_ops
):
    mock = mocker.patch.object(
        mocked_ops.client, "getSubmissionBundles", return_value=[]
    )
    result = mocked_ops.monitor_evaluation_queue("foo")
    mock.assert_called_once_with("foo", status="RECEIVED")
    assert result is False


def test_monitor_evaluation_queue_returns_true_when_there_are_new_submissions(
    mocker, mocked_ops
):
    mock = mocker.patch.object(
        mocked_ops.client,
        "getSubmissionBundles",
        return_value=["submission_1", "submission_2"],
    )
    result = mocked_ops.monitor_evaluation_queue("foo")
    mock.assert_called_once_with("foo", status="RECEIVED")
    assert result


def test_trigger_indexing(mocker, mocked_ops):
    # Mocking connection to the Synapse API
    syn_mock = mocked_ops.client

    # Assigning variable to a fake submission view string
    submission_view = "test_view"

    # Using patch to mock the Synapse tableQuery method
    with mocker.patch.object(syn_mock, "tableQuery") as table_query_mock:
        # Calling the function
        mocked_ops.trigger_indexing(syn_mock, submission_view)

        # Assertions
        syn_mock.tableQuery.assert_called_once_with(
            f"select * from {submission_view} limit 1"
        )


def createMockTable(mock, dataframe):
    table = mock.create_autospec(synapseclient.table.CsvFileTable)
    table.asDataFrame.return_value = dataframe
    return table


def test_get_submissions(mocker, mocked_ops):
    # Input values
    submission_view = "syn111"
    submission_status = "RECEIVED"

    # TODO: return value for tableQuery needs to be a CsvFileTable??
    input_dict = {
        "id": ["submission_1", "submission_2"],
        "status": ["RECEIVED", "RECEIVED"],
    }

    # Mocking connection to the Synapse API
    syn_mock = mocked_ops.client

    # Mocking the table query results
    table_mock = MagicMock()
    table_mock.asDataFrame.return_value = pd.DataFrame(
        input_dict
    )  # input_dict#pd.DataFrame({"id": submission_ids})
    # table_mock.asCsvFileTable.return_value = createMockTable(mock, pd.DataFrame(input_dict))

    # Mock the ``trigger_indexing`` call in SynapseOps() and the tableQuery call in ``SynapseOps().get_submissions``
    with mocker.patch.object(
        mocked_ops, "trigger_indexing", return_value=None
    ) as trigger_indexing_mock:
        with mocker.patch.object(syn_mock, "tableQuery", return_value=table_mock):
            # Calling the function to be tested
            result = mocked_ops.get_submissions(submission_view, submission_status)

            # Assertions
            # trigger_indexing_mock.assert_called_once_with(syn_mock, "test_view")
            syn_mock.tableQuery.assert_called_once_with(
                f"select * from {submission_view} where status = '{submission_status}'"
            )
            table_mock.asDataFrame.assert_called()
            assert result == input_dict["id"]


def test_update_submissions_status(mocker, mocked_ops):
    # Mocking the ``update_submission_status`` call in ``SynapseOps``
    mock_update_status = mocker.patch.object(mocked_ops, "update_submissions_status")

    # Calling the function to be tested
    mocked_ops.update_submissions_status(["submission_1", "submission_2"], "SCORED")

    # Assertions
    mock_update_status.assert_called_once_with(
        ["submission_1", "submission_2"], "SCORED"
    )


def test_update_submission_status_with_non_string_non_list_input(mocker, mocked_ops):
    # Mocking the ``update_submission_status`` call in ``SynapseOps``.
    # Test for non-string + non-list submission_ids.
    with mocker.patch.object(
        mocked_ops, "update_submissions_status", side_effect=TypeError
    ) as moc:
        with pytest.raises(TypeError):
            # Calling the function to be tested
            mocked_ops.update_submissions_status(1234, "SCORED")

            # Assertions
            mocked_ops.update_submissions_status.assert_called_once_with(1234, "SCORED")


def test_update_submission_status_with_non_string_in_list(mocker, mocked_ops):
    # Mocking the ``update_submission_status`` call in ``SynapseOps``
    # Test for non-string elements in list
    with mocker.patch.object(
        mocked_ops, "update_submissions_status", side_effect=TypeError
    ) as moc:
        with pytest.raises(TypeError):
            # Calling the function to be tested
            mocked_ops.update_submissions_status(["syn111", 1234], "SCORED")

            # Assertions
            mocked_ops.update_submissions_status.assert_called_once_with(
                ["syn111", 1234], "SCORED"
            )
