
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
