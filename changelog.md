
**1.1.0**

- Default `preset` changed from `medium` → `fast`. NVENC's `fast`
  preset is the documented recommended setting for transcoding
  throughput; the quality delta versus `medium` is minor and the
  throughput delta is large. Users wanting max quality can still
  pick `slow` or `lossless` from the preset dropdown.
- Default simple-mode thread count for `fast`/`medium` presets
  changed from `4` → `2`. NVENC is GPU-bound; spawning four ffmpeg
  threads gained little and ate CPU headroom that parallel workers
  need. `slow`/`lossless` presets continue to run single-threaded.
- No new settings; no schema changes. Existing installations pick up
  the new defaults only for fields the user hasn't customised.

**1.0.0**

- Initial release of `encoder_video_hevc_nvenc_gpu` — a fork of
  [Josh5/unmanic.plugin.encoder_video_hevc_nvenc](https://github.com/Josh5/unmanic.plugin.encoder_video_hevc_nvenc)
  at commit `master`.
- Adds `-hwaccel_output_format cuda` to the NVDEC argument set when
  HW decoding is enabled, so decoded frames stay in GPU memory all the
  way through to NVENC. Gated by a new "Keep decoded frames in GPU
  memory" setting (default **on**) so the behavior can be disabled
  without losing NVDEC decode.
- Vendored `lib/ffmpeg/` from upstream's
  `Josh5/unmanic.plugin.helpers.ffmpeg` submodule at commit
  `e061f527e4d5e6068b6e4c7395edcde2cdd07c37`.
- New plugin id `encoder_video_hevc_nvenc_gpu` to avoid colliding with
  upstream when both are installed.
- Adds CI, weekly security scans (pip-audit + bandit), automated
  release zip + Unmanic-repo branch publishing, and a vulnerability
  disclosure policy. See `.github/workflows/` and `SECURITY.md`.
