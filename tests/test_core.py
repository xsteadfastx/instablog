"""Tests for core."""
# pylint:disable=missing-docstring
from unittest.mock import call, patch

import pytest

from instablog import core


# pylint: disable=missing-docstring
@pytest.mark.parametrize(
    "datetime_str,expected",
    [
        ("2018-5-1 16h49m44s0", {"date": "2018-05-01", "time": "16:49"}),
        ("2018-05-01 16h49m44s0", {"date": "2018-05-01", "time": "16:49"}),
    ],
)
def test_parse_datetime(datetime_str, expected):
    assert core.parse_datetime(datetime_str) == expected


@patch("instablog.core.logging")
@patch("instablog.core.os.listdir")
def test_parse_images(mock_listdir, mock_logging, tmpdir):
    mock_listdir.return_value = [
        "insta-2018-7-19 10h44m51s0-1826786070344609046.jpg",
        "insta-2018-4-29 12h1m54s0-1768118018388578728.jpg",
    ]

    assert core.parse_images(tmpdir.strpath) == {
        "2018-07-19": [("insta-2018-7-19 10h44m51s0-1826786070344609046.jpg", "10:44")],
        "2018-04-29": [("insta-2018-4-29 12h1m54s0-1768118018388578728.jpg", "12:01")],
    }

    assert mock_logging.info.call_args_list == [
        call("Parsing images..."),
        call("parsing: %s", "insta-2018-7-19 10h44m51s0-1826786070344609046.jpg"),
        call("parsing: %s", "insta-2018-4-29 12h1m54s0-1768118018388578728.jpg"),
        call("Done parsing."),
    ]

    assert mock_logging.debug.call_args_list == [
        call("matched: %s", ("2018-7-19 10h44m51s0", "1826786070344609046")),
        call("matched: %s", ("2018-4-29 12h1m54s0", "1768118018388578728")),
    ]


@patch("instablog.core.logging")
@patch("instablog.core.os.listdir")
def test_parse_images_not_matched(mock_listdir, mock_logging, tmpdir):
    mock_listdir.return_value = ["foobar.jpg"]

    assert core.parse_images(tmpdir.strpath) == {}

    assert mock_logging.info.call_args_list == [
        call("Parsing images..."),
        call("parsing: %s", "foobar.jpg"),
        call("Done parsing."),
    ]

    assert mock_logging.debug.call_args_list == [
        call("did not matched: %s", "foobar.jpg")
    ]


@pytest.mark.parametrize(
    "data",
    [
        {
            "2018-07-19": [
                ("insta-2018-7-19 10h44m51s0-1826786070344609046.jpg", "10:44")
            ],
            "2018-04-29": [
                ("insta-2018-4-29 12h1m54s0-1768118018388578728.jpg", "12:01")
            ],
        }
    ],
)
def test_create_markdown(data, tmpdir):
    core.create_markdown(tmpdir.strpath, data)
    for key, value in data.items():
        assert tmpdir.join(f"{key}-in-bildern.md") in tmpdir.listdir()
        with open(tmpdir.join(f"{key}-in-bildern.md"), "r") as md_file:
            content = md_file.read()
            assert (
                f"Title: {key} in Bildern\n"
                f"Date: {key} {value[0][1]}\n"
                "Tags: instagram, photography\n"
                f"Slug: {key}-in-bildern\n\n\n"
                f"![{key}]"
                "({filename}/images/"
                f"{value[0][0]})\n"
            ) == content


@patch("instablog.core.ProfileLooter")
@patch("instablog.core.logging")
def test_download(mock_logging, mock_profile_looter):
    core.download("foouser", "/tmp/foouser")
    assert mock_logging.info.call_args_list == [
        call("Downloading..."),
        call("Done downloading."),
    ]

    mock_profile_looter.assert_called_with("foouser", template="insta-{datetime}-{id}")
    mock_profile_looter.return_value.download.assert_called_with("/tmp/foouser")
