<!--
doc: TODO
last-refreshed: 2026-05-11
-->

# ToDo

Tracked work items that aren't worth a Jira/Issue but shouldn't be lost.

## Plugin features

- **Device-id discovery.** `PluginStreamMapper.generate_default_nvdec_args` hard-codes `-hwaccel_device 0`. Once Unmanic exposes GPU enumeration (or we add a settings option to pick the device), replace the literal `"0"` with the configured value. Inherited from the upstream plugin's TODO.
  - **SECURITY:** when wiring the config option, validate the user-supplied value against `^[0-9]+$` (or similar) before it reaches `set_ffmpeg_generic_options`. Without validation an operator could inject extra ffmpeg flags by setting the device id to e.g. `"0 -malicious_flag value"`.

## Distribution

- **Submit upstream PR.** Open a PR against `Josh5/unmanic.plugin.encoder_video_hevc_nvenc` adding `-hwaccel_output_format cuda` behind a settings toggle. If merged, archive this fork in favor of upstream.
