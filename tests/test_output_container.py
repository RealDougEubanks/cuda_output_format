"""Tests for `_apply_output_container` — the container-remux decision."""

from unittest.mock import MagicMock

import plugin


def _settings(keep_container: bool, dest_container: str = "mkv"):
    s = MagicMock()
    s.get_setting.side_effect = lambda key: {
        "keep_container": keep_container,
        "dest_container": dest_container,
    }.get(key)
    return s


def test_keep_container_passes_file_out_through_unchanged():
    mapper = MagicMock()
    data = {"file_out": "/tmp/foo.mp4"}

    plugin._apply_output_container(data, _settings(keep_container=True), mapper)

    mapper.set_output_file.assert_called_once_with("/tmp/foo.mp4")
    assert data["file_out"] == "/tmp/foo.mp4"


def test_remux_rewrites_extension_and_updates_file_out():
    mapper = MagicMock()
    data = {"file_out": "/tmp/foo.mp4"}

    plugin._apply_output_container(
        data, _settings(keep_container=False, dest_container="mkv"), mapper
    )

    mapper.set_output_file.assert_called_once_with("/tmp/foo.mkv")
    assert data["file_out"] == "/tmp/foo.mkv"


def test_remux_strips_leading_dot_in_dest_container():
    mapper = MagicMock()
    data = {"file_out": "/tmp/foo.mp4"}

    plugin._apply_output_container(
        data, _settings(keep_container=False, dest_container=".mov"), mapper
    )

    mapper.set_output_file.assert_called_once_with("/tmp/foo.mov")


def test_remux_handles_path_with_no_extension():
    mapper = MagicMock()
    data = {"file_out": "/tmp/foo"}

    plugin._apply_output_container(
        data, _settings(keep_container=False, dest_container="mkv"), mapper
    )

    mapper.set_output_file.assert_called_once_with("/tmp/foo.mkv")
