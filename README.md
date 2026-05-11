<!--
doc: README
last-refreshed: 2026-05-11
generated-by: doc-refresh skill
-->

# CUDA Output Format Injector — Unmanic Plugin

> **SECURITY:** This plugin runs inside an Unmanic worker process and
> only mutates an in-memory `data['exec_command']` list. It opens no
> network connections, reads no user files, and handles no
> credentials. Report any security concern privately — see
> [`SECURITY.md`](./SECURITY.md).

An [Unmanic](https://docs.unmanic.app) plugin that adds
`-hwaccel_output_format cuda` to any ffmpeg command that already uses
`-hwaccel cuda`. This keeps NVDEC-decoded frames in GPU memory so
NVENC re-encodes them without a round-trip through system RAM,
dropping per-worker CPU use by roughly one busy core.

- **Plugin id:** `cuda_output_format`
- **Hook:** `on_worker_process` (priority `200` — runs late)
- **Dependencies:** Python 3 standard library only

## What it does

Given an ffmpeg command like:

```
ffmpeg ... -hwaccel cuda -hwaccel_device 0 -i input.mp4 ... -c:v hevc_nvenc ...
```

the plugin rewrites it to:

```
ffmpeg ... -hwaccel cuda -hwaccel_device 0 -hwaccel_output_format cuda -i input.mp4 ... -c:v hevc_nvenc ...
```

If `-hwaccel cuda` isn't in the command, nothing is changed. Running
the hook twice on the same command does not double-insert the flag.

## Why it matters

Without `-hwaccel_output_format cuda`, ffmpeg downloads each NVDEC-decoded
frame from the GPU to system RAM and then re-uploads it to the GPU for
NVENC. That round-trip burns ~70% of a CPU core per worker and limits
throughput. Adding the flag keeps the whole pipeline on the GPU.

## Install

### Option 1 — Add as a custom Unmanic plugin repository (easiest)

In the Unmanic web UI:

1. **Settings → Plugins → Repos → +** (Add a new repository).
2. Paste this URL:
   ```
   https://raw.githubusercontent.com/RealDougEubanks/cuda_output_format/repo/repo.json
   ```
3. **Settings → Plugins** — *CUDA Output Format Injector* will now appear in the list. Click **Install**.
4. Add it to your library's Plugin Flow (see step 3 of Option 2 below — same workflow).

The `repo` branch is rebuilt automatically by GitHub Actions on every push to `main`, so installs always pull the current published version.

### Option 2 — Manual install

```bash
cd /config/.unmanic/userdata/plugins/
git clone https://github.com/RealDougEubanks/cuda_output_format.git cuda_output_format
```

The destination folder name **must** be `cuda_output_format` — it has
to match the plugin id in `info.json`.

Then in the Unmanic web UI:

1. **Settings → Plugins → Local** — find *CUDA Output Format Injector*
   and click **Install**.
2. Open the library you want it on: **Libraries → \<your library\> →
   Plugin Flow**.
3. Drag *CUDA Output Format Injector* so it sits **after** the plugin
   that builds your ffmpeg command (typically *Transcode Video Files*
   / `video_transcoder`). Order matters — this plugin only edits an
   already-assembled command.
4. Save and run a test job.

### Option 3 — Download a zip

Grab the latest source zip from the
[Releases](https://github.com/RealDougEubanks/cuda_output_format/releases)
page and extract it into
`/config/.unmanic/userdata/plugins/cuda_output_format/` so that
`plugin.py` and `info.json` sit at the top of that folder.

## Verify

After a test transcode, open the worker's command log in the Unmanic
UI. You should see `-hwaccel_output_format cuda` in the assembled
command. CPU usage per worker should drop noticeably during the encode.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Plugin not visible in Unmanic UI | Folder name does not match `info.json` `id` | Rename the install folder to exactly `cuda_output_format`. |
| `-hwaccel_output_format cuda` never appears in command | This plugin runs **before** the plugin that adds `-hwaccel cuda` | In **Library → Plugin Flow**, drag this plugin **below** *Transcode Video Files* (or whatever adds `-hwaccel cuda`). |
| Flag appears but CPU is still high | NVDEC fallback to software decode (e.g., codec not supported by your GPU) | Check the worker log for `Cannot load nvcuvid` or similar — the source codec/profile may not have NVDEC support on your hardware. |
| `Skipping injection: ...` warning in logs | `exec_command` was passed in an unexpected shape | Open an issue with the warning message and the relevant worker log lines. |

## Repository layout

```
.
├── plugin.py             # the hook implementation
├── info.json             # Unmanic plugin manifest
├── description.md        # long-form description shown in the Unmanic UI
├── changelog.md          # version history
├── requirements.txt      # empty — runtime uses stdlib only
├── requirements-dev.txt  # pytest + ruff for local development
├── pyproject.toml        # ruff + pytest config
├── tests/                # pytest suite
├── docs/                  # assumptions and design notes
├── CONTRIBUTING.md       # development workflow
├── README.md             # this file
└── LICENSE               # MIT
```

## Development

See [CONTRIBUTING.md](./CONTRIBUTING.md) for the dev workflow. In short:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

## Compatibility

Declares compatibility with Unmanic plugin API levels `1` and `2`
(see `info.json`). The plugin makes no assumptions about which
encoder/decoder plugin assembled the command — it only inspects and
edits `data['exec_command']`. Compatibility is verified manually
against the current Unmanic release; the automated CI runs the unit
tests under Python 3.10, 3.11, and 3.12 but does not exercise the
Unmanic runtime.

## License

MIT — see [LICENSE](./LICENSE).
