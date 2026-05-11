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

from encoder_video_hevc_nvenc_gpu.lib.ffmpeg import Parser, Probe, StreamMapper
from unmanic.libs.unplugins.settings import PluginSettings

logger = logging.getLogger("Unmanic.Plugin.encoder_video_hevc_nvenc_gpu")


class Settings(PluginSettings):
    settings = {
        "hw_decoding": False,
        "hw_output_format_cuda": True,
        "advanced": False,
        "preset": "medium",
        "profile": "main",
        "max_muxing_queue_size": 2048,
        "main_options": "-threads 2\n",
        "advanced_options": "-strict -2\n" "-max_muxing_queue_size 2048\n",
        "custom_options": "-preset medium\n"
        "-profile:v main\n"
        "-pix_fmt p010le\n"
        "-rc:v vbr_hq\n"
        "-qmin 0\n"
        "-rc-lookahead 32\n"
        "-spatial_aq:v 1\n"
        "-aq-strength:v 8\n"
        "-a53cc 0\n"
        "-b:v:0 4M\n",
        "keep_container": True,
        "dest_container": "mkv",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_settings = {
            "advanced": {
                "label": "Write your own FFmpeg params",
            },
            "hw_decoding": self.__set_hw_decoding_checkbox_form_settings(),
            "hw_output_format_cuda": self.__set_hw_output_format_cuda_form_settings(),
            "max_muxing_queue_size": self.__set_max_muxing_queue_size_form_settings(),
            "preset": self.__set_preset_form_settings(),
            "profile": self.__set_profile_form_settings(),
            "main_options": self.__set_main_options_form_settings(),
            "advanced_options": self.__set_advanced_options_form_settings(),
            "custom_options": self.__set_custom_options_form_settings(),
            "keep_container": {
                "label": "Keep the same container",
            },
            "dest_container": self.__set_destination_container(),
        }

    def __set_hw_decoding_checkbox_form_settings(self):
        return {
            "label": "Enable NVDEC HW Accelerated Decoding?",
            "input_type": "checkbox",
        }

    def __set_hw_output_format_cuda_form_settings(self):
        values = {
            "label": "Keep decoded frames in GPU memory (-hwaccel_output_format cuda)",
            "input_type": "checkbox",
        }
        # Only meaningful when HW decoding is on.
        if not self.get_setting("hw_decoding"):
            values["display"] = "hidden"
        return values

    def __set_max_muxing_queue_size_form_settings(self):
        values = {
            "label": "Max input stream packet buffer",
            "input_type": "slider",
            "slider_options": {
                "min": 1024,
                "max": 10240,
            },
        }
        if self.get_setting("advanced"):
            values["display"] = "hidden"
        return values

    def __set_preset_form_settings(self):
        values = {
            "label": "NVENC Encoder Quality Preset",
            "input_type": "select",
            "select_options": [
                {"value": "fast", "label": "Fast"},
                {"value": "medium", "label": "Medium"},
                {"value": "slow", "label": "Slow"},
                {"value": "lossless", "label": "Lossless (slowest)"},
            ],
        }
        if self.get_setting("advanced"):
            values["display"] = "hidden"
        return values

    def __set_profile_form_settings(self):
        values = {
            "label": "Profile",
            "input_type": "select",
            "select_options": [
                {"value": "main", "label": "Main"},
                {"value": "main10", "label": "Main10"},
                {"value": "rext", "label": "Range Extended"},
            ],
        }
        if self.get_setting("advanced"):
            values["display"] = "hidden"
        return values

    def __set_main_options_form_settings(self):
        values = {
            "label": "Write your own custom main options",
            "input_type": "textarea",
        }
        if not self.get_setting("advanced"):
            values["display"] = "hidden"
        return values

    def __set_advanced_options_form_settings(self):
        values = {
            "label": "Write your own custom advanced options",
            "input_type": "textarea",
        }
        if not self.get_setting("advanced"):
            values["display"] = "hidden"
        return values

    def __set_custom_options_form_settings(self):
        values = {
            "label": "Write your own custom video options",
            "input_type": "textarea",
        }
        if not self.get_setting("advanced"):
            values["display"] = "hidden"
        return values

    def __set_destination_container(self):
        values = {
            "label": "Set the output container",
            "input_type": "select",
            "select_options": [
                {"value": "mkv", "label": ".mkv - Matroska"},
                {"value": "avi", "label": ".avi - AVI (Audio Video Interleaved)"},
                {"value": "mov", "label": ".mov - QuickTime / MOV"},
                {"value": "mp4", "label": ".mp4 - MP4 (MPEG-4 Part 14)"},
            ],
        }
        if self.get_setting("keep_container"):
            values["display"] = "hidden"
        return values


class PluginStreamMapper(StreamMapper):
    image_video_codecs = [
        "alias_pix",
        "apng",
        "brender_pix",
        "dds",
        "dpx",
        "exr",
        "fits",
        "gif",
        "mjpeg",
        "mjpegb",
        "pam",
        "pbm",
        "pcx",
        "pfm",
        "pgm",
        "pgmyuv",
        "pgx",
        "photocd",
        "pictor",
        "pixlet",
        "png",
        "ppm",
        "ptx",
        "sgi",
        "sunrast",
        "tiff",
        "vc1image",
        "wmv3image",
        "xbm",
        "xface",
        "xpm",
        "xwd",
    ]

    def __init__(self):
        super().__init__(logger, ["video"])
        self.settings = None

    def set_settings(self, settings):
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
                f"-c:v:{stream_id}",
                "hevc_nvenc",
                f"-profile:v:{stream_id}",
                self.settings.get_setting("profile"),
                "-preset",
                self.settings.get_setting("preset"),
            ]

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

        # TODO: discover device id from a config option once Unmanic exposes
        # GPU enumeration.
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

    if mapper.streams_need_processing():
        data["add_file_to_pending_tasks"] = True
        logger.debug("File '%s' should be added to task list.", abspath)
    else:
        logger.debug("File '%s' does not contain streams requiring processing.", abspath)

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

    if settings.get_setting("keep_container"):
        mapper.set_output_file(data.get("file_out"))
    else:
        container_extension = settings.get_setting("dest_container")
        split_file_out = os.path.splitext(data.get("file_out"))
        new_file_out = f"{split_file_out[0]}.{container_extension.lstrip('.')}"
        mapper.set_output_file(new_file_out)
        data["file_out"] = new_file_out

    mapper.generate_default_nvdec_args()

    if settings.get_setting("advanced"):
        main_options = settings.get_setting("main_options").split()
        if main_options:
            mapper.main_options = main_options
        advanced_options = settings.get_setting("advanced_options").split()
        if advanced_options:
            mapper.advanced_options = advanced_options
    else:
        advanced_kwargs = {
            "-max_muxing_queue_size": str(settings.get_setting("max_muxing_queue_size")),
        }
        if settings.get_setting("preset") in ("fast", "medium"):
            advanced_kwargs["-threads"] = "4"
        else:
            advanced_kwargs["-threads"] = "1"
        mapper.set_ffmpeg_advanced_options(**advanced_kwargs)

    ffmpeg_args = mapper.get_ffmpeg_args()

    data["exec_command"] = ["ffmpeg", *ffmpeg_args]

    parser = Parser(logger)
    parser.set_probe(probe)
    data["command_progress_parser"] = parser.parse_progress

    return data
