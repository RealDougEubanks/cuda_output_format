"""End-to-end tests for the two Unmanic hooks — `on_library_management_file_test`
and `on_worker_process`. Verifies that the orchestration (probe, settings,
mapper, helpers) wires together correctly, not just the individual helpers.
"""

from unittest.mock import MagicMock, patch

import plugin

# --- shared fixtures ----------------------------------------------------------


def _stream_info(codec: str = "h264") -> dict:
    return {
        "codec_name": codec,
        "codec_type": "video",
        "avg_frame_rate": "30000/1001",
    }


def _make_probe(file_ok: bool = True, codec: str = "h264") -> MagicMock:
    probe = MagicMock()
    probe.file.return_value = file_ok
    probe.get.side_effect = lambda key, default=None: {
        "streams": [_stream_info(codec)],
        "format": {"duration": "60.0"},
    }.get(key, default)
    return probe


def _settings_dict(**overrides) -> dict:
    base = {
        "hw_decoding": False,
        "hw_output_format_cuda": True,
        "advanced": False,
        "preset": "fast",
        "profile": "main",
        "max_muxing_queue_size": 2048,
        "main_options": "",
        "advanced_options": "",
        "custom_options": "",
        "keep_container": True,
        "dest_container": "mkv",
        "library_id": None,
    }
    base.update(overrides)
    return base


def _patch_settings_class(values: dict):
    instance = MagicMock()
    instance.get_setting.side_effect = lambda key: values.get(key)
    return patch.object(plugin, "Settings", return_value=instance)


# --- on_library_management_file_test ------------------------------------------


def test_library_test_marks_pending_when_streams_need_processing():
    data = {"path": "/tmp/movie.mp4", "library_id": None}
    probe = _make_probe(file_ok=True, codec="h264")

    with patch.object(plugin, "Probe", return_value=probe), _patch_settings_class(_settings_dict()):
        result = plugin.on_library_management_file_test(data)

    assert result is data
    assert data["add_file_to_pending_tasks"] is True


def test_library_test_skips_when_video_already_hevc():
    data = {"path": "/tmp/movie.mkv", "library_id": None}
    probe = _make_probe(file_ok=True, codec="hevc")

    with patch.object(plugin, "Probe", return_value=probe), _patch_settings_class(_settings_dict()):
        plugin.on_library_management_file_test(data)

    assert "add_file_to_pending_tasks" not in data or data.get("add_file_to_pending_tasks") is None


def test_library_test_short_circuits_when_probe_fails():
    data = {"path": "/tmp/not-a-video.txt", "library_id": None}
    probe = _make_probe(file_ok=False)

    with patch.object(plugin, "Probe", return_value=probe), _patch_settings_class(_settings_dict()):
        result = plugin.on_library_management_file_test(data)

    # Probe failure means the hook returns data untouched — never crashes.
    assert result is data
    assert "add_file_to_pending_tasks" not in data


# --- on_worker_process --------------------------------------------------------


def test_worker_process_builds_ffmpeg_command_for_h264_source():
    data = {
        "file_in": "/tmp/in.mp4",
        "file_out": "/tmp/out.mkv",
        "library_id": None,
    }
    probe = _make_probe(file_ok=True, codec="h264")
    settings = _settings_dict(hw_decoding=True, hw_output_format_cuda=True)

    with patch.object(plugin, "Probe", return_value=probe), _patch_settings_class(settings):
        result = plugin.on_worker_process(data)

    assert result is data
    assert data["exec_command"][0] == "ffmpeg"
    assert "-hwaccel" in data["exec_command"]
    assert "-hwaccel_output_format" in data["exec_command"]
    # NVENC must be the chosen codec.
    assert "hevc_nvenc" in data["exec_command"]
    # repeat must be False — we don't ask Unmanic to re-run us.
    assert data["repeat"] is False


def test_worker_process_returns_empty_command_when_streams_already_hevc():
    data = {
        "file_in": "/tmp/already.mkv",
        "file_out": "/tmp/out.mkv",
        "library_id": None,
    }
    probe = _make_probe(file_ok=True, codec="hevc")

    with patch.object(plugin, "Probe", return_value=probe), _patch_settings_class(_settings_dict()):
        plugin.on_worker_process(data)

    # Nothing to do → exec_command stays empty so Unmanic skips this runner.
    assert data["exec_command"] == []
    assert data["repeat"] is False


def test_worker_process_short_circuits_when_probe_fails():
    data = {
        "file_in": "/tmp/garbage.bin",
        "file_out": "/tmp/out.mkv",
        "library_id": None,
    }
    probe = _make_probe(file_ok=False)

    with patch.object(plugin, "Probe", return_value=probe), _patch_settings_class(_settings_dict()):
        plugin.on_worker_process(data)

    assert data["exec_command"] == []
    assert data["repeat"] is False


def test_worker_process_remuxes_when_keep_container_disabled():
    data = {
        "file_in": "/tmp/in.mp4",
        "file_out": "/tmp/out.mp4",
        "library_id": None,
    }
    probe = _make_probe(file_ok=True, codec="h264")
    settings = _settings_dict(keep_container=False, dest_container="mkv")

    with patch.object(plugin, "Probe", return_value=probe), _patch_settings_class(settings):
        plugin.on_worker_process(data)

    # Container remux must update file_out in-place so Unmanic writes to the
    # correct path.
    assert data["file_out"] == "/tmp/out.mkv"


# --- _finalize_command --------------------------------------------------------


def test_finalize_command_prepends_ffmpeg_and_attaches_progress_parser():
    data: dict = {}
    mapper = MagicMock()
    mapper.get_ffmpeg_args.return_value = ["-i", "/tmp/in.mp4", "/tmp/out.mkv"]
    probe = _make_probe()

    plugin._finalize_command(data, mapper, probe)

    assert data["exec_command"] == ["ffmpeg", "-i", "/tmp/in.mp4", "/tmp/out.mkv"]
    assert callable(data["command_progress_parser"])
