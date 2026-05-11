"""Tests for the NVDEC argument-building logic that distinguishes this
fork from upstream — i.e., the `-hwaccel_output_format cuda` injection.
"""

from unittest.mock import MagicMock

import plugin


def _make_mapper(settings_map: dict) -> "plugin.PluginStreamMapper":
    mapper = plugin.PluginStreamMapper()
    mock_settings = MagicMock()
    mock_settings.get_setting.side_effect = lambda key: settings_map.get(key)
    mapper.set_settings(mock_settings)
    return mapper


def test_nvdec_args_include_hwaccel_output_format_when_both_settings_on():
    mapper = _make_mapper({"hw_decoding": True, "hw_output_format_cuda": True})
    mapper.generate_default_nvdec_args()

    assert "-hwaccel" in mapper.generic_options
    hwaccel_idx = mapper.generic_options.index("-hwaccel")
    assert mapper.generic_options[hwaccel_idx + 1] == "cuda"

    assert "-hwaccel_output_format" in mapper.generic_options
    out_idx = mapper.generic_options.index("-hwaccel_output_format")
    assert mapper.generic_options[out_idx + 1] == "cuda"


def test_nvdec_args_skip_output_format_when_toggle_off():
    mapper = _make_mapper({"hw_decoding": True, "hw_output_format_cuda": False})
    mapper.generate_default_nvdec_args()

    assert "-hwaccel" in mapper.generic_options
    assert "-hwaccel_output_format" not in mapper.generic_options


def test_nvdec_args_noop_when_hw_decoding_disabled():
    before = ["-hide_banner", "-loglevel", "info"]
    mapper = _make_mapper({"hw_decoding": False, "hw_output_format_cuda": True})
    mapper.generate_default_nvdec_args()

    # No hwaccel flags added when hw_decoding is off.
    assert "-hwaccel" not in mapper.generic_options
    assert "-hwaccel_output_format" not in mapper.generic_options
    # Defaults from StreamMapper.__init__ should still be intact.
    assert mapper.generic_options == before


def test_nvdec_args_sets_default_device_id_zero():
    mapper = _make_mapper({"hw_decoding": True, "hw_output_format_cuda": True})
    mapper.generate_default_nvdec_args()

    assert "-hwaccel_device" in mapper.generic_options
    idx = mapper.generic_options.index("-hwaccel_device")
    assert mapper.generic_options[idx + 1] == "0"


def test_generic_options_order_is_ffmpeg_safe():
    """`-hwaccel_output_format` must follow `-hwaccel` in ffmpeg's CLI grammar."""
    mapper = _make_mapper({"hw_decoding": True, "hw_output_format_cuda": True})
    mapper.generate_default_nvdec_args()

    hwaccel_idx = mapper.generic_options.index("-hwaccel")
    out_fmt_idx = mapper.generic_options.index("-hwaccel_output_format")
    assert hwaccel_idx < out_fmt_idx
