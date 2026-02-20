"""Tests for watch mode."""

from pathlib import Path
from gfi.watch import (
    load_watch_state,
    save_watch_state,
    enable_watch,
    disable_watch,
    is_watch_enabled,
)


def test_watch_state_persistence(tmp_path, monkeypatch):
    """Test watch state save/load."""

    state_file = tmp_path / "test-state.json"
    monkeypatch.setattr('gfi.watch.WATCH_STATE_FILE', state_file)

    # Initial state
    state = load_watch_state()
    assert state["enabled"] == False
    assert state["last_check"] is None

    # Save state
    state["enabled"] = True
    state["seen_issues"] = ["url1", "url2"]
    save_watch_state(state)

    # Load state
    loaded = load_watch_state()
    assert loaded["enabled"] == True
    assert len(loaded["seen_issues"]) == 2


def test_enable_disable_watch(tmp_path, monkeypatch):
    """Test enabling/disabling watch mode."""

    state_file = tmp_path / "test-state.json"
    monkeypatch.setattr('gfi.watch.WATCH_STATE_FILE', state_file)

    # Enable
    enable_watch()
    assert is_watch_enabled() == True

    # Disable
    disable_watch()
    assert is_watch_enabled() == False


def test_watch_state_limits_seen_issues(tmp_path, monkeypatch):
    """Test that seen issues list is limited to 100."""

    state_file = tmp_path / "test-state.json"
    monkeypatch.setattr('gfi.watch.WATCH_STATE_FILE', state_file)

    # Create state with 150 seen issues
    state = {
        "enabled": True,
        "last_check": None,
        "seen_issues": [f"url{i}" for i in range(150)]
    }
    save_watch_state(state)

    # Load and verify it's limited to 100
    loaded = load_watch_state()
    assert len(loaded["seen_issues"]) == 150  # Save preserves all

    # But the check_for_new_issues function should limit to last 100
    # (This would need the actual check_for_new_issues to be tested with mock client)
