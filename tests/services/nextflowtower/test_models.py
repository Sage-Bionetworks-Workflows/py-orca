import pytest

from orca.services.nextflowtower.models import LaunchInfo


def test_that_getting_an_launch_info_attribute_works():
    launch_info = LaunchInfo(pipeline="foo")
    assert launch_info.get("pipeline") == "foo"


def test_for_an_error_when_getting_an_launch_info_attribute_that_is_missing():
    launch_info = LaunchInfo()
    with pytest.raises(ValueError):
        launch_info.get("pipeline")


def test_that_launch_info_attribute_can_be_filled_in():
    launch_info = LaunchInfo()
    assert launch_info.pipeline is None
    launch_info.fill_in("pipeline", "foo")
    assert launch_info.pipeline == "foo"


def test_that_launch_info_list_attribute_can_be_added_in():
    launch_info = LaunchInfo(label_ids=[1, 2, 3])
    assert launch_info.label_ids == [1, 2, 3]
    launch_info.add_in("label_ids", [4, 5, 6])
    assert launch_info.label_ids == [1, 2, 3, 4, 5, 6]


def test_for_an_error_when_adding_in_with_nonlist_launch_info_attribute():
    launch_info = LaunchInfo(pipeline="foo")
    with pytest.raises(ValueError):
        launch_info.add_in("pipeline", [4, 5, 6])
