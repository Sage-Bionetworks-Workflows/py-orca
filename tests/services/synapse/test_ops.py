"""
Tests for Synapse operations conducted by SynapseOps.
"""
from unittest.mock import MagicMock

import pandas as pd
import pytest
from challengeutils import utils

from orca.errors import ConfigError
from orca.services.synapse import SynapseOps


def test_for_an_error_when_accessing_fs_without_credentials(
    patch_os_environ: pytest.fixture, syn_project_id: str
) -> None:
    """
    Test for an error when accessing fs without credentials.

    Arguments:
        patch_os_environ: The OS environment patch
        syn_project_id: The project ID

    """
    ops = SynapseOps()
    with pytest.raises(ConfigError):
        ops.fs.listdir(syn_project_id)


def test_monitor_evaluation_queue_returns_false_when_there_are_no_new_submissions(
    mocker: pytest.fixture, mocked_ops: MagicMock
) -> None:
    """
    Function to test if the monitor evaluation queue returns False
    when there are no new submissions.

    Arguments:
        mocker: The mocker object for mocking.
        mocked_ops: A mocked instance of ``SynapseOps``.

    Returns:
        Boolean indicating if there are no new submissions.
    """
    mock = mocker.patch.object(
        mocked_ops.client, "getSubmissionBundles", return_value=[]
    )
    result = mocked_ops.monitor_evaluation_queue("foo")
    mock.assert_called_once_with("foo", status="RECEIVED")
    assert not result


def test_monitor_evaluation_queue_returns_true_when_there_are_new_submissions(
    mocker: pytest.fixture, mocked_ops: MagicMock
) -> None:
    """
    A function to test if the monitor evaluation queue returns True
    when there are new submissions.

    Arguments:
        mocker: A mocker object.
        mocked_ops: A mocked instance of ``SynapseOps``.

    """
    mock = mocker.patch.object(
        mocked_ops.client,
        "getSubmissionBundles",
        return_value=["submission_1", "submission_2"],
    )
    result = mocked_ops.monitor_evaluation_queue("foo")
    mock.assert_called_once_with("foo", status="RECEIVED")
    assert result


def test_trigger_indexing(mocker: pytest.fixture, mocked_ops: MagicMock) -> None:
    """
    Tests that the ``trigger_indexing`` method in ``SynapseOps``
    triggers indexing in a Synapse table view.

    Arguments:
        mocker: A mocker object.
        mocked_ops: A mocked instance of ``SynapseOps``.

    """
    # Assigning variable to a fake submission view string
    submission_view = "test_view"

    # Using patch to mock the Synapse tableQuery method
    with mocker.patch.object(mocked_ops.client, "tableQuery"):
        # Calling the function
        mocked_ops.trigger_indexing(submission_view)

        # Assertions
        mocked_ops.client.tableQuery.assert_called_once_with(
            f"select * from {submission_view} limit 1"
        )


def test_get_submissions_with_status(
    mocker: pytest.fixture, mocked_ops: MagicMock
) -> None:
    """
    Tests that the ``get_submissions_with_status`` method in ``SynapseOps``
    returns a list of submission IDs.

    Arguments:
        mocker: A mocker object.
        mocked_ops: A mocked instance of ``SynapseOps``.

    """
    # Input values
    submission_view = "syn111"
    submission_status = "RECEIVED"

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
    # in ``SynapseOps().get_submissions_with_status``
    with mocker.patch.object(mocked_ops, "trigger_indexing", return_value=None):
        with mocker.patch.object(syn_mock, "tableQuery", return_value=table_mock):
            # Calling the function to be tested
            result = mocked_ops.get_submissions_with_status(
                submission_view, submission_status
            )

            # Assertions
            syn_mock.tableQuery.assert_called_once_with(
                f"select id from {submission_view} where status = '{submission_status}'"
            )
            table_mock.asDataFrame.assert_called()
            assert result == input_dict["id"]


def test_update_submission_status(
    mocker: pytest.fixture, mocked_ops: MagicMock
) -> None:
    """
    Tests that the ``update_submissions_status`` method in ``SynapseOps``
    updates the status of one or more submissions in Synapse.

    Arguments:
        mocker: A mocker object.
        mocked_ops: A mocked instance of ``SynapseOps``.
    """
    # Input args
    submission_status = "APPROVED"
    submission_id = "1234"
    etag = "0000"

    # Mocking the ``change_submission_status`` call
    # in ``SynapseOps.update_submissions_status``
    status_object = mocked_ops.client.evaluation.SubmissionStatus(
        id=submission_id,
        etag=etag,
        submissionAnnotations={"status": [submission_status]},
    )
    mock_change_submission_status = mocker.patch.object(
        utils, "change_submission_status", return_value=status_object
    )

    # Calling the function to be tested
    mocked_ops.update_submission_status(submission_id, submission_status)

    # Assertions
    mock_change_submission_status.assert_called_once_with(
        mocked_ops.client, submissionid=submission_id, status=submission_status
    )


@pytest.mark.parametrize("submission_id", (111.0, [111]))
def test_update_submission_status_with_wrong_data_type(submission_id) -> None:
    """
    Tests that the ``update_submission_status`` method in ``SynapseOps``
    raises an error if the input is the wrong datatype.

    """
    # Expect a custom TypeError for incorrect data types
    with pytest.raises(TypeError, match="``submission_id`` must be a string or int."):
        # Calling the function to be tested
        SynapseOps().update_submission_status(submission_id, "SCORED")
