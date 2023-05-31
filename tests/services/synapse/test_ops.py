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
