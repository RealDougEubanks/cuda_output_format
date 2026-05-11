
**1.1.0**

- **Hardening:** the vendored `lib/ffmpeg/parser.py` previously
  called `eval()` on the `avg_frame_rate` value reported by
  `ffprobe`. In practice ffprobe's output for that field is
  structurally constrained to `"<int>/<int>"`, so no working
  exploit was demonstrated — but `eval` on parsed data is the kind
  of code that turns into a real vulnerability the moment an
  adjacent assumption changes (a future ffprobe output format,
  a different probe backend, an ffprobe fuzzing finding, etc.).
  Replaced with `fractions.Fraction(...)`, which parses the
  `"num/den"` form natively and rejects everything else as
  `ValueError`. Inherited from upstream
  `Josh5/unmanic.plugin.helpers.ffmpeg`; a hardening issue has been
  filed there.
- **Reliability (Moderate):** `ffprobe` is now invoked with a 60-second
  timeout. Previously a hung NFS mount, a slow network share, or a
  malformed media file could pin a worker thread indefinitely.
- **Correctness (Low):** replaced the brittle `'error' in raw_output`
  substring check in the ffprobe wrapper with `pipe.returncode != 0`
  so legitimate metadata containing the word "error" no longer
  false-positives.
- **Privacy (Info):** file paths in debug-level log lines are now
  basenames rather than full paths, limiting accidental disclosure
  if Unmanic's logs are shared.
- **Supply chain:** release workflow now generates a signed build
  provenance attestation via `actions/attest-build-provenance`,
  visible under the repository's Attestations tab.
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
