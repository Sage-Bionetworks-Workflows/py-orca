from orca.services.nextflowtower.models.enums import TaskStatus


def test_that_TaskStatus_contant_values_are_correct():
    assert TaskStatus.SUBMITTED == "SUBMITTED"
    assert TaskStatus.RUNNING == "RUNNING"
    assert TaskStatus.SUCCEEDED == "SUCCEEDED"
    assert TaskStatus.FAILED == "FAILED"
    assert TaskStatus.CANCELLED == "CANCELLED"
    assert TaskStatus.UNKNOWN == "UNKNOWN"


def test_that_TaskStatus_terminal_states_are_in_terminal_states_list():
    assert TaskStatus.SUCCEEDED in TaskStatus.terminal_states
    assert TaskStatus.FAILED in TaskStatus.terminal_states
    assert TaskStatus.CANCELLED in TaskStatus.terminal_states
    assert TaskStatus.UNKNOWN in TaskStatus.terminal_states
