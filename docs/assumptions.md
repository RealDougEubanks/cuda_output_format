<!--
doc: ASSUMPTIONS
last-refreshed: 2026-05-11
generated-by: doc-refresh skill
-->

# Assumptions

Non-obvious decisions in `encoder_video_hevc_nvenc_gpu`.

---

- **Assumption:** `-hwaccel_output_format cuda` is only meaningful when `-hwaccel cuda` is already set, so the new `hw_output_format_cuda` setting is hidden in the UI unless `hw_decoding` is also enabled and defaults to **on**.
- **Why:** A user enabling NVDEC decoding almost always wants the full GPU pipeline. Exposing the toggle as off-by-default would put us in the same place as upstream (slow). Hiding it when NVDEC is off prevents misconfigurations like setting `-hwaccel_output_format cuda` without `-hwaccel cuda` (ffmpeg error).
- **Recorded by:** Doug Eubanks
- **Date:** 2026-05-11

---

- **Assumption:** The vendored `lib/ffmpeg/` directory is a snapshot of `Josh5/unmanic.plugin.helpers.ffmpeg` at commit `e061f527e4d5e6068b6e4c7395edcde2cdd07c37`, vendored rather than referenced as a git submodule.
- **Why:** Submodules force every install path (manual clone, repo URL, zip download) to handle a second repo. Vendoring keeps `pip install` and `git clone` single-step. Trade-off: we have to manually re-sync if upstream pushes important fixes. Acceptable because the helpers module changes rarely.
- **Recorded by:** Doug Eubanks
- **Date:** 2026-05-11

---

- **Assumption:** The plugin id `encoder_video_hevc_nvenc_gpu` is intentionally distinct from upstream's `encoder_video_hevc_nvenc` so both can coexist on the same Unmanic install.
- **Why:** Plugin id collisions break Unmanic's plugin manager. Users may want to A/B test this fork against upstream before committing to it. A unique id is the cheapest way to allow that.
- **Recorded by:** Doug Eubanks
- **Date:** 2026-05-11

---

- **Assumption:** Errors during NVDEC arg generation are non-fatal — if `generate_default_nvdec_args` would throw, the worker still has a valid (software-decode) ffmpeg command and the transcode proceeds.
- **Why:** A plugin bug should degrade to "slower transcode," never a failed transcode. This mirrors the safety stance documented in the upstream plugin.
- **Recorded by:** Doug Eubanks
- **Date:** 2026-05-11
