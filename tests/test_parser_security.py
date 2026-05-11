"""Regression tests for the SECURITY-CRITICAL `eval()` removal in
`lib/ffmpeg/parser.py`. A malicious media file must not be able to execute
Python code via the `avg_frame_rate` metadata field.
"""

import logging
import os
import sys
from unittest.mock import MagicMock

import pytest

# Path-hack: load lib/ffmpeg/parser.py directly so this test doesn't depend
# on the synthetic `encoder_video_hevc_nvenc_gpu` package set up by conftest
# (the parser module has no Unmanic dependency).
_LIB_DIR = os.path.join(os.path.dirname(__file__), os.pardir, "lib")
sys.path.insert(0, os.path.abspath(_LIB_DIR))
from ffmpeg.parser import Parser  # noqa: E402


def _probe_with_frame_rate(avg_frame_rate: str, duration: str = "60.0"):
    probe = MagicMock()
    probe.get.side_effect = lambda key, default=None: {
        "streams": [{"avg_frame_rate": avg_frame_rate}],
        "format": {"duration": duration},
    }.get(key, default)
    return probe


def test_well_formed_frame_rate_parses_to_float():
    parser = Parser(logging.getLogger("test"))
    parser.set_probe(_probe_with_frame_rate("30000/1001"))
    assert parser.src_fps == pytest.approx(29.97, abs=0.01)


def test_integer_frame_rate_parses():
    parser = Parser(logging.getLogger("test"))
    parser.set_probe(_probe_with_frame_rate("24/1"))
    assert parser.src_fps == pytest.approx(24.0)


def test_malicious_avg_frame_rate_is_rejected_not_evaluated(tmp_path):
    """The pre-fix code did `eval(avg_frame_rate)`. A crafted media file
    could supply a value like `__import__('os').system('touch /tmp/pwned')`
    and the worker would execute it. After the fix, `Fraction(...)` raises
    `ValueError` for anything that isn't a numeric fraction — code is
    NEVER evaluated.

    This test asserts the side effect (file creation) does NOT happen.
    """
    canary = tmp_path / "pwned"
    payload = f"__import__('os').system('touch {canary}')"

    parser = Parser(logging.getLogger("test"))
    parser.set_probe(_probe_with_frame_rate(payload))

    # The fix must:
    #   1. Not execute the payload (canary must not exist).
    #   2. Treat the malformed input as a benign parse failure
    #      (src_fps stays None, no exception escapes).
    assert not canary.exists(), (
        "SECURITY REGRESSION: malicious avg_frame_rate executed code. "
        "lib/ffmpeg/parser.py must not eval() ffprobe metadata."
    )
    assert parser.src_fps is None


def test_arithmetic_expression_is_rejected_not_evaluated():
    """A subtler version of the malicious input: a plain Python expression
    like '1+1' would have eval'd to 2 under the old code. Fraction must
    reject it as ValueError."""
    parser = Parser(logging.getLogger("test"))
    parser.set_probe(_probe_with_frame_rate("1+1"))
    assert parser.src_fps is None


def test_zero_denominator_is_handled_gracefully():
    """ZeroDivisionError from Fraction('0/0') would previously crash under
    eval. Now treated as a parse failure, src_fps stays None."""
    parser = Parser(logging.getLogger("test"))
    parser.set_probe(_probe_with_frame_rate("0/0"))
    # Parser logs a warning and leaves src_fps None — no exception.
    assert parser.src_fps is None
