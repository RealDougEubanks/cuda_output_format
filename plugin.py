"""
cuda_output_format
==================

Unmanic plugin that injects `-hwaccel_output_format cuda` into ffmpeg
commands which already use NVDEC hardware-accelerated decoding
(`-hwaccel cuda`). Keeping decoded frames in GPU memory avoids a
round-trip through system RAM before NVENC re-encodes them, cutting
per-worker CPU usage significantly.

This plugin only mutates `data['exec_command']` during the
`on_worker_process` hook and is intentionally idempotent.
"""

import logging
from typing import Any, List, Mapping, MutableMapping

logger = logging.getLogger("unmanic.plugin.cuda_output_format")


class CudaOutputFormatError(Exception):
    """Base error for the cuda_output_format plugin."""


class InvalidExecCommandError(CudaOutputFormatError):
    """Raised when `data['exec_command']` is not a list[str] or str."""


def _inject_output_format(args: List[str]) -> List[str]:
    """Return a new list of ffmpeg args with `-hwaccel_output_format cuda`
    inserted at the correct position.

    The input is returned unchanged when:
      - `-hwaccel` is absent, or its value is not `cuda`
      - `-hwaccel_output_format` is already present (idempotent)

    Raises:
      TypeError: if `args` is not a list.
    """
    if not isinstance(args, list):
        raise TypeError(f"args must be a list, got {type(args).__name__}")

    if "-hwaccel" not in args:
        return args

    hwaccel_idx = args.index("-hwaccel")
    if hwaccel_idx + 1 >= len(args) or args[hwaccel_idx + 1] != "cuda":
        return args

    if "-hwaccel_output_format" in args:
        return args

    # Insert after `-hwaccel_device <val>` if present, otherwise after
    # `-hwaccel cuda`. See docs/assumptions.md for ordering rationale.
    if "-hwaccel_device" in args:
        device_idx = args.index("-hwaccel_device")
        insert_at = min(device_idx + 2, len(args))
    else:
        insert_at = hwaccel_idx + 2

    new_args = list(args)
    new_args[insert_at:insert_at] = ["-hwaccel_output_format", "cuda"]
    return new_args


def _validate_data(data: Any) -> MutableMapping[str, Any]:
    if not isinstance(data, MutableMapping):
        raise InvalidExecCommandError(
            f"data must be a mutable mapping, got {type(data).__name__}"
        )
    return data


def on_worker_process(data: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    try:
        _validate_data(data)
        exec_command = data.get("exec_command")

        if isinstance(exec_command, list):
            data["exec_command"] = _inject_output_format(exec_command)
        elif isinstance(exec_command, str):
            tokens = exec_command.split()
            updated = _inject_output_format(tokens)
            if updated is not tokens:
                data["exec_command"] = " ".join(updated)
        elif exec_command is None:
            logger.debug("exec_command missing; nothing to inject")
        else:
            raise InvalidExecCommandError(
                f"exec_command must be list or str, got {type(exec_command).__name__}"
            )
    except CudaOutputFormatError as exc:
        logger.warning("Skipping injection: %s", exc)
    except Exception:
        logger.exception("Unexpected error in on_worker_process; leaving exec_command unchanged")

    return data
