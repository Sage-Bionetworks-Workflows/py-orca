from datetime import datetime, timezone

import pytest

from orca.services.nextflowtower import utils


def test_that_parse_datetime_works():
    result = utils.parse_datetime("2023-04-26T00:49:49Z")
    assert result == datetime(2023, 4, 26, 0, 49, 49, tzinfo=timezone.utc)


def test_that_launch_info_dedup_works():
    secrets = ["foo", "bar", "baz", "foo"]
    dedupped = utils.dedup(secrets)
    assert len(dedupped) == 3


def test_that_increment_suffix_works_with_unsuffixed_strings_with_underscore():
    assert utils.increment_suffix("foo_bar") == "foo_bar_2"


def test_that_increment_suffix_works_with_unsuffixed_strings():
    assert utils.increment_suffix("foo") == "foo_2"


def test_that_increment_suffix_works_with_underscore_suffixed_strings():
    assert utils.increment_suffix("foo_") == "foo_2"


def test_that_increment_suffix_works_with_1_suffixed_strings():
    assert utils.increment_suffix("foo_1") == "foo_2"


def test_that_increment_suffix_works_with_2_suffixed_strings():
    assert utils.increment_suffix("foo_2") == "foo_3"


def test_that_increment_suffix_works_with_99_suffixed_strings():
    assert utils.increment_suffix("foo_99") == "foo_100"


def test_that_get_nested_works_with_single_key():
    input = {"foo": {"bar": {"baz": 123}}}
    result = utils.get_nested(input, "foo")
    assert result == {"bar": {"baz": 123}}


def test_that_get_nested_works_with_many_keys():
    input = {"foo": {"bar": {"baz": 123}}}
    result = utils.get_nested(input, "foo.bar.baz")
    assert result == 123


def test_for_an_error_when_using_nonexistent_keys_with_get_nested_works():
    input = {"foo": {"bar": {"baz": 123}}}
    with pytest.raises(ValueError):
        utils.get_nested(input, "foo.bar.atchoo")
