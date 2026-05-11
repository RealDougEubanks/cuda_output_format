import logging

import pytest

from plugin import (
    _inject_output_format,
    on_worker_process,
)


def test_inject_with_hwaccel_device_inserts_after_device_pair():
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-hwaccel",
        "cuda",
        "-hwaccel_device",
        "0",
        "-i",
        "input.mp4",
        "-c:v",
        "hevc_nvenc",
        "out.mkv",
    ]
    assert _inject_output_format(cmd) == [
        "ffmpeg",
        "-hide_banner",
        "-hwaccel",
        "cuda",
        "-hwaccel_device",
        "0",
        "-hwaccel_output_format",
        "cuda",
        "-i",
        "input.mp4",
        "-c:v",
        "hevc_nvenc",
        "out.mkv",
    ]


def test_inject_without_hwaccel_device_inserts_after_hwaccel_value():
    cmd = ["ffmpeg", "-hwaccel", "cuda", "-i", "input.mp4", "-c:v", "hevc_nvenc", "out.mkv"]
    assert _inject_output_format(cmd) == [
        "ffmpeg",
        "-hwaccel",
        "cuda",
        "-hwaccel_output_format",
        "cuda",
        "-i",
        "input.mp4",
        "-c:v",
        "hevc_nvenc",
        "out.mkv",
    ]


def test_inject_skipped_when_hwaccel_absent_returns_input_unchanged():
    cmd = ["ffmpeg", "-i", "input.mp4", "-c:v", "libx265", "out.mkv"]
    assert _inject_output_format(cmd) == cmd


def test_inject_skipped_when_hwaccel_value_is_not_cuda():
    cmd = ["ffmpeg", "-hwaccel", "vaapi", "-i", "input.mp4", "out.mkv"]
    assert _inject_output_format(cmd) == cmd


def test_inject_is_idempotent_when_output_format_already_present():
    cmd = [
        "ffmpeg",
        "-hwaccel",
        "cuda",
        "-hwaccel_output_format",
        "cuda",
        "-i",
        "input.mp4",
        "out.mkv",
    ]
    assert _inject_output_format(cmd) == cmd


def test_inject_called_twice_produces_same_result():
    cmd = ["ffmpeg", "-hwaccel", "cuda", "-i", "input.mp4", "out.mkv"]
    once = _inject_output_format(cmd)
    twice = _inject_output_format(once)
    assert once == twice


def test_inject_handles_dangling_hwaccel_flag_at_end_of_args():
    cmd = ["ffmpeg", "-hwaccel"]
    assert _inject_output_format(cmd) == cmd


def test_inject_raises_type_error_on_non_list_input():
    with pytest.raises(TypeError):
        _inject_output_format("ffmpeg -hwaccel cuda -i in.mp4 out.mkv")
    with pytest.raises(TypeError):
        _inject_output_format(None)


def test_on_worker_process_mutates_list_exec_command_in_place():
    cmd = ["ffmpeg", "-hwaccel", "cuda", "-i", "input.mp4", "out.mkv"]
    data = {"exec_command": list(cmd)}
    result = on_worker_process(data)
    assert result is data
    assert data["exec_command"] == [
        "ffmpeg",
        "-hwaccel",
        "cuda",
        "-hwaccel_output_format",
        "cuda",
        "-i",
        "input.mp4",
        "out.mkv",
    ]


def test_on_worker_process_handles_string_exec_command():
    data = {"exec_command": "ffmpeg -hwaccel cuda -i input.mp4 out.mkv"}
    on_worker_process(data)
    assert data["exec_command"] == (
        "ffmpeg -hwaccel cuda -hwaccel_output_format cuda -i input.mp4 out.mkv"
    )


def test_on_worker_process_preserves_quoted_paths_with_whitespace():
    data = {"exec_command": "ffmpeg -hwaccel cuda -i 'my movie.mp4' 'out file.mkv'"}
    on_worker_process(data)
    assert data["exec_command"] == (
        "ffmpeg -hwaccel cuda -hwaccel_output_format cuda -i 'my movie.mp4' 'out file.mkv'"
    )


def test_on_worker_process_leaves_string_unchanged_when_not_applicable():
    original = "ffmpeg -i input.mp4 -c:v libx265 out.mkv"
    data = {"exec_command": original}
    on_worker_process(data)
    assert data["exec_command"] == original


def test_on_worker_process_logs_warning_on_invalid_exec_command_type(caplog):
    data = {"exec_command": 12345}
    with caplog.at_level(logging.WARNING, logger="unmanic.plugin.cuda_output_format"):
        on_worker_process(data)
    assert any("exec_command must be list or str" in r.message for r in caplog.records)
    assert data["exec_command"] == 12345


def test_on_worker_process_logs_warning_when_data_is_not_a_mapping(caplog):
    with caplog.at_level(logging.WARNING, logger="unmanic.plugin.cuda_output_format"):
        result = on_worker_process("not a dict")  # type: ignore[arg-type]
    assert any("data must be a mutable mapping" in r.message for r in caplog.records)
    assert result == "not a dict"


def test_on_worker_process_missing_exec_command_is_noop():
    data: dict = {}
    on_worker_process(data)
    assert data == {}
