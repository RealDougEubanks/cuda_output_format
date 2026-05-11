
---

### About

This plugin adds the `-hwaccel_output_format cuda` flag to any ffmpeg
command that is already using NVDEC hardware-accelerated decoding
(`-hwaccel cuda`). Without this flag, ffmpeg downloads each decoded
frame from the GPU to system RAM and then re-uploads it to the GPU for
NVENC — a needless round-trip that burns roughly one CPU core per
worker.

With the flag in place the decoded frames stay in GPU memory for the
whole pipeline, so the worker's CPU footprint drops dramatically and
throughput goes up.

### How it works

* Hooks `on_worker_process` at priority **200** (runs late).
* Inspects `data['exec_command']`.
* If the args contain `-hwaccel cuda` and do not already contain
  `-hwaccel_output_format`, it inserts `-hwaccel_output_format cuda`
  immediately after the `-hwaccel_device` value (or after `-hwaccel
  cuda` if no device is set), keeping the flag before `-i <input>`.
* Idempotent — running twice produces the same command.
* Defensive — if `exec_command` is missing, malformed, or any
  unexpected error occurs, the plugin logs a warning under
  `unmanic.plugin.cuda_output_format` and returns the original
  command untouched. A plugin failure must never break a transcode.

### Ordering

This plugin **must run after** whichever plugin adds `-hwaccel cuda`
to your command. In a typical setup that is *Transcode Video Files*
(`video_transcoder`). Make sure *CUDA Output Format Injector* sits
below it in your library's Plugin Flow.

### Verifying

Run a test transcode and open the worker's command log in the Unmanic
UI. You should see `-hwaccel_output_format cuda` in the assembled
command, and CPU usage per worker should fall noticeably during the
encode.
