from datetime import datetime
from getpass import getuser
from uuid import uuid4

import pytest

UUID = str(uuid4())
USER = getuser()
UTCTIME = datetime.now().isoformat("T", "seconds").replace(":", ".")
RUN_ID = f"{USER}--{UTCTIME}--{UUID}"  # Valid characters: [A-Za-z0-9._-]


@pytest.fixture
def run_id():
    return RUN_ID


@pytest.fixture
def patch_os_environ(mocker):
    yield mocker.patch("os.environ", {})
