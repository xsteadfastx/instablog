# pylint:disable=missing-docstring,redefined-outer-name,too-many-arguments
import logging
from unittest.mock import call, patch

import pytest
from click.testing import CliRunner

from instablog import cli


@pytest.fixture
def runner():
    yield CliRunner()


@pytest.mark.parametrize(
    "verbose,expected",
    [("-v", logging.DEBUG), ("-vvvv", logging.DEBUG), (None, logging.INFO)],
)
@patch("instablog.cli.core")
@patch("instablog.cli.logging.basicConfig")
def test_main(mock_basic_config, mock_core, runner, tmpdir, verbose, expected):
    data = {"foo": "bar"}
    mock_core.parse_images.return_value = data
    image_dir = tmpdir.mkdir("images").strpath
    posts_dir = tmpdir.mkdir("posts").strpath
    args_list = ["-u", "foo", "-i", image_dir, "-p", posts_dir]
    if verbose:
        args_list.append(verbose)
    runner.invoke(cli.main, args_list)
    assert mock_basic_config.call_args_list == [call(level=expected)]
    mock_core.parse_images.assert_called_with(image_dir)
    mock_core.create_markdown.assert_called_with(posts_dir, data)


@patch("instablog.cli.logging")
@patch("instablog.cli.core")
def test_main_exception(mock_core, mock_logging, runner, tmpdir):
    mock_core.download.side_effect = KeyError("foo")
    data = {"foo": "bar"}
    mock_core.parse_images.return_value = data
    image_dir = tmpdir.mkdir("images").strpath
    posts_dir = tmpdir.mkdir("posts").strpath
    args_list = ["-u", "foo", "-i", image_dir, "-p", posts_dir]
    runner.invoke(cli.main, args_list)

    mock_core.parse_images.assert_called_with(image_dir)
    mock_core.create_markdown.assert_called_with(posts_dir, data)
    assert mock_logging.exception.call_args_list == [call("%s", str("'foo'"))]
