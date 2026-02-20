"""Tests for cache module."""

import pytest
import json
import time
from pathlib import Path
from gfi.cache import DiskCache


@pytest.fixture
def cache(tmp_path):
    """Create cache instance with temp directory."""
    # Override cache directory for testing
    DiskCache.CACHE_DIR = tmp_path / ".gfi-cache-test"
    return DiskCache(enabled=True)


def test_cache_disabled():
    """Test that disabled cache returns None."""
    cache = DiskCache(enabled=False)
    cache.set("key", "value")
    assert cache.get("key", 60) is None


def test_cache_set_and_get(cache):
    """Test basic cache set and get."""
    cache.set("test_key", {"data": "test_value"})
    result = cache.get("test_key", 60)
    assert result == {"data": "test_value"}


def test_cache_expiry(cache):
    """Test cache expiration."""
    # Set short TTL
    cache.set("expiry_key", "will_expire")

    # Should exist immediately
    assert cache.get("expiry_key", 60) == "will_expire"

    # Manually expire by setting TTL to 0
    assert cache.get("expiry_key", 0) is None


def test_cache_miss(cache):
    """Test cache miss returns None."""
    assert cache.get("nonexistent_key", 60) is None


def test_cache_key_hashing(cache):
    """Test that different keys generate different hashes."""
    cache.set("key1", "value1")
    cache.set("key2", "value2")

    assert cache.get("key1", 60) == "value1"
    assert cache.get("key2", 60) == "value2"


def test_cache_clear(cache):
    """Test cache clearing."""
    cache.set("key1", "value1")
    cache.set("key2", "value2")

    assert cache.get("key1", 60) == "value1"

    cache.clear()

    assert cache.get("key1", 60) is None
    assert cache.get("key2", 60) is None


def test_cache_stats(cache):
    """Test cache statistics."""
    cache.set("key1", "value1")
    cache.set("key2", {"nested": "data"})

    stats = cache.get_stats()

    assert stats['enabled'] is True
    assert stats['file_count'] == 2
    assert stats['size_mb'] >= 0  # Size can be 0.0 for very small files
    assert stats['max_size_mb'] == 100


def test_cache_size_enforcement(cache, tmp_path):
    """Test cache size limit enforcement."""
    # Set a very small limit for testing
    cache.MAX_CACHE_SIZE_MB = 0.001  # 1 KB

    # Write multiple cache entries
    for i in range(10):
        cache.set(f"key_{i}", {"data": "x" * 1000})

    # Cache should have enforced size limit
    stats = cache.get_stats()
    assert stats['size_mb'] <= cache.MAX_CACHE_SIZE_MB


def test_corrupted_cache_file(cache):
    """Test handling of corrupted cache files."""
    cache.set("good_key", "good_value")

    # Corrupt the cache file
    cache_files = list(cache.CACHE_DIR.glob("*.json"))
    if cache_files:
        with open(cache_files[0], 'w') as f:
            f.write("corrupted json{{{")

    # Should return None and delete corrupted file
    result = cache.get("good_key", 60)
    assert result is None


def test_cache_with_complex_data(cache):
    """Test caching complex nested data structures."""
    complex_data = {
        "issues": [
            {"id": 1, "title": "Issue 1", "labels": ["bug", "good first issue"]},
            {"id": 2, "title": "Issue 2", "labels": ["enhancement"]},
        ],
        "metadata": {
            "total": 2,
            "timestamp": "2024-01-01T00:00:00",
        }
    }

    cache.set("complex_key", complex_data)
    result = cache.get("complex_key", 60)

    assert result == complex_data
    assert len(result['issues']) == 2
    assert result['metadata']['total'] == 2
