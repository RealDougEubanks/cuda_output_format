
**0.2.0**

- Replaced silent `except` handlers with a structured error hierarchy
  (`CudaOutputFormatError`, `InvalidExecCommandError`) and a module
  logger under `unmanic.plugin.cuda_output_format`. Unexpected errors
  are now logged; the hook still degrades to a no-op so transcodes are
  never broken by the plugin.
- Validate `data` and `exec_command` types at the plugin boundary.
- Tokenize string `exec_command` values with `shlex` so quoted paths
  containing whitespace round-trip safely.
- Removed the inline `__main__` self-test harness from `plugin.py`;
  tests now live under `tests/` and run with `pytest`.
- Added GitHub Actions CI, `ruff` lint/format config, and a
  `requirements-dev.txt` / `pyproject.toml` for development.

**0.1.0**

- Initial release.
- Implements `on_worker_process` at priority 200.
- Injects `-hwaccel_output_format cuda` after `-hwaccel_device <n>` (or
  after `-hwaccel cuda` if no device is specified) when the assembled
  ffmpeg command uses NVDEC.
- Idempotent.
