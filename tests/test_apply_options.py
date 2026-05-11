"""Tests for `_apply_options` — advanced free-text vs simple form-driven."""

from unittest.mock import MagicMock

import plugin


def _settings(**overrides):
    base = {
        "advanced": False,
        "main_options": "",
        "advanced_options": "",
        "preset": "medium",
        "max_muxing_queue_size": 2048,
    }
    base.update(overrides)
    s = MagicMock()
    s.get_setting.side_effect = lambda key: base.get(key)
    return s


def test_simple_mode_threads_two_for_fast_preset():
    mapper = MagicMock()
    plugin._apply_options(_settings(advanced=False, preset="fast"), mapper)

    mapper.set_ffmpeg_advanced_options.assert_called_once()
    kwargs = mapper.set_ffmpeg_advanced_options.call_args.kwargs
    assert kwargs["-threads"] == "2"
    assert kwargs["-max_muxing_queue_size"] == "2048"


def test_simple_mode_threads_two_for_medium_preset():
    mapper = MagicMock()
    plugin._apply_options(_settings(advanced=False, preset="medium"), mapper)
    assert mapper.set_ffmpeg_advanced_options.call_args.kwargs["-threads"] == "2"


def test_simple_mode_threads_one_for_slow_preset():
    mapper = MagicMock()
    plugin._apply_options(_settings(advanced=False, preset="slow"), mapper)
    assert mapper.set_ffmpeg_advanced_options.call_args.kwargs["-threads"] == "1"


def test_simple_mode_threads_one_for_lossless_preset():
    mapper = MagicMock()
    plugin._apply_options(_settings(advanced=False, preset="lossless"), mapper)
    assert mapper.set_ffmpeg_advanced_options.call_args.kwargs["-threads"] == "1"


def test_simple_mode_propagates_max_muxing_queue_size_as_string():
    mapper = MagicMock()
    plugin._apply_options(_settings(advanced=False, max_muxing_queue_size=4096), mapper)
    assert mapper.set_ffmpeg_advanced_options.call_args.kwargs["-max_muxing_queue_size"] == "4096"


def test_advanced_mode_overwrites_main_and_advanced_options():
    mapper = MagicMock()
    plugin._apply_options(
        _settings(
            advanced=True,
            main_options="-threads 8 -loglevel debug",
            advanced_options="-strict -2 -max_muxing_queue_size 8192",
        ),
        mapper,
    )

    assert mapper.main_options == ["-threads", "8", "-loglevel", "debug"]
    assert mapper.advanced_options == ["-strict", "-2", "-max_muxing_queue_size", "8192"]
    mapper.set_ffmpeg_advanced_options.assert_not_called()


def test_advanced_mode_leaves_empty_option_strings_alone():
    mapper = MagicMock()
    # Pre-existing values on the mapper — `_apply_options` must not clobber
    # them with empty lists when the textareas are blank.
    mapper.main_options = ["-existing"]
    mapper.advanced_options = ["-existing-advanced"]

    plugin._apply_options(_settings(advanced=True, main_options="", advanced_options=""), mapper)

    assert mapper.main_options == ["-existing"]
    assert mapper.advanced_options == ["-existing-advanced"]
