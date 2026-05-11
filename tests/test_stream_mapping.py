"""Tests for `PluginStreamMapper.test_stream_needs_processing` and
`custom_stream_mapping`."""

from unittest.mock import MagicMock

import plugin


def _mapper(advanced: bool, preset: str = "medium", profile: str = "main"):
    m = plugin.PluginStreamMapper()
    settings = MagicMock()
    settings.get_setting.side_effect = lambda key: {
        "advanced": advanced,
        "preset": preset,
        "profile": profile,
        "custom_options": "-preset slow -profile:v main10 -b:v 6M",
    }.get(key)
    m.set_settings(settings)
    return m


def test_image_codecs_are_skipped():
    m = _mapper(advanced=False)
    assert m.test_stream_needs_processing({"codec_name": "png"}) is False
    assert m.test_stream_needs_processing({"codec_name": "MJPEG"}) is False


def test_hevc_streams_are_skipped():
    m = _mapper(advanced=False)
    assert m.test_stream_needs_processing({"codec_name": "hevc"}) is False
    assert m.test_stream_needs_processing({"codec_name": "H265"}) is False


def test_h264_streams_are_processed():
    m = _mapper(advanced=False)
    assert m.test_stream_needs_processing({"codec_name": "h264"}) is True


def test_simple_mapping_includes_profile_and_preset_for_stream():
    m = _mapper(advanced=False, preset="slow", profile="main10")
    mapping = m.custom_stream_mapping({"codec_name": "h264"}, stream_id=0)

    assert mapping["stream_mapping"] == ["-map", "0:v:0"]
    assert mapping["stream_encoding"] == [
        "-c:v:0",
        "hevc_nvenc",
        "-profile:v:0",
        "main10",
        "-preset",
        "slow",
    ]


def test_advanced_mapping_uses_custom_options_split():
    m = _mapper(advanced=True)
    mapping = m.custom_stream_mapping({"codec_name": "h264"}, stream_id=1)

    assert mapping["stream_mapping"] == ["-map", "0:v:1"]
    # Encoding starts with the encoder, then the user's free-text split.
    assert mapping["stream_encoding"][:2] == ["-c:v:1", "hevc_nvenc"]
    assert mapping["stream_encoding"][2:] == [
        "-preset",
        "slow",
        "-profile:v",
        "main10",
        "-b:v",
        "6M",
    ]
