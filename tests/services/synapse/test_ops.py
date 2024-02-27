import pytest
import synapseclient

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


def createMockTable(mock, dataframe):
    table = mock.create_autospec(synapseclient.table.CsvFileTable)
    table.asDataFrame.return_value = dataframe
    return table


def test_get_submissions(mocker, mocked_ops):
    input_dict = {
        "id": ["submission_1", "submission_2"],
        "status": ["RECEIVED", "RECEIVED"],
    }

    # Mock the tableQuery call in ``get_submissions``, and its expected output
    mock_table_query = mocker.patch.object(mocked_ops.client, "tableQuery")
    mock_as_dataframe = mock_table_query.return_value.asDataFrame
    mock_as_dataframe.return_value.__getitem__.return_value.tolist.return_value = (
        input_dict["id"]
    )

    # Input variables
    submission_id = "syn111"
    submission_status = "RECEIVED"

    # Call ``get_submissions``
    results = mocked_ops.get_submissions(submission_id, submission_status)

    # Ensure the appropriate query was made based on Input variables
    mock_table_query.assert_called_with(
        f"select * from {submission_id} where status = '{submission_status}'"
    )

    # Ensure output is as expected
    assert set(results) == set(input_dict["id"])


def test_update_submissions_status(mocker, mocked_ops):
    mock = mocker.patch.object(mocked_ops, "update_submission_status")
    mocked_ops.update_submissions_status(["submission_1", "submission_2"], "RECEIVED")
    mock.assert_called_once_with("submission_1", "RECEIVED")
    mock.assert_called_once_with("submission_2", "RECEIVED")


"""

def test_get_submissions_with_list_not_returned(mocker, mocked_ops):
    mock = mocker.patch.object(
        mocked_ops,
        "get_submissions",
        return_value=["submission_1", "submission_2"],
    )
    result = mock()
    mock.assert_called_once()
    assert isinstance(result, list), "A list was not returned."
    # assert all(isinstance(id, int) for id in result), "Non-integer IDs returned."

def test_get_submissions_with_non_string_data_types()
"""
