#!/usr/bin/env python3

"""
plugin.py — encoder_video_hevc_nvenc_gpu

Fork of Josh5/unmanic.plugin.encoder_video_hevc_nvenc that injects
`-hwaccel_output_format cuda` alongside `-hwaccel cuda` when NVDEC
hardware-accelerated decoding is enabled, so decoded frames stay in
GPU memory all the way through to NVENC.

Original author:          Josh.5 <jsunnex@gmail.com> (2021)
Fork maintained by:       Doug Eubanks <doug.eubanks@atlanticbt.com> (2026)

Copyright:
    Copyright (C) 2021 Josh Sunnex
    Copyright (C) 2026 Doug Eubanks

    This program is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by the
    Free Software Foundation, version 3.

    This program is distributed in the hope that it will be useful, but
    WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
    or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
    for more details.

    You should have received a copy of the GNU General Public License along
    with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import logging
import os
from typing import Any

from encoder_video_hevc_nvenc_gpu.lib.ffmpeg import Parser, Probe, StreamMapper
from encoder_video_hevc_nvenc_gpu.settings import Settings

__all__ = ["Settings", "on_library_management_file_test", "on_worker_process"]

logger = logging.getLogger("Unmanic.Plugin.encoder_video_hevc_nvenc_gpu")


class PluginStreamMapper(StreamMapper):
    image_video_codecs = [
        "alias_pix", "apng", "brender_pix", "dds", "dpx", "exr", "fits", "gif",
        "mjpeg", "mjpegb", "pam", "pbm", "pcx", "pfm", "pgm", "pgmyuv", "pgx",
        "photocd", "pictor", "pixlet", "png", "ppm", "ptx", "sgi", "sunrast",
        "tiff", "vc1image", "wmv3image", "xbm", "xface", "xpm", "xwd",
    ]  # fmt: skip

    def __init__(self):
        super().__init__(logger, ["video"])
        # Typed as `Any` because the Settings instance is injected via
        # `set_settings` after construction (mirroring the upstream pattern).
        # All methods that touch `self.settings` assume it's been set.
        self.settings: Any = None

    def set_settings(self, settings: Settings) -> None:
        self.settings = settings

    def test_stream_needs_processing(self, stream_info: dict):
        codec = stream_info.get("codec_name", "").lower()
        if codec in self.image_video_codecs:
            return False
        return codec not in ("h265", "hevc")

    def custom_stream_mapping(self, stream_info: dict, stream_id: int):
        if self.settings.get_setting("advanced"):
            stream_encoding = [f"-c:v:{stream_id}", "hevc_nvenc"]
            stream_encoding += self.settings.get_setting("custom_options").split()
        else:
            stream_encoding = [
                f"-c:v:{stream_id}", "hevc_nvenc",
                f"-profile:v:{stream_id}", self.settings.get_setting("profile"),
                "-preset", self.settings.get_setting("preset"),
            ]  # fmt: skip

        return {
            "stream_mapping": ["-map", f"0:v:{stream_id}"],
            "stream_encoding": stream_encoding,
        }

    def generate_default_nvdec_args(self):
        """Configure NVDEC HW-accelerated decoding args.

        When the user has enabled `hw_decoding`, this sets `-hwaccel cuda
        -hwaccel_device <id>`. When `hw_output_format_cuda` is also on
        (default), it additionally sets `-hwaccel_output_format cuda` so the
        decoded surfaces stay in GPU memory rather than round-tripping to
        system RAM before NVENC re-encodes them.
        """
        if not self.settings.get_setting("hw_decoding"):
            return

        # Device id is hardcoded; see docs/ToDo.md for the planned config option.
        dev_id = "0"
        generic_kwargs = {
            "-hwaccel": "cuda",
            "-hwaccel_device": dev_id,
        }
        if self.settings.get_setting("hw_output_format_cuda"):
            generic_kwargs["-hwaccel_output_format"] = "cuda"
        self.set_ffmpeg_generic_options(**generic_kwargs)


def _build_settings(data):
    if data.get("library_id"):
        return Settings(library_id=data.get("library_id"))
    return Settings()


def _apply_output_container(data, settings, mapper):
    """Set the mapper's output file, optionally remuxing to a new container."""
    if settings.get_setting("keep_container"):
        mapper.set_output_file(data.get("file_out"))
        return

    container_extension = settings.get_setting("dest_container")
    split_file_out = os.path.splitext(data.get("file_out"))
    new_file_out = f"{split_file_out[0]}.{container_extension.lstrip('.')}"
    mapper.set_output_file(new_file_out)
    data["file_out"] = new_file_out


def _apply_options(settings, mapper):
    """Apply either the advanced (free-text) or simple (form-driven) options."""
    if settings.get_setting("advanced"):
        main_options = settings.get_setting("main_options").split()
        if main_options:
            mapper.main_options = main_options
        advanced_options = settings.get_setting("advanced_options").split()
        if advanced_options:
            mapper.advanced_options = advanced_options
        return

    advanced_kwargs = {
        "-max_muxing_queue_size": str(settings.get_setting("max_muxing_queue_size")),
    }
    # NVENC is GPU-bound; spawning more ffmpeg threads gains little and
    # eats CPU headroom that parallel workers need. `slow`/`lossless`
    # presets stay single-threaded to maximise per-frame quality.
    if settings.get_setting("preset") in ("fast", "medium"):
        advanced_kwargs["-threads"] = "2"
    else:
        advanced_kwargs["-threads"] = "1"
    mapper.set_ffmpeg_advanced_options(**advanced_kwargs)


def _finalize_command(data, mapper, probe):
    """Materialise the assembled ffmpeg args and progress parser onto `data`."""
    ffmpeg_args = mapper.get_ffmpeg_args()
    data["exec_command"] = ["ffmpeg", *ffmpeg_args]

    parser = Parser(logger)
    parser.set_probe(probe)
    data["command_progress_parser"] = parser.parse_progress


def on_library_management_file_test(data):
    """Library-test hook: flag files whose video streams need transcoding."""
    abspath = data.get("path")

    probe = Probe(logger, allowed_mimetypes=["video"])
    if not probe.file(abspath):
        return data

    settings = _build_settings(data)

    mapper = PluginStreamMapper()
    mapper.set_settings(settings)
    mapper.set_probe(probe)

    # Log basenames at debug to limit accidental path disclosure if Unmanic's
    # log files are shared. Full path is still available via Unmanic's own
    # task records.
    name = os.path.basename(abspath) if abspath else "<unknown>"
    if mapper.streams_need_processing():
        data["add_file_to_pending_tasks"] = True
        logger.debug("File '%s' should be added to task list.", name)
    else:
        logger.debug("File '%s' does not contain streams requiring processing.", name)

    return data


def on_worker_process(data):
    """Worker hook: build the hevc_nvenc ffmpeg command for the worker."""
    data["exec_command"] = []
    data["repeat"] = False

    abspath = data.get("file_in")

    probe = Probe(logger, allowed_mimetypes=["video"])
    if not probe.file(abspath):
        return data

    settings = _build_settings(data)

    mapper = PluginStreamMapper()
    mapper.set_settings(settings)
    mapper.set_probe(probe)

    if not mapper.streams_need_processing():
        return data

    mapper.set_input_file(abspath)
    _apply_output_container(data, settings, mapper)
    mapper.generate_default_nvdec_args()
    _apply_options(settings, mapper)
    _finalize_command(data, mapper, probe)

    return data
