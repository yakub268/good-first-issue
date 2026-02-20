"""Tests for success tracking."""

from pathlib import Path
from gfi.success import (
    load_successes,
    save_successes,
    report_success,
    get_success_count,
)


def test_success_persistence(tmp_path, monkeypatch):
    """Test success save/load."""

    success_file = tmp_path / "test-successes.json"
    monkeypatch.setattr('gfi.success.SUCCESS_FILE', success_file)

    # Initial state
    successes = load_successes()
    assert len(successes) == 0

    # Save success
    successes.append({
        "issue_url": "https://github.com/test/repo/issues/1",
        "pr_url": "https://github.com/test/repo/pull/2",
        "notes": "Test",
    })
    save_successes(successes)

    # Load
    loaded = load_successes()
    assert len(loaded) == 1
    assert loaded[0]["issue_url"] == "https://github.com/test/repo/issues/1"


def test_report_success(tmp_path, monkeypatch):
    """Test reporting a success."""

    success_file = tmp_path / "test-successes.json"
    monkeypatch.setattr('gfi.success.SUCCESS_FILE', success_file)

    # Report success
    success = report_success(
        "https://github.com/test/repo/issues/1",
        "https://github.com/test/repo/pull/2",
        "My first contribution!"
    )

    assert success["issue_url"] == "https://github.com/test/repo/issues/1"
    assert success["pr_url"] == "https://github.com/test/repo/pull/2"
    assert success["notes"] == "My first contribution!"
    assert "reported_at" in success

    # Verify it was saved
    assert get_success_count() == 1


def test_multiple_successes(tmp_path, monkeypatch):
    """Test tracking multiple successes."""

    success_file = tmp_path / "test-successes.json"
    monkeypatch.setattr('gfi.success.SUCCESS_FILE', success_file)

    # Report multiple successes
    for i in range(5):
        report_success(
            f"https://github.com/test/repo/issues/{i}",
            f"https://github.com/test/repo/pull/{i}",
            f"Success {i}"
        )

    assert get_success_count() == 5

    successes = load_successes()
    assert len(successes) == 5
    assert successes[0]["notes"] == "Success 0"
    assert successes[4]["notes"] == "Success 4"
