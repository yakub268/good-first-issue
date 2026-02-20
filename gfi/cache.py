"""Disk-based cache for GitHub API responses."""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Any
import shutil


class DiskCache:
    """Simple disk-based cache with TTL and size limits."""

    CACHE_DIR = Path.home() / ".gfi-cache"
    MAX_CACHE_SIZE_MB = 100

    # Cache TTLs
    SEARCH_TTL_MINUTES = 30
    REPO_TTL_MINUTES = 60

    def __init__(self, enabled: bool = True):
        """Initialize cache.

        Args:
            enabled: Whether caching is enabled (can be disabled via --no-cache)
        """
        self.enabled = enabled

        if self.enabled:
            self.CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, key: str) -> str:
        """Generate cache key from input string.

        Args:
            key: Input string to hash

        Returns:
            Hash of the input string
        """
        return hashlib.md5(key.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get path for cache file.

        Args:
            cache_key: Cache key hash

        Returns:
            Path to cache file
        """
        return self.CACHE_DIR / f"{cache_key}.json"

    def get(self, key: str, ttl_minutes: int) -> Optional[Any]:
        """Get cached value if valid.

        Args:
            key: Cache key
            ttl_minutes: Time-to-live in minutes

        Returns:
            Cached value if valid, None otherwise
        """
        if not self.enabled:
            return None

        cache_key = self._get_cache_key(key)
        cache_path = self._get_cache_path(cache_key)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, 'r') as f:
                cached = json.load(f)

            # Check if expired
            cached_at = datetime.fromisoformat(cached['timestamp'])
            age = datetime.now() - cached_at

            if age > timedelta(minutes=ttl_minutes):
                # Expired - delete it
                cache_path.unlink()
                return None

            return cached['data']

        except (json.JSONDecodeError, KeyError, ValueError):
            # Corrupted cache - delete it
            cache_path.unlink()
            return None

    def set(self, key: str, value: Any) -> None:
        """Store value in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        if not self.enabled:
            return

        # Check cache size before writing
        self._enforce_size_limit()

        cache_key = self._get_cache_key(key)
        cache_path = self._get_cache_path(cache_key)

        cached = {
            'timestamp': datetime.now().isoformat(),
            'data': value
        }

        try:
            with open(cache_path, 'w') as f:
                json.dump(cached, f, indent=2, default=str)
        except Exception:
            # Silently fail on cache write errors
            pass

    def _get_cache_size_mb(self) -> float:
        """Get total cache size in MB.

        Returns:
            Cache size in megabytes
        """
        if not self.CACHE_DIR.exists():
            return 0.0

        total_size = sum(
            f.stat().st_size
            for f in self.CACHE_DIR.glob('*.json')
            if f.is_file()
        )

        return total_size / (1024 * 1024)

    def _enforce_size_limit(self) -> None:
        """Enforce cache size limit by deleting oldest files."""
        cache_size = self._get_cache_size_mb()

        if cache_size <= self.MAX_CACHE_SIZE_MB:
            return

        # Get all cache files sorted by modification time (oldest first)
        cache_files = sorted(
            self.CACHE_DIR.glob('*.json'),
            key=lambda f: f.stat().st_mtime
        )

        # Delete oldest files until under limit
        for cache_file in cache_files:
            if cache_size <= self.MAX_CACHE_SIZE_MB * 0.8:  # 80% threshold
                break

            file_size_mb = cache_file.stat().st_size / (1024 * 1024)
            cache_file.unlink()
            cache_size -= file_size_mb

    def clear(self) -> None:
        """Clear entire cache."""
        if self.CACHE_DIR.exists():
            shutil.rmtree(self.CACHE_DIR)
            self.CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def get_stats(self) -> dict:
        """Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        if not self.CACHE_DIR.exists():
            return {
                'enabled': self.enabled,
                'size_mb': 0.0,
                'file_count': 0,
            }

        cache_files = list(self.CACHE_DIR.glob('*.json'))

        return {
            'enabled': self.enabled,
            'size_mb': round(self._get_cache_size_mb(), 2),
            'file_count': len(cache_files),
            'max_size_mb': self.MAX_CACHE_SIZE_MB,
        }
