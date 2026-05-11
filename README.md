# CUDA Output Format Injector — Unmanic Plugin

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

### Option 1 — Manual install (recommended for a single plugin)

```bash
cd /config/.unmanic/userdata/plugins/
git clone https://github.com/RealDougEubanks/unmanic.plugin.cuda_output_format.git cuda_output_format
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

### Option 2 — Download a zip

Grab the latest source zip from the
[Releases](https://github.com/RealDougEubanks/unmanic.plugin.cuda_output_format/releases)
page and extract it into
`/config/.unmanic/userdata/plugins/cuda_output_format/` so that
`plugin.py` and `info.json` sit at the top of that folder.

## Verify

After a test transcode, open the worker's command log in the Unmanic
UI. You should see `-hwaccel_output_format cuda` in the assembled
command. CPU usage per worker should drop noticeably during the encode.

## Repository layout

```
.
├── plugin.py        # the hook implementation + self-tests
├── info.json        # Unmanic plugin manifest
├── description.md   # long-form description shown in the Unmanic UI
├── changelog.md     # version history
├── requirements.txt # empty — stdlib only
├── README.md        # this file
└── LICENSE          # MIT
```

`plugin.py` has a small self-test block; you can run it directly:

```bash
python3 plugin.py
# All assertions passed.
```

## Compatibility

Tested against Unmanic plugin compatibility levels `1` and `2`. The
plugin makes no assumptions about which encoder/decoder plugin
assembled the command — it only inspects and edits `data['exec_command']`.

## License

MIT — see [LICENSE](./LICENSE).
