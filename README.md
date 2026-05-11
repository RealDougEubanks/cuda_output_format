<!--
doc: README
last-refreshed: 2026-05-11
generated-by: doc-refresh skill
-->

# Video Encoder H265/HEVC - hevc_nvenc (GPU Pipeline) — Unmanic Plugin

> **Friendly fork of [Josh5/unmanic.plugin.encoder_video_hevc_nvenc](https://github.com/Josh5/unmanic.plugin.encoder_video_hevc_nvenc)** — all credit for the original plugin goes to Josh Sunnex ([@Josh5](https://github.com/Josh5)). This fork adds a single feature: `-hwaccel_output_format cuda` so decoded frames stay in GPU memory.

This Unmanic plugin transcodes video streams to H265/HEVC using the `hevc_nvenc` encoder. When NVDEC hardware-accelerated decoding is enabled, it now also adds `-hwaccel_output_format cuda` — the missing flag that keeps decoded frames in GPU memory for the entire NVDEC → NVENC pipeline. Result: substantially lower CPU per worker and higher transcode throughput on full GPU transcodes.

## Why does this fork exist?

The upstream plugin doesn't add `-hwaccel_output_format cuda`, so each decoded frame round-trips from GPU to system RAM and back, burning roughly one CPU core per worker. [Upstream issue #1](https://github.com/Josh5/unmanic.plugin.encoder_video_hevc_nvenc/issues/1) has tracked related ordering problems since October 2024 without a maintainer response, so this fork ships the fix in the meantime.

**Relationship to upstream:** if Josh merges the equivalent change upstream (a PR is welcome — see [docs/ToDo.md](./docs/ToDo.md)), this fork will be archived in favor of the canonical plugin. We're not competing; we're patching forward until the original moves.

> **SECURITY:** This plugin runs inside an Unmanic worker process. It probes media files with `ffprobe` and constructs an ffmpeg argument list. It does not open network connections, write secrets to disk, or handle credentials. Report any concern privately — see [`SECURITY.md`](./SECURITY.md).

- **Plugin id:** `encoder_video_hevc_nvenc_gpu`
- **Hooks:** `on_library_management_file_test`, `on_worker_process`
- **Dependencies:** Python 3 standard library; Unmanic's plugin runtime
- **License:** GPL-3.0 (inherited from the upstream plugin)

## What's different from upstream

Upstream's NVDEC branch only sets:

```
-hwaccel cuda -hwaccel_device 0
```

Without `-hwaccel_output_format cuda`, ffmpeg downloads each NVDEC-decoded frame from the GPU into system RAM and re-uploads it to the GPU for NVENC. That round-trip burns roughly one CPU core per worker and caps throughput.

This fork adds:

```
-hwaccel cuda -hwaccel_device 0 -hwaccel_output_format cuda
```

The flag is gated on a new toggle (**"Keep decoded frames in GPU memory"**) that defaults to **on**, but you can disable it without losing NVDEC decoding.

A PR submitting this change to upstream is welcome — when/if upstream merges it, this fork can be archived.

## Install

### Option 1 — Add as a custom Unmanic plugin repository (easiest)

1. **Settings → Plugins → Repos → +** (Add a new repository).
2. Paste this URL:
   ```
   https://raw.githubusercontent.com/RealDougEubanks/unmanic.plugin.encoder_video_hevc_nvenc_gpu/repo/repo.json
   ```
3. **Settings → Plugins** — *Video Encoder H265/HEVC - hevc_nvenc (GPU Pipeline)* will appear in the list. Click **Install**.
4. Add it to your library's **Plugin Flow** (replace or sit alongside the upstream encoder).

The `repo` branch is rebuilt automatically by GitHub Actions on every push to `main`, so installs always pull the current published version.

### Option 2 — Manual install

```bash
cd /config/.unmanic/userdata/plugins/
git clone https://github.com/RealDougEubanks/unmanic.plugin.encoder_video_hevc_nvenc_gpu.git encoder_video_hevc_nvenc_gpu
```

The destination folder name **must** be `encoder_video_hevc_nvenc_gpu` to match the plugin id in `info.json`.

Then in the Unmanic UI: **Settings → Plugins → Local** → find the plugin → click **Install** → add it to your library's Plugin Flow.

### Option 3 — Download a zip

Grab the latest `encoder_video_hevc_nvenc_gpu-X.Y.Z.zip` from the [Releases](https://github.com/RealDougEubanks/unmanic.plugin.encoder_video_hevc_nvenc_gpu/releases) page and extract it into `/config/.unmanic/userdata/plugins/encoder_video_hevc_nvenc_gpu/` so that `plugin.py` and `info.json` sit at the top of that folder.

## Configure

In the plugin's settings page in Unmanic:

| Setting | Default | Purpose |
|---------|---------|---------|
| Enable NVDEC HW Accelerated Decoding | **off** | Turns on `-hwaccel cuda -hwaccel_device 0`. Required for the GPU pipeline. |
| Keep decoded frames in GPU memory | **on** (when HW decoding is on) | Adds `-hwaccel_output_format cuda`. The whole point of this fork. |
| NVENC Encoder Quality Preset | fast | Speed/compression trade-off. `fast` is the NVENC-recommended throughput default; pick `slow` for max quality. |
| Profile | main | 8-bit / 10-bit / Range Extended. |
| Max input stream packet buffer | 2048 | ffmpeg's `-max_muxing_queue_size`. |
| Keep the same container | on | Off = remux to the configured container. |
| Write your own FFmpeg params | off | Advanced override mode. |

## Verify

After a test transcode, open the worker's command log in the Unmanic UI. With both settings on, you should see the full GPU pipeline:

```
ffmpeg ... -hwaccel cuda -hwaccel_device 0 -hwaccel_output_format cuda -i ...
```

CPU usage per worker should drop noticeably during the encode versus the upstream encoder.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Plugin not visible in Unmanic UI | Folder name does not match `info.json` `id` | Rename the install folder to exactly `encoder_video_hevc_nvenc_gpu`. |
| `-hwaccel_output_format cuda` missing in command | "Keep decoded frames in GPU memory" toggle is off, or HW decoding is off | Enable both toggles in the plugin's settings page. |
| `Cannot load nvcuvid` in ffmpeg output | Source codec/profile not supported by NVDEC on your GPU | ffmpeg falls back to software decode; the `-hwaccel_output_format` flag is moot in that case. Check your NVIDIA GPU's [decode matrix](https://developer.nvidia.com/video-encode-and-decode-gpu-support-matrix-new). |
| ffmpeg error about pixel format mismatch | Some 10-bit sources can't be passed straight to NVENC without conversion | Either disable HW decoding for that source, or set the encoder profile to `main10`. |

## Repository layout

```
.
├── plugin.py                 # patched fork of upstream
├── info.json                 # Unmanic plugin manifest
├── description.md            # long-form description shown in the Unmanic UI
├── changelog.md              # version history (this fork)
├── icon.png                  # plugin icon (from upstream)
├── requirements.txt          # empty — runtime uses stdlib only
├── requirements-dev.txt      # pytest + ruff + scanners for local development
├── pyproject.toml            # ruff + pytest config
├── lib/ffmpeg/               # vendored from upstream's helpers.ffmpeg submodule
├── tests/                    # pytest suite
├── docs/                     # assumptions and design notes
├── .github/workflows/        # CI, security scan, repo publish, release
├── SECURITY.md               # vulnerability disclosure policy
├── CONTRIBUTING.md           # development workflow
├── README.md                 # this file
└── LICENSE                   # GPL-3.0 (inherited)
```

## Development

See [CONTRIBUTING.md](./CONTRIBUTING.md). In short:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

CI runs `ruff check`, `ruff format --check`, `pytest`, and `pip-audit` on Python 3.10–3.12.

## Source code

This repository is the complete corresponding source for the
installable plugin zip, per [GPL-3.0 §6](https://www.gnu.org/licenses/gpl-3.0.html#section6).
Each release on the [Releases](https://github.com/RealDougEubanks/unmanic.plugin.encoder_video_hevc_nvenc_gpu/releases)
page mirrors this repository's contents at the matching `vX.Y.Z` tag.

## License & Credits

GPL-3.0 — see [LICENSE](./LICENSE).

Forked from [Josh5/unmanic.plugin.encoder_video_hevc_nvenc](https://github.com/Josh5/unmanic.plugin.encoder_video_hevc_nvenc) (Josh Sunnex, 2021). The `lib/ffmpeg/` directory is vendored from [Josh5/unmanic.plugin.helpers.ffmpeg](https://github.com/Josh5/unmanic.plugin.helpers.ffmpeg) at commit `e061f527`.
