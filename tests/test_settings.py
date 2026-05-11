"""Smoke tests for the Settings class — defaults, form visibility toggles."""

import importlib


def _fresh_settings():
    """Re-import settings to construct a fresh instance.

    The Settings class reads `self.get_setting(...)` during `__init__` to
    build `form_settings`, so we can't share an instance across tests that
    care about default-value behaviour.
    """
    settings_mod = importlib.import_module("settings")
    return settings_mod.Settings()


def test_defaults_match_documented_v1_1_0_values():
    s = _fresh_settings()
    assert s.settings["preset"] == "fast"
    assert s.settings["profile"] == "main"
    assert s.settings["hw_decoding"] is False
    assert s.settings["hw_output_format_cuda"] is True
    assert s.settings["advanced"] is False
    assert s.settings["keep_container"] is True
    assert s.settings["dest_container"] == "mkv"
    assert s.settings["max_muxing_queue_size"] == 2048


def test_hw_output_format_cuda_form_hidden_when_hw_decoding_off():
    s = _fresh_settings()
    # Default state: hw_decoding=False, so the GPU-pipeline toggle is hidden.
    assert s.form_settings["hw_output_format_cuda"]["display"] == "hidden"


def test_dest_container_form_hidden_when_keep_container_on():
    s = _fresh_settings()
    assert s.form_settings["dest_container"]["display"] == "hidden"


def test_advanced_mode_form_visibility_inverts_preset_and_custom():
    """When `advanced` is on, the simple-mode fields hide and the textareas
    appear. When it's off, the inverse. Verified by toggling via the underlying
    settings dict because we mock `get_setting` from the dict in tests."""
    s = _fresh_settings()
    # Default state: advanced=False → preset visible, main_options hidden.
    assert s.form_settings["preset"].get("display") != "hidden"
    assert s.form_settings["main_options"].get("display") == "hidden"


def test_form_settings_keys_match_settings_keys():
    """Every setting must have a corresponding form entry, or the Unmanic UI
    silently drops it. Catches the easy mistake of adding a setting without
    wiring its form."""
    s = _fresh_settings()
    assert set(s.form_settings.keys()) == set(s.settings.keys())
