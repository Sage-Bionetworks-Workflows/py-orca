import pytest

from orca.errors import ConfigError
from orca.services.synapse import SynapseOps
from synapseclient import Project, Folder, EntityViewSchema, EntityViewType
from unittest import mock

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

def build_up() -> EntityViewSchema:
    """
    Create a project and 2 folders with status annotations
    """
    syn = SynapseOps().client

    # Create a test Project
    project = Project(name="My project for testing submissions retrieval and update with py-orca")
    project = syn.store(obj=project)

    # Create an Evaluation
    name = "Test Evaluation"
    ev = Evaluation(
        name=name, description="Evaluation for testing", contentSource=project["id"]
    )
    ev = syn.store(ev)

    # Create Folders with status annotations
    folder_1 = Folder(
        name="folder_1", annotations={"status":"SCORED"}, parent=project)
    folder_2 = Folder(
        name="folder_2", annotations={"status":"RECEIVED"}, parent=project)

    syn.store(folder_1)
    syn.store(folder_2)

    syn.submit(ev, folder_1)

    # Create a View for the Folders that will "mock" a submission view
    view = SubmissionViewSchema(name="test submission view",
                            parent=project,
                            scopes=project["id"],
                            includeEntityTypes=[EntityViewType.FOLDER])

    view = syn.store(view)

    return view

import synapseclient
def createMockTable(mock, dataframe):
    table = mock.create_autospec(synapseclient.table.CsvFileTable)
    table.asDataFrame.return_value = dataframe
    return table

def test_get_submissions(mocker, mocked_ops):

    input_dict = {"id": ["submission_1", "submission_2"], "status": ["RECEIVED", "RECEIVED"]}

    # Mock the call for tableQuery and its expected output
    mock_table_query = mocker.patch.object(mocked_ops.client, "tableQuery")
    mock_as_dataframe = mock_table_query.return_value.asDataFrame
    mock_as_dataframe.return_value.__getitem__.return_value.tolist.return_value = input_dict["id"]
    
    # Input variables
    submission_id = "syn111"
    submission_status = "RECEIVED"

    # Call ``get_submissions``
    results = mocked_ops.get_submissions(submission_id, submission_status)

    # Ensure the appropriate query was made based on Input variables
    mock_table_query.assert_called_with(f"select * from {submission_id} where status = '{submission_status}'")

    # Ensure output is as expected
    assert set(results) == set(input_dict["id"])
