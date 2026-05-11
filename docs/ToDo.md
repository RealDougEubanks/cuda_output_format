<!--
doc: TODO
last-refreshed: 2026-05-11
-->

# ToDo

Tracked work items that aren't worth a Jira/Issue but shouldn't be lost.

## Plugin features

- **Device-id discovery.** `PluginStreamMapper.generate_default_nvdec_args` hard-codes `-hwaccel_device 0`. Once Unmanic exposes GPU enumeration (or we add a settings option to pick the device), replace the literal `"0"` with the configured value. Inherited from the upstream plugin's TODO.

## Distribution

- **Submit upstream PR.** Open a PR against `Josh5/unmanic.plugin.encoder_video_hevc_nvenc` adding `-hwaccel_output_format cuda` behind a settings toggle. If merged, archive this fork in favor of upstream.
