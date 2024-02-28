from unittest.mock import MagicMock

import pandas as pd
import pytest

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
    """
    Tests that the ``trigger_indexing`` method in ``SynapseOps``
    triggers indexing in a Synapse table view.

    Arguments:
        mocker: A mocker object.
        mocked_ops: A mocked instance of ``SynapseOps``.
    """
    # Mocking connection to the Synapse API
    syn_mock = mocked_ops.client

    # Assigning variable to a fake submission view string
    submission_view = "test_view"

    # Using patch to mock the Synapse tableQuery method
    with mocker.patch.object(syn_mock, "tableQuery"):
        # Calling the function
        mocked_ops.trigger_indexing(syn_mock, submission_view)

        # Assertions
        syn_mock.tableQuery.assert_called_once_with(
            f"select * from {submission_view} limit 1"
        )


def test_get_submissions(mocker, mocked_ops):
    """
    Tests that the ``get_submissions`` method in ``SynapseOps``
    returns a list of submission IDs.

    Arguments:
        mocker: A mocker object.
        mocked_ops: A mocked instance of ``SynapseOps``.

    """
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
    table_mock.asDataFrame.return_value = pd.DataFrame(input_dict)

    # Mock the ``trigger_indexing`` call in SynapseOps() and the tableQuery call
    # in ``SynapseOps().get_submissions``
    with mocker.patch.object(mocked_ops, "trigger_indexing", return_value=None):
        with mocker.patch.object(syn_mock, "tableQuery", return_value=table_mock):
            # Calling the function to be tested
            result = mocked_ops.get_submissions(submission_view, submission_status)

            # Assertions
            syn_mock.tableQuery.assert_called_once_with(
                f"select * from {submission_view} where status = '{submission_status}'"
            )
            table_mock.asDataFrame.assert_called()
            assert result == input_dict["id"]


def test_update_submissions_status(mocker, mocked_ops):
    """
    Tests that the ``update_submissions_status`` method in ``SynapseOps``
    updates the status of one or more submissions in Synapse.

    Arguments:
        mocker: A mocker object.
        mocked_ops: A mocked instance of ``SynapseOps``.
    """
    # Mocking the ``update_submission_status`` call in ``SynapseOps``
    mock_update_status = mocker.patch.object(mocked_ops, "update_submissions_status")

    # Calling the function to be tested
    mocked_ops.update_submissions_status(["submission_1", "submission_2"], "SCORED")

    # Assertions
    mock_update_status.assert_called_once_with(
        ["submission_1", "submission_2"], "SCORED"
    )


def test_update_submission_status_with_non_string_non_list_input():
    """
    Tests that the ``update_submissions_status`` method in ``SynapseOps``
    raises an error if the input is neither a string nor a list.

    Arguments:
        mocker: A mocker object.
        mocked_ops: A mocked instance of ``SynapseOps``.

    """
    # Test for non-string + non-list submission_ids.
    error = "Not a list. ``submission_ids`` must be an int or list of ints."
    with pytest.raises(TypeError) as err:
        # Calling the function to be tested
        SynapseOps().update_submissions_status(1234, "SCORED")

    # Assertions
    assert str(err.value) == error, f"Incorrect error message. Got '{err.value}'"


def test_update_submission_status_with_non_string_in_list(mocker, mocked_ops):
    """
    Tests that the ``update_submissions_status`` method in ``SynapseOps``
    raises an error if the input is a list with a non-string element.

    Arguments:
        mocker: A mocker object.
        mocked_ops: A mocked instance of ``SynapseOps``.

    """
    # Test for non-string elements in list
    error = "Non-strings found. ``submission_ids`` must be an int or list of ints."
    with pytest.raises(TypeError) as err:
        # Calling the function to be tested
        SynapseOps().update_submissions_status(["syn111", 1234], "SCORED")

    # Assertions
    assert str(err.value) == error, f"Incorrect error message. Got '{err.value}'"
