from datetime import datetime, timezone

from orca.services.nextflowtower import utils


def test_that_parse_datetime_works():
    result = utils.parse_datetime("2023-04-26T00:49:49Z")
    assert result == datetime(2023, 4, 26, 0, 49, 49, tzinfo=timezone.utc)
