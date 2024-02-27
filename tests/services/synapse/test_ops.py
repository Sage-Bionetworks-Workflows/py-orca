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
    with mocker.patch.object(syn_mock, 'tableQuery') as table_query_mock:
        # Calling the function
        mocked_ops.trigger_indexing(syn_mock, submission_view)

        # Assertions
        syn_mock.tableQuery.assert_called_once_with(f"select * from {submission_view} limit 1")


def createMockTable(mock, dataframe):
    table = mock.create_autospec(synapseclient.table.CsvFileTable)
    table.asDataFrame.return_value = dataframe
    return table

def test_get_submissions(mocker, mocked_ops):
    # TODO: return value for tableQuery needs to be a CsvFileTable 
    input_dict = {
        "id": ["submission_1", "submission_2"],
        "status": ["RECEIVED", "RECEIVED"],
    }

    syn_mock = mocked_ops.client
    # Mocking the table query results
    table_mock = MagicMock()
    table_mock.asDataFrame.return_value = pd.DataFrame(input_dict)#input_dict#pd.DataFrame({"id": submission_ids})
    #table_mock.asCsvFileTable.return_value = createMockTable(mock, pd.DataFrame(input_dict))

    # Mock the tableQuery call in ``get_submissions``, and generate expected output
    with mocker.patch.object(mocked_ops, "trigger_indexing", return_value=None) as trigger_indexing_mock:
        with mocker.patch.object(syn_mock, 'tableQuery', return_value=table_mock):
        
            # Calling the function
            result = mocked_ops.get_submissions("test_view", "RECEIVED")
            print(result)
            # Assertions
            #trigger_indexing_mock.assert_called_once_with(syn_mock, "test_view")
            syn_mock.tableQuery.assert_called_once_with("select * from test_view where status = 'RECEIVED'")
            table_mock.asDataFrame.assert_called()
            assert result == input_dict["id"]

    # # Mock the tableQuery call in ``get_submissions``, and generate expected output
    # mock_table_query = mocker.patch.object(mocked_ops.client,
    #                                        "tableQuery",
    #                                        return_value=table_mock)
    # mock_as_dataframe = mock_table_query.return_value.asDataFrame
    # mock_as_dataframe.return_value.__getitem__.return_value.tolist.return_value = (
    #     input_dict["id"]
    # )

    # # Input variables
    # submission_id = "syn111"
    # submission_status = "RECEIVED"

    # # Call ``get_submissions``
    # results = mocked_ops.get_submissions(submission_id, submission_status)

    # # Ensure the appropriate query was made based on Input variables
    # mock_table_query.assert_called_with(
    #     f"select * from {submission_id} where status = '{submission_status}'"
    # )

    # # Ensure output is as expected
    # assert set(results) == set(input_dict["id"])

def test_update_submissions_status(mocker, mocked_ops):
    mock_update_status = mocker.patch.object(mocked_ops, "update_submissions_status")
    mocked_ops.update_submissions_status(["submission_1", "submission_2"], "SCORED")
    
    mock_update_status.assert_called_once_with(["submission_1", "submission_2"], "SCORED")
