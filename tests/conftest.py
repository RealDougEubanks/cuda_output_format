"""Shim the runtime environment so plugin.py is importable in tests.

Unmanic installs each plugin into `<plugins-dir>/<plugin-id>/` and runs
workers with the plugins directory on `sys.path`, which makes the
plugin folder name importable as a package. We replicate that in tests
by registering a synthetic `encoder_video_hevc_nvenc_gpu` package whose
`__path__` points at the repo root.

We also stub `unmanic.libs.unplugins.settings.PluginSettings` so the
plugin's `Settings` subclass has a base class at import time.
"""

import os
import sys
import types
from typing import Any


class _FakePluginSettings:
    """Minimal stand-in for `unmanic.libs.unplugins.settings.PluginSettings`."""

    settings: dict = {}

    def __init__(self, *_args: Any, **_kwargs: Any) -> None:
        self._values = dict(self.settings)

    def get_setting(self, name: str) -> Any:
        return self._values.get(name, self.settings.get(name))


def _install_fakes() -> None:
    unmanic_pkg = types.ModuleType("unmanic")
    libs_pkg = types.ModuleType("unmanic.libs")
    unplugins_pkg = types.ModuleType("unmanic.libs.unplugins")
    settings_mod = types.ModuleType("unmanic.libs.unplugins.settings")
    settings_mod.PluginSettings = _FakePluginSettings  # type: ignore[attr-defined]

    sys.modules.setdefault("unmanic", unmanic_pkg)
    sys.modules.setdefault("unmanic.libs", libs_pkg)
    sys.modules.setdefault("unmanic.libs.unplugins", unplugins_pkg)
    sys.modules.setdefault("unmanic.libs.unplugins.settings", settings_mod)

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pkg = types.ModuleType("encoder_video_hevc_nvenc_gpu")
    pkg.__path__ = [repo_root]  # type: ignore[attr-defined]
    sys.modules.setdefault("encoder_video_hevc_nvenc_gpu", pkg)


_install_fakes()
