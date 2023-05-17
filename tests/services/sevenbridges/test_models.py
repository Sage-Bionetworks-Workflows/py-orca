import pytest
from sevenbridges.models.enums import TaskStatus as TaskState

from orca.services.sevenbridges.models import TaskStatus


def test_for_an_error_when_using_invalid_state():
    with pytest.raises(ValueError):
        TaskStatus("foobar")


def test_that_terminal_states_are_considered_done():
    for state in TaskState.terminal_states:
        status = TaskStatus(state)
        assert status.is_done
