import json
import hashlib
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional, Union
import threading
import os

class ContentCache:
    def __init__(self, cache_dir: str = "cache", default_max_age_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_max_age_hours = default_max_age_hours
        self._lock = threading.Lock()
        
        # Create subdirectories for different types of cache
        self.text_cache_dir = self.cache_dir / "text"
        self.binary_cache_dir = self.cache_dir / "binary"
        self.api_cache_dir = self.cache_dir / "api"
        
        for cache_type_dir in [self.text_cache_dir, self.binary_cache_dir, self.api_cache_dir]:
            cache_type_dir.mkdir(exist_ok=True)
    
    def _get_cache_key(self, data: str) -> str:
        """Generate a safe cache key from input data"""
        return hashlib.md5(data.encode('utf-8')).hexdigest()
    
    def _get_cache_file_path(self, key: str, cache_type: str = "text") -> Path:
        """Get the full path to a cache file"""
        cache_key = self._get_cache_key(key)
        
        if cache_type == "binary":
            return self.binary_cache_dir / f"{cache_key}.pkl"
        elif cache_type == "api":
            return self.api_cache_dir / f"{cache_key}.json"
        else:
            return self.text_cache_dir / f"{cache_key}.json"
    
    def get(self, key: str, max_age_hours: Optional[int] = None, cache_type: str = "text") -> Optional[Any]:
        """Retrieve data from cache if it exists and is not expired"""
        with self._lock:
            max_age = max_age_hours or self.default_max_age_hours
            cache_file = self._get_cache_file_path(key, cache_type)
            
            if not cache_file.exists():
                return None
            
            try:
                if cache_type == "binary":
                    with open(cache_file, 'rb') as f:
                        cached = pickle.load(f)
                else:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cached = json.load(f)
                
                created = datetime.fromisoformat(cached['timestamp'])
                if datetime.now() - created > timedelta(hours=max_age):
                    cache_file.unlink()
                    return None
                
                return cached['data']
            
            except (json.JSONDecodeError, pickle.PickleError, KeyError, ValueError) as e:
                # Remove corrupted cache file
                cache_file.unlink()
                return None
    
    def set(self, key: str, data: Any, cache_type: str = "text") -> bool:
        """Store data in cache"""
        with self._lock:
            try:
                cache_file = self._get_cache_file_path(key, cache_type)
                cache_data = {
                    'timestamp': datetime.now().isoformat(),
                    'data': data,
                    'cache_type': cache_type
                }
                
                if cache_type == "binary":
                    with open(cache_file, 'wb') as f:
                        pickle.dump(cache_data, f)
                else:
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(cache_data, f, indent=2, ensure_ascii=False)
                
                return True
            
            except Exception as e:
                print(f"Error caching data: {e}")
                return False
    
    def delete(self, key: str, cache_type: str = "text") -> bool:
        """Delete a specific cache entry"""
        with self._lock:
            cache_file = self._get_cache_file_path(key, cache_type)
            if cache_file.exists():
                cache_file.unlink()
                return True
            return False
    
    def clear_expired(self, max_age_hours: Optional[int] = None) -> int:
        """Clear all expired cache entries and return count of deleted files"""
        max_age = max_age_hours or self.default_max_age_hours
        cutoff_time = datetime.now() - timedelta(hours=max_age)
        deleted_count = 0
        
        with self._lock:
            for cache_type_dir in [self.text_cache_dir, self.binary_cache_dir, self.api_cache_dir]:
                for cache_file in cache_type_dir.glob("*"):
                    if cache_file.is_file():
                        try:
                            file_modified = datetime.fromtimestamp(cache_file.stat().st_mtime)
                            if file_modified < cutoff_time:
                                cache_file.unlink()
                                deleted_count += 1
                        except (OSError, ValueError):
                            # Remove problematic files
                            cache_file.unlink()
                            deleted_count += 1
        
        return deleted_count
    
    def clear_all(self) -> int:
        """Clear all cache entries and return count of deleted files"""
        deleted_count = 0
        
        with self._lock:
            for cache_type_dir in [self.text_cache_dir, self.binary_cache_dir, self.api_cache_dir]:
                for cache_file in cache_type_dir.glob("*"):
                    if cache_file.is_file():
                        cache_file.unlink()
                        deleted_count += 1
        
        return deleted_count
    
    def get_cache_stats(self) -> dict:
        """Get statistics about cache usage"""
        stats = {
            'total_files': 0,
            'total_size_mb': 0,
            'by_type': {}
        }
        
        for cache_type_dir in [self.text_cache_dir, self.binary_cache_dir, self.api_cache_dir]:
            cache_type = cache_type_dir.name
            type_files = 0
            type_size = 0
            
            for cache_file in cache_type_dir.glob("*"):
                if cache_file.is_file():
                    type_files += 1
                    type_size += cache_file.stat().st_size
            
            stats['by_type'][cache_type] = {
                'files': type_files,
                'size_mb': round(type_size / 1024 / 1024, 2)
            }
            
            stats['total_files'] += type_files
            stats['total_size_mb'] += type_size / 1024 / 1024
        
        stats['total_size_mb'] = round(stats['total_size_mb'], 2)
        return stats

# Global cache instance
cache = ContentCache()
