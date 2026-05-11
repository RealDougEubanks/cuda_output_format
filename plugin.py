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


def _inject_output_format(args):
    """Return a new list of ffmpeg args with `-hwaccel_output_format cuda`
    inserted in the correct position, or the input unchanged if not
    applicable. Never raises."""
    try:
        if not isinstance(args, list):
            return args

        if "-hwaccel" not in args:
            return args

        hwaccel_idx = args.index("-hwaccel")
        if hwaccel_idx + 1 >= len(args) or args[hwaccel_idx + 1] != "cuda":
            return args

        if "-hwaccel_output_format" in args:
            return args

        if "-hwaccel_device" in args:
            device_idx = args.index("-hwaccel_device")
            insert_at = device_idx + 2
        else:
            insert_at = hwaccel_idx + 2

        if insert_at > len(args):
            insert_at = len(args)

        new_args = list(args)
        new_args[insert_at:insert_at] = ["-hwaccel_output_format", "cuda"]
        return new_args
    except Exception:
        return args


def on_worker_process(data):
    try:
        exec_command = data.get("exec_command")

        if isinstance(exec_command, list):
            data["exec_command"] = _inject_output_format(exec_command)
        elif isinstance(exec_command, str):
            tokens = exec_command.split()
            updated = _inject_output_format(tokens)
            if updated is not tokens:
                data["exec_command"] = " ".join(updated)
    except Exception:
        pass

    return data


if __name__ == "__main__":
    cmd_a = [
        "ffmpeg", "-hide_banner", "-hwaccel", "cuda", "-hwaccel_device", "0",
        "-i", "input.mp4", "-c:v", "hevc_nvenc", "out.mkv",
    ]
    out_a = _inject_output_format(cmd_a)
    assert out_a == [
        "ffmpeg", "-hide_banner", "-hwaccel", "cuda", "-hwaccel_device", "0",
        "-hwaccel_output_format", "cuda",
        "-i", "input.mp4", "-c:v", "hevc_nvenc", "out.mkv",
    ], out_a

    cmd_b = [
        "ffmpeg", "-hwaccel", "cuda",
        "-i", "input.mp4", "-c:v", "hevc_nvenc", "out.mkv",
    ]
    out_b = _inject_output_format(cmd_b)
    assert out_b == [
        "ffmpeg", "-hwaccel", "cuda", "-hwaccel_output_format", "cuda",
        "-i", "input.mp4", "-c:v", "hevc_nvenc", "out.mkv",
    ], out_b

    cmd_c = ["ffmpeg", "-i", "input.mp4", "-c:v", "libx265", "out.mkv"]
    out_c = _inject_output_format(cmd_c)
    assert out_c == cmd_c, out_c

    cmd_d = [
        "ffmpeg", "-hwaccel", "cuda", "-hwaccel_device", "0",
        "-hwaccel_output_format", "cuda",
        "-i", "input.mp4", "-c:v", "hevc_nvenc", "out.mkv",
    ]
    out_d = _inject_output_format(cmd_d)
    assert out_d == cmd_d, out_d

    assert _inject_output_format(_inject_output_format(cmd_a)) == out_a

    assert _inject_output_format(None) is None
    assert _inject_output_format(12345) == 12345

    data = {"exec_command": list(cmd_a)}
    on_worker_process(data)
    assert data["exec_command"] == out_a

    print("All assertions passed.")
