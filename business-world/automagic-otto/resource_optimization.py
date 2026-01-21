"""
Resource management and performance optimization for AutoMagic
"""
import os
import psutil
import threading
import time
import gc
import logging
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue, PriorityQueue
import json
import weakref

logger = logging.getLogger("AutoMagic.ResourceManager")

class ResourceMonitor:
    """Monitor system resources and performance"""
    
    def __init__(self, monitor_interval: int = 30):
        self.monitor_interval = monitor_interval
        self.monitoring = False
        self.stats_history = []
        self.max_history_size = 1000
        self._monitor_thread = None
        self.resource_limits = {
            'max_memory_percent': 80,  # Max 80% memory usage
            'max_cpu_percent': 90,     # Max 90% CPU usage
            'max_disk_percent': 85,    # Max 85% disk usage
            'min_free_disk_gb': 5      # Min 5GB free disk space
        }
        
    def start_monitoring(self):
        """Start resource monitoring"""
        if not self.monitoring:
            self.monitoring = True
            self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._monitor_thread.start()
            logger.info("Resource monitoring started")
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        logger.info("Resource monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                stats = self.get_current_stats()
                self.stats_history.append(stats)
                
                # Keep history size manageable
                if len(self.stats_history) > self.max_history_size:
                    self.stats_history = self.stats_history[-self.max_history_size:]
                
                # Check for resource issues
                self._check_resource_warnings(stats)
                
                time.sleep(self.monitor_interval)
                
            except Exception as e:
                logger.error(f"Error in resource monitoring: {e}")
                time.sleep(self.monitor_interval)
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current system resource statistics"""
        try:
            # Memory info
            memory = psutil.virtual_memory()
            
            # CPU info
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Disk info
            disk = psutil.disk_usage('/')
            
            # Process info
            process = psutil.Process(os.getpid())
            process_memory = process.memory_info()
            
            stats = {
                'timestamp': datetime.now().isoformat(),
                'memory': {
                    'total_gb': round(memory.total / (1024**3), 2),
                    'available_gb': round(memory.available / (1024**3), 2),
                    'used_percent': memory.percent,
                    'free_gb': round(memory.free / (1024**3), 2)
                },
                'cpu': {
                    'usage_percent': cpu_percent,
                    'count': cpu_count,
                    'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else None
                },
                'disk': {
                    'total_gb': round(disk.total / (1024**3), 2),
                    'used_gb': round(disk.used / (1024**3), 2),
                    'free_gb': round(disk.free / (1024**3), 2),
                    'used_percent': round((disk.used / disk.total) * 100, 2)
                },
                'process': {
                    'memory_rss_mb': round(process_memory.rss / (1024**2), 2),
                    'memory_vms_mb': round(process_memory.vms / (1024**2), 2),
                    'cpu_percent': process.cpu_percent(),
                    'num_threads': process.num_threads(),
                    'open_files': len(process.open_files()),
                    'connections': len(process.connections())
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def _check_resource_warnings(self, stats: Dict[str, Any]):
        """Check for resource usage warnings"""
        if 'error' in stats:
            return
        
        warnings = []
        
        # Memory check
        if stats['memory']['used_percent'] > self.resource_limits['max_memory_percent']:
            warnings.append(f"High memory usage: {stats['memory']['used_percent']}%")
        
        # CPU check
        if stats['cpu']['usage_percent'] > self.resource_limits['max_cpu_percent']:
            warnings.append(f"High CPU usage: {stats['cpu']['usage_percent']}%")
        
        # Disk check
        if stats['disk']['used_percent'] > self.resource_limits['max_disk_percent']:
            warnings.append(f"High disk usage: {stats['disk']['used_percent']}%")
        
        if stats['disk']['free_gb'] < self.resource_limits['min_free_disk_gb']:
            warnings.append(f"Low disk space: {stats['disk']['free_gb']}GB free")
        
        # Log warnings
        for warning in warnings:
            logger.warning(f"Resource warning: {warning}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary from history"""
        if not self.stats_history:
            return {}
        
        # Calculate averages and peaks
        memory_usages = [s['memory']['used_percent'] for s in self.stats_history if 'memory' in s]
        cpu_usages = [s['cpu']['usage_percent'] for s in self.stats_history if 'cpu' in s]
        
        summary = {
            'monitoring_duration_minutes': len(self.stats_history) * (self.monitor_interval / 60),
            'data_points': len(self.stats_history),
            'memory': {
                'avg_usage_percent': round(sum(memory_usages) / len(memory_usages), 2) if memory_usages else 0,
                'peak_usage_percent': max(memory_usages) if memory_usages else 0,
                'min_usage_percent': min(memory_usages) if memory_usages else 0
            },
            'cpu': {
                'avg_usage_percent': round(sum(cpu_usages) / len(cpu_usages), 2) if cpu_usages else 0,
                'peak_usage_percent': max(cpu_usages) if cpu_usages else 0,
                'min_usage_percent': min(cpu_usages) if cpu_usages else 0
            }
        }
        
        return summary


class CacheManager:
    """Intelligent caching system for AutoMagic"""
    
    def __init__(self, cache_dir: Optional[str] = None, max_cache_size_gb: float = 5.0):
        self.cache_dir = cache_dir or os.path.join(tempfile.gettempdir(), "automagic_cache")
        self.max_cache_size_gb = max_cache_size_gb
        self.cache_index = {}
        self.access_times = {}
        self._lock = threading.Lock()
        
        # Create cache directory
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Load existing cache index
        self._load_cache_index()
        
        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._periodic_cleanup, daemon=True)
        self._cleanup_thread.start()
        
        logger.info(f"Cache manager initialized: {self.cache_dir}")
    
    def _load_cache_index(self):
        """Load cache index from disk"""
        index_file = os.path.join(self.cache_dir, "cache_index.json")
        
        try:
            if os.path.exists(index_file):
                with open(index_file, 'r') as f:
                    data = json.load(f)
                    self.cache_index = data.get('index', {})
                    self.access_times = data.get('access_times', {})
                logger.info(f"Loaded cache index with {len(self.cache_index)} entries")
        except Exception as e:
            logger.warning(f"Failed to load cache index: {e}")
            self.cache_index = {}
            self.access_times = {}
    
    def _save_cache_index(self):
        """Save cache index to disk"""
        index_file = os.path.join(self.cache_dir, "cache_index.json")
        
        try:
            with self._lock:
                data = {
                    'index': self.cache_index,
                    'access_times': self.access_times,
                    'last_updated': datetime.now().isoformat()
                }
                
                with open(index_file, 'w') as f:
                    json.dump(data, f, indent=2)
                    
        except Exception as e:
            logger.error(f"Failed to save cache index: {e}")
    
    def get_cache_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        import hashlib
        
        # Create string representation of all arguments
        key_data = str(args) + str(sorted(kwargs.items()))
        
        # Generate hash
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, cache_key: str) -> Optional[str]:
        """Get cached file path"""
        with self._lock:
            if cache_key in self.cache_index:
                file_path = self.cache_index[cache_key]
                
                if os.path.exists(file_path):
                    # Update access time
                    self.access_times[cache_key] = time.time()
                    logger.debug(f"Cache hit: {cache_key}")
                    return file_path
                else:
                    # Remove invalid entry
                    del self.cache_index[cache_key]
                    if cache_key in self.access_times:
                        del self.access_times[cache_key]
                    logger.debug(f"Cache entry removed (file missing): {cache_key}")
            
        logger.debug(f"Cache miss: {cache_key}")
        return None
    
    def put(self, cache_key: str, file_path: str) -> bool:
        """Add file to cache"""
        if not os.path.exists(file_path):
            logger.error(f"Cannot cache non-existent file: {file_path}")
            return False
        
        try:
            # Copy file to cache directory
            cache_file_path = os.path.join(self.cache_dir, f"{cache_key}_{Path(file_path).name}")
            shutil.copy2(file_path, cache_file_path)
            
            with self._lock:
                self.cache_index[cache_key] = cache_file_path
                self.access_times[cache_key] = time.time()
            
            logger.debug(f"Cached file: {cache_key} -> {cache_file_path}")
            
            # Check cache size and cleanup if needed
            self._check_cache_size()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache file {file_path}: {e}")
            return False
    
    def _check_cache_size(self):
        """Check cache size and cleanup if necessary"""
        try:
            cache_size_gb = self._get_cache_size_gb()
            
            if cache_size_gb > self.max_cache_size_gb:
                logger.info(f"Cache size ({cache_size_gb:.2f}GB) exceeds limit ({self.max_cache_size_gb}GB), cleaning up...")
                self._cleanup_old_entries()
                
        except Exception as e:
            logger.error(f"Error checking cache size: {e}")
    
    def _get_cache_size_gb(self) -> float:
        """Get current cache size in GB"""
        total_size = 0
        
        for root, dirs, files in os.walk(self.cache_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    total_size += os.path.getsize(file_path)
                except OSError:
                    continue
        
        return total_size / (1024**3)
    
    def _cleanup_old_entries(self):
        """Remove old cache entries based on LRU"""
        with self._lock:
            # Sort by access time (oldest first)
            sorted_entries = sorted(
                self.access_times.items(),
                key=lambda x: x[1]
            )
            
            # Remove oldest 30% of entries
            entries_to_remove = int(len(sorted_entries) * 0.3)
            
            for cache_key, _ in sorted_entries[:entries_to_remove]:
                try:
                    file_path = self.cache_index.get(cache_key)
                    if file_path and os.path.exists(file_path):
                        os.remove(file_path)
                    
                    # Remove from index
                    if cache_key in self.cache_index:
                        del self.cache_index[cache_key]
                    if cache_key in self.access_times:
                        del self.access_times[cache_key]
                        
                except Exception as e:
                    logger.error(f"Error removing cache entry {cache_key}: {e}")
            
            logger.info(f"Removed {entries_to_remove} old cache entries")
            
            # Save updated index
            self._save_cache_index()
    
    def _periodic_cleanup(self):
        """Periodic cache cleanup"""
        while True:
            try:
                time.sleep(3600)  # Run every hour
                self._check_cache_size()
                self._save_cache_index()
                
            except Exception as e:
                logger.error(f"Error in periodic cache cleanup: {e}")
    
    def clear_cache(self):
        """Clear all cache"""
        try:
            with self._lock:
                for file_path in self.cache_index.values():
                    if os.path.exists(file_path):
                        os.remove(file_path)
                
                self.cache_index.clear()
                self.access_times.clear()
            
            logger.info("Cache cleared")
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")


class TempFileManager:
    """Manage temporary files with automatic cleanup"""
    
    def __init__(self, base_temp_dir: Optional[str] = None):
        self.base_temp_dir = base_temp_dir or tempfile.gettempdir()
        self.temp_files = weakref.WeakSet()
        self.temp_dirs = weakref.WeakSet()
        self._lock = threading.Lock()
        
        # Register cleanup on exit
        import atexit
        atexit.register(self.cleanup_all)
        
    def create_temp_file(self, suffix: str = "", prefix: str = "automagic_") -> str:
        """Create temporary file with tracking"""
        try:
            fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=self.base_temp_dir)
            os.close(fd)  # Close the file descriptor
            
            with self._lock:
                self.temp_files.add(temp_path)
            
            return temp_path
            
        except Exception as e:
            logger.error(f"Failed to create temp file: {e}")
            raise
    
    def create_temp_dir(self, prefix: str = "automagic_") -> str:
        """Create temporary directory with tracking"""
        try:
            temp_dir = tempfile.mkdtemp(prefix=prefix, dir=self.base_temp_dir)
            
            with self._lock:
                self.temp_dirs.add(temp_dir)
            
            return temp_dir
            
        except Exception as e:
            logger.error(f"Failed to create temp dir: {e}")
            raise
    
    def cleanup_file(self, file_path: str) -> bool:
        """Clean up specific temporary file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Cleaned up temp file: {file_path}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to cleanup temp file {file_path}: {e}")
            return False
    
    def cleanup_dir(self, dir_path: str) -> bool:
        """Clean up specific temporary directory"""
        try:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                logger.debug(f"Cleaned up temp dir: {dir_path}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to cleanup temp dir {dir_path}: {e}")
            return False
    
    def cleanup_all(self):
        """Clean up all tracked temporary files and directories"""
        cleanup_count = 0
        
        # Clean up files
        with self._lock:
            temp_files_copy = list(self.temp_files)
        
        for file_path in temp_files_copy:
            if self.cleanup_file(file_path):
                cleanup_count += 1
        
        # Clean up directories
        with self._lock:
            temp_dirs_copy = list(self.temp_dirs)
        
        for dir_path in temp_dirs_copy:
            if self.cleanup_dir(dir_path):
                cleanup_count += 1
        
        if cleanup_count > 0:
            logger.info(f"Cleaned up {cleanup_count} temporary files/directories")


class PerformanceOptimizer:
    """Performance optimization utilities"""
    
    def __init__(self):
        self.resource_monitor = ResourceMonitor()
        self.cache_manager = CacheManager()
        self.temp_manager = TempFileManager()
        
    def optimize_for_video_processing(self):
        """Optimize system settings for video processing"""
        logger.info("Applying video processing optimizations...")
        
        try:
            # Force garbage collection
            gc.collect()
            
            # Set thread count based on CPU cores
            cpu_count = psutil.cpu_count()
            optimal_threads = max(1, cpu_count - 1)  # Leave one core free
            
            # Set environment variables for FFmpeg
            os.environ['OMP_NUM_THREADS'] = str(optimal_threads)
            os.environ['FFMPEG_THREADS'] = str(optimal_threads)
            
            logger.info(f"Optimized for {optimal_threads} threads")
            
        except Exception as e:
            logger.error(f"Error in performance optimization: {e}")
    
    def optimize_memory_usage(self):
        """Optimize memory usage"""
        try:
            # Force garbage collection
            gc.collect()
            
            # Get current memory stats
            memory = psutil.virtual_memory()
            
            if memory.percent > 80:
                logger.warning(f"High memory usage detected: {memory.percent}%")
                
                # Clear caches if memory is high
                self.cache_manager._cleanup_old_entries()
                
                # Force another garbage collection
                gc.collect()
                
                # Check memory again
                memory_after = psutil.virtual_memory()
                logger.info(f"Memory usage after optimization: {memory_after.percent}%")
            
        except Exception as e:
            logger.error(f"Error in memory optimization: {e}")
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get system optimization recommendations"""
        recommendations = []
        
        try:
            stats = self.resource_monitor.get_current_stats()
            
            if 'error' in stats:
                recommendations.append("Unable to get system stats for recommendations")
                return recommendations
            
            # Memory recommendations
            memory_percent = stats['memory']['used_percent']
            if memory_percent > 85:
                recommendations.append("Consider adding more RAM or closing other applications")
            elif memory_percent > 70:
                recommendations.append("Monitor memory usage during video processing")
            
            # CPU recommendations
            cpu_percent = stats['cpu']['usage_percent']
            if cpu_percent > 90:
                recommendations.append("CPU is under heavy load - consider reducing concurrent tasks")
            
            # Disk recommendations
            disk_percent = stats['disk']['used_percent']
            if disk_percent > 90:
                recommendations.append("Low disk space - consider cleaning up old files")
            elif stats['disk']['free_gb'] < 10:
                recommendations.append("Less than 10GB free disk space - ensure adequate space for video processing")
            
            # Process recommendations
            process_memory = stats['process']['memory_rss_mb']
            if process_memory > 2000:  # 2GB
                recommendations.append("AutoMagic is using significant memory - consider restarting periodically")
            
            if not recommendations:
                recommendations.append("System performance looks good!")
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            recommendations.append("Error analyzing system for recommendations")
        
        return recommendations


# Global instances
resource_monitor = ResourceMonitor()
cache_manager = CacheManager()
temp_manager = TempFileManager()
performance_optimizer = PerformanceOptimizer()

def start_resource_monitoring():
    """Start resource monitoring"""
    resource_monitor.start_monitoring()

def stop_resource_monitoring():
    """Stop resource monitoring"""
    resource_monitor.stop_monitoring()

def get_system_stats() -> Dict[str, Any]:
    """Get current system statistics"""
    return resource_monitor.get_current_stats()

def optimize_system():
    """Run system optimizations"""
    performance_optimizer.optimize_for_video_processing()
    performance_optimizer.optimize_memory_usage()

def get_optimization_recommendations() -> List[str]:
    """Get optimization recommendations"""
    return performance_optimizer.get_optimization_recommendations()

def cleanup_temp_files():
    """Clean up temporary files"""
    temp_manager.cleanup_all()

def clear_cache():
    """Clear application cache"""
    cache_manager.clear_cache()

if __name__ == "__main__":
    # Demo/test mode
    logging.basicConfig(level=logging.INFO)
    
    logger.info("Starting resource optimization demo...")
    
    # Start monitoring
    start_resource_monitoring()
    
    # Get current stats
    stats = get_system_stats()
    logger.info(f"Current memory usage: {stats.get('memory', {}).get('used_percent', 'unknown')}%")
    
    # Get recommendations
    recommendations = get_optimization_recommendations()
    logger.info("Optimization recommendations:")
    for rec in recommendations:
        logger.info(f"  - {rec}")
    
    # Run optimizations
    optimize_system()
    
    time.sleep(5)
    
    # Stop monitoring
    stop_resource_monitoring()
    
    logger.info("Resource optimization demo completed")