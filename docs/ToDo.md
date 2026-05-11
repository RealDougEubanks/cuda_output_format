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

- ~~**Submit upstream PR for the GPU-pipeline feature.** Open a PR against `Josh5/unmanic.plugin.encoder_video_hevc_nvenc` adding `-hwaccel_output_format cuda` behind a settings toggle.~~ — **Not actionable:** the upstream encoder repository is archived (read-only). This fork is the active line of development going forward.

- **File hardening issue against `Josh5/unmanic.plugin.helpers.ffmpeg`.** That repo is still open and accepting issues. The `eval()` removal we shipped in v1.1.0 (replacement with `fractions.Fraction`) should be proposed upstream as a defense-in-depth fix so other plugins vendoring this helper benefit. Frame as hardening, not RCE — no working exploit was demonstrated; the issue is that `eval` on parsed data is the kind of code that becomes exploitable as soon as adjacent assumptions change.
