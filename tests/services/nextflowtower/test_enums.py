from orca.services.nextflowtower.models import TaskStatus


def test_that_TaskStatus_contant_values_are_correct():
    assert TaskStatus.SUBMITTED.value == "SUBMITTED"
    assert TaskStatus.RUNNING.value == "RUNNING"
    assert TaskStatus.SUCCEEDED.value == "SUCCEEDED"
    assert TaskStatus.FAILED.value == "FAILED"
    assert TaskStatus.CANCELLED.value == "CANCELLED"
    assert TaskStatus.UNKNOWN.value == "UNKNOWN"


def test_that_TaskStatus_terminal_states_are_in_terminal_states_list():
    assert TaskStatus.SUCCEEDED.value in TaskStatus.terminal_states.value
    assert TaskStatus.FAILED.value in TaskStatus.terminal_states.value
    assert TaskStatus.CANCELLED.value in TaskStatus.terminal_states.value
    assert TaskStatus.UNKNOWN.value in TaskStatus.terminal_states.value
