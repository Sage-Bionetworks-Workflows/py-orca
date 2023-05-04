import pytest

from orca.services.nextflowtower.models import LaunchInfo


@pytest.fixture
def launch_info():
    yield LaunchInfo(
        compute_env_id="5ykJF",
        pipeline="foo/bar",
        revision="1.1.0",
        profiles=["test"],
        params={"foo": "bar"},
        work_dir="s3://foo/work",
    )


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


def test_that_launch_info_can_be_created_with_resume_enabled():
    launch_info = LaunchInfo(resume=True, session_id="foo")
    assert launch_info


def test_that_launch_info_can_be_serialized_with_resume_enabled(launch_info):
    launch_info.resume = True
    launch_info.session_id = "foo"
    json = launch_info.to_json()
    assert "resume" in json["launch"]
    assert "sessionId" in json["launch"]


def test_that_launch_info_can_be_serialized_with_resume_disabled(launch_info):
    json = launch_info.to_json()
    assert "resume" not in json["launch"]
    assert "sessionId" not in json["launch"]


def test_for_an_error_when_enabling_resume_without_session_id():
    with pytest.raises(ValueError):
        LaunchInfo(resume=True)
