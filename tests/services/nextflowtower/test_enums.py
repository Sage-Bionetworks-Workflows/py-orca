from orca.services.nextflowtower.models import WorkflowStatus


def test_that_TaskStatus_contant_values_are_correct():
    assert WorkflowStatus.SUBMITTED.value == "SUBMITTED"
    assert WorkflowStatus.RUNNING.value == "RUNNING"
    assert WorkflowStatus.SUCCEEDED.value == "SUCCEEDED"
    assert WorkflowStatus.FAILED.value == "FAILED"
    assert WorkflowStatus.CANCELLED.value == "CANCELLED"
    assert WorkflowStatus.UNKNOWN.value == "UNKNOWN"


def test_that_TaskStatus_terminal_states_are_in_terminal_states_list():
    assert WorkflowStatus.SUCCEEDED.value in WorkflowStatus.terminal_states.value
    assert WorkflowStatus.FAILED.value in WorkflowStatus.terminal_states.value
    assert WorkflowStatus.CANCELLED.value in WorkflowStatus.terminal_states.value
    assert WorkflowStatus.UNKNOWN.value in WorkflowStatus.terminal_states.value
