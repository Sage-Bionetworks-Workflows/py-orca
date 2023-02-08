import pytest


@pytest.fixture
def patch_os_environ(mocker):
    yield mocker.patch("os.environ", {})
