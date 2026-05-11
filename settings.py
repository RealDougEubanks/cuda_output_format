"""Settings + form configuration for encoder_video_hevc_nvenc_gpu.

Split out of plugin.py to keep the plugin entry point focused on the
hook runners and stream-mapping logic. Re-exported from plugin.py so
Unmanic's plugin loader still discovers the `Settings` class via the
plugin module's namespace.
"""

from unmanic.libs.unplugins.settings import PluginSettings


class Settings(PluginSettings):
    settings = {
        "hw_decoding": False,
        "hw_output_format_cuda": True,
        "advanced": False,
        "preset": "fast",
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
            "hw_decoding": self._form_hw_decoding(),
            "hw_output_format_cuda": self._form_hw_output_format_cuda(),
            "max_muxing_queue_size": self._form_max_muxing_queue_size(),
            "preset": self._form_preset(),
            "profile": self._form_profile(),
            "main_options": self._form_main_options(),
            "advanced_options": self._form_advanced_options(),
            "custom_options": self._form_custom_options(),
            "keep_container": {
                "label": "Keep the same container",
            },
            "dest_container": self._form_dest_container(),
        }

    def _form_hw_decoding(self):
        return {
            "label": "Enable NVDEC HW Accelerated Decoding?",
            "input_type": "checkbox",
        }

    def _form_hw_output_format_cuda(self):
        values = {
            "label": "Keep decoded frames in GPU memory (-hwaccel_output_format cuda)",
            "input_type": "checkbox",
        }
        if not self.get_setting("hw_decoding"):
            values["display"] = "hidden"
        return values

    def _form_max_muxing_queue_size(self):
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

    def _form_preset(self):
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

    def _form_profile(self):
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

    def _form_main_options(self):
        values = {
            "label": "Write your own custom main options",
            "input_type": "textarea",
        }
        if not self.get_setting("advanced"):
            values["display"] = "hidden"
        return values

    def _form_advanced_options(self):
        values = {
            "label": "Write your own custom advanced options",
            "input_type": "textarea",
        }
        if not self.get_setting("advanced"):
            values["display"] = "hidden"
        return values

    def _form_custom_options(self):
        values = {
            "label": "Write your own custom video options",
            "input_type": "textarea",
        }
        if not self.get_setting("advanced"):
            values["display"] = "hidden"
        return values

    def _form_dest_container(self):
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
