
**0.1.0**

- Initial release.
- Implements `on_worker_process` at priority 200.
- Injects `-hwaccel_output_format cuda` after `-hwaccel_device <n>` (or
  after `-hwaccel cuda` if no device is specified) when the assembled
  ffmpeg command uses NVDEC.
- Idempotent and defensive — tolerates `exec_command` being a list or
  a string, and never raises.
