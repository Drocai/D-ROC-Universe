#!/usr/bin/env python3
"""
Resource Management and Cleanup System
Manages system resources, monitors usage, and performs cleanup operations
"""

import asyncio
import psutil
import time
import logging
import shutil
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from pathlib import Path
from contextlib import asynccontextmanager
import gc
import threading
from ..config import get_config

logger = logging.getLogger("AutoMagic.ResourceManager")

@dataclass
class ResourceLimits:
    """Resource usage limits"""
    max_memory_gb: float = 4.0
    max_disk_gb: float = 10.0
    max_cpu_percent: float = 80.0
    max_concurrent_ops: int = 3

@dataclass
class ResourceUsage:
    """Current resource usage"""
    memory_gb: float = 0.0
    disk_gb: float = 0.0
    cpu_percent: float = 0.0
    active_ops: int = 0
    
    def is_within_limits(self, limits: ResourceLimits) -> bool:
        """Check if usage is within specified limits"""
        return (
            self.memory_gb <= limits.max_memory_gb and
            self.disk_gb <= limits.max_disk_gb and
            self.cpu_percent <= limits.max_cpu_percent and
            self.active_ops <= limits.max_concurrent_ops
        )

class ResourceMonitor:
    """Monitors system resource usage"""
    
    def __init__(self, check_interval: float = 5.0):
        self.check_interval = check_interval
        self.config = get_config()
        self.limits = ResourceLimits(
            max_memory_gb=self.config.resources.max_memory_gb,
            max_disk_gb=self.config.resources.max_disk_usage_gb,
            max_concurrent_ops=self.config.resources.max_concurrent_operations
        )
        
        self._monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._callbacks: List[Callable[[ResourceUsage], None]] = []
        
        # Resource tracking
        self.current_usage = ResourceUsage()
        self.usage_history: List[ResourceUsage] = []
        self.max_history = 100
        
        # Active operations tracking
        self.active_operations: Dict[str, float] = {}  # operation_id -> start_time
        self._operation_lock = threading.Lock()
    
    def add_callback(self, callback: Callable[[ResourceUsage], None]):
        """Add callback for resource usage updates"""
        self._callbacks.append(callback)
    
    async def start_monitoring(self):
        """Start resource monitoring"""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("Resource monitoring started")
    
    async def stop_monitoring(self):
        """Stop resource monitoring"""
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Resource monitoring stopped")
    
    async def _monitor_loop(self):
        """Main monitoring loop"""
        while self._monitoring:
            try:
                await self._update_usage()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in resource monitoring: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _update_usage(self):
        """Update current resource usage"""
        try:
            # Memory usage
            memory = psutil.virtual_memory()
            self.current_usage.memory_gb = memory.used / (1024**3)
            
            # Disk usage
            disk = psutil.disk_usage(self.config.paths.base_dir)
            used_gb = (disk.total - disk.free) / (1024**3)
            self.current_usage.disk_gb = used_gb
            
            # CPU usage
            self.current_usage.cpu_percent = psutil.cpu_percent(interval=1)
            
            # Active operations
            with self._operation_lock:
                self.current_usage.active_ops = len(self.active_operations)
            
            # Store in history
            self.usage_history.append(ResourceUsage(
                memory_gb=self.current_usage.memory_gb,
                disk_gb=self.current_usage.disk_gb,
                cpu_percent=self.current_usage.cpu_percent,
                active_ops=self.current_usage.active_ops
            ))
            
            # Limit history size
            if len(self.usage_history) > self.max_history:
                self.usage_history = self.usage_history[-self.max_history:]
            
            # Call callbacks
            for callback in self._callbacks:
                try:
                    callback(self.current_usage)
                except Exception as e:
                    logger.error(f"Error in resource callback: {e}")
            
            # Log warnings if limits exceeded
            if not self.current_usage.is_within_limits(self.limits):
                logger.warning(f"Resource limits exceeded: "
                             f"Memory: {self.current_usage.memory_gb:.1f}GB, "
                             f"Disk: {self.current_usage.disk_gb:.1f}GB, "
                             f"CPU: {self.current_usage.cpu_percent:.1f}%, "
                             f"Ops: {self.current_usage.active_ops}")
                
        except Exception as e:
            logger.error(f"Failed to update resource usage: {e}")
    
    def register_operation(self, operation_id: str):
        """Register a new operation"""
        with self._operation_lock:
            self.active_operations[operation_id] = time.time()
        logger.debug(f"Registered operation: {operation_id}")
    
    def unregister_operation(self, operation_id: str):
        """Unregister completed operation"""
        with self._operation_lock:
            start_time = self.active_operations.pop(operation_id, None)
            if start_time:
                duration = time.time() - start_time
                logger.debug(f"Unregistered operation: {operation_id} (duration: {duration:.2f}s)")
    
    def can_start_operation(self) -> bool:
        """Check if a new operation can be started"""
        return self.current_usage.is_within_limits(self.limits)
    
    def get_resource_summary(self) -> Dict[str, Any]:
        """Get current resource usage summary"""
        return {
            "memory_gb": self.current_usage.memory_gb,
            "memory_limit_gb": self.limits.max_memory_gb,
            "disk_gb": self.current_usage.disk_gb,
            "disk_limit_gb": self.limits.max_disk_gb,
            "cpu_percent": self.current_usage.cpu_percent,
            "cpu_limit_percent": self.limits.max_cpu_percent,
            "active_operations": self.current_usage.active_ops,
            "max_operations": self.limits.max_concurrent_ops,
            "within_limits": self.current_usage.is_within_limits(self.limits)
        }

class FileCleanupManager:
    """Manages file cleanup operations"""
    
    def __init__(self):
        self.config = get_config()
        self.cleanup_rules: List[Dict[str, Any]] = []
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Setup default cleanup rules"""
        self.cleanup_rules = [
            {
                "name": "old_generated_images",
                "path": self.config.paths.image_save_path,
                "pattern": "*.png",
                "max_age_days": self.config.resources.cleanup_after_days,
                "max_files": 100
            },
            {
                "name": "old_generated_audio",
                "path": self.config.paths.audio_save_path,
                "pattern": "*.mp3",
                "max_age_days": self.config.resources.cleanup_after_days,
                "max_files": 50
            },
            {
                "name": "temp_files",
                "path": self.config.paths.temp_path,
                "pattern": "*",
                "max_age_days": 1,
                "max_files": 10
            },
            {
                "name": "old_video_clips",
                "path": self.config.paths.video_clips_path,
                "pattern": "*.mp4",
                "max_age_days": self.config.resources.cleanup_after_days,
                "max_files": 20
            }
        ]
    
    async def cleanup_files(self, dry_run: bool = False) -> Dict[str, Any]:
        """Execute cleanup operations"""
        results = {
            "total_files_removed": 0,
            "total_size_freed_mb": 0,
            "rules_executed": [],
            "errors": []
        }
        
        for rule in self.cleanup_rules:
            try:
                rule_result = await self._execute_cleanup_rule(rule, dry_run)
                results["total_files_removed"] += rule_result["files_removed"]
                results["total_size_freed_mb"] += rule_result["size_freed_mb"]
                results["rules_executed"].append(rule_result)
                
                logger.info(f"Cleanup rule '{rule['name']}': "
                          f"removed {rule_result['files_removed']} files, "
                          f"freed {rule_result['size_freed_mb']:.1f}MB")
                
            except Exception as e:
                error_msg = f"Error executing cleanup rule '{rule['name']}': {e}"
                results["errors"].append(error_msg)
                logger.error(error_msg)
        
        return results
    
    async def _execute_cleanup_rule(self, rule: Dict[str, Any], dry_run: bool) -> Dict[str, Any]:
        """Execute a single cleanup rule"""
        result = {
            "rule_name": rule["name"],
            "files_removed": 0,
            "size_freed_mb": 0,
            "files_processed": []
        }
        
        path = Path(rule["path"])
        if not path.exists():
            return result
        
        # Find files matching pattern
        files = list(path.glob(rule["pattern"]))
        
        # Filter by age
        max_age_days = rule.get("max_age_days", 999)
        cutoff_time = time.time() - (max_age_days * 24 * 3600)
        
        old_files = []
        for file_path in files:
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                old_files.append(file_path)
        
        # Sort by modification time (oldest first)
        old_files.sort(key=lambda f: f.stat().st_mtime)
        
        # Apply max_files limit
        max_files = rule.get("max_files", len(old_files))
        if len(files) > max_files:
            # Keep only the newest files, remove the rest
            files_to_remove = old_files + files[max_files:]
        else:
            files_to_remove = old_files
        
        # Remove duplicates
        files_to_remove = list(set(files_to_remove))
        
        # Remove files
        for file_path in files_to_remove:
            try:
                file_size = file_path.stat().st_size
                
                if not dry_run:
                    file_path.unlink()
                
                result["files_removed"] += 1
                result["size_freed_mb"] += file_size / (1024 * 1024)
                result["files_processed"].append(str(file_path))
                
            except Exception as e:
                logger.error(f"Failed to remove file {file_path}: {e}")
        
        return result
    
    def add_cleanup_rule(self, name: str, path: Path, pattern: str, 
                        max_age_days: int = 7, max_files: int = 100):
        """Add a custom cleanup rule"""
        rule = {
            "name": name,
            "path": path,
            "pattern": pattern,
            "max_age_days": max_age_days,
            "max_files": max_files
        }
        self.cleanup_rules.append(rule)
        logger.info(f"Added cleanup rule: {name}")

class ResourceManager:
    """Main resource management coordinator"""
    
    def __init__(self):
        self.config = get_config()
        self.monitor = ResourceMonitor()
        self.cleanup_manager = FileCleanupManager()
        
        # Resource management settings
        self.auto_cleanup_enabled = True
        self.auto_gc_enabled = True
        self.memory_pressure_threshold = 0.8  # 80% of limit
        
        # Setup callbacks
        self.monitor.add_callback(self._on_resource_update)
        
    async def initialize(self):
        """Initialize resource management"""
        await self.monitor.start_monitoring()
        logger.info("Resource manager initialized")
    
    async def shutdown(self):
        """Shutdown resource management"""
        await self.monitor.stop_monitoring()
        logger.info("Resource manager shutdown")
    
    def _on_resource_update(self, usage: ResourceUsage):
        """Handle resource usage updates"""
        # Check for memory pressure
        memory_ratio = usage.memory_gb / self.config.resources.max_memory_gb
        
        if memory_ratio > self.memory_pressure_threshold:
            logger.warning(f"Memory pressure detected: {memory_ratio:.1%}")
            
            if self.auto_gc_enabled:
                asyncio.create_task(self._emergency_gc())
            
            if self.auto_cleanup_enabled:
                asyncio.create_task(self._emergency_cleanup())
    
    async def _emergency_gc(self):
        """Perform emergency garbage collection"""
        try:
            logger.info("Performing emergency garbage collection")
            
            # Run garbage collection
            collected = gc.collect()
            logger.info(f"Garbage collection freed {collected} objects")
            
        except Exception as e:
            logger.error(f"Emergency garbage collection failed: {e}")
    
    async def _emergency_cleanup(self):
        """Perform emergency file cleanup"""
        try:
            logger.info("Performing emergency file cleanup")
            
            # Run cleanup with more aggressive settings
            temp_rule = {
                "name": "emergency_temp",
                "path": self.config.paths.temp_path,
                "pattern": "*",
                "max_age_days": 0,  # Remove all temp files
                "max_files": 0
            }
            
            await self.cleanup_manager._execute_cleanup_rule(temp_rule, dry_run=False)
            
        except Exception as e:
            logger.error(f"Emergency cleanup failed: {e}")
    
    @asynccontextmanager
    async def managed_operation(self, operation_id: str):
        """Context manager for resource-managed operations"""
        # Wait for resource availability
        while not self.monitor.can_start_operation():
            logger.info(f"Waiting for resources to start operation: {operation_id}")
            await asyncio.sleep(1)
        
        # Register operation
        self.monitor.register_operation(operation_id)
        
        try:
            yield
        finally:
            # Unregister operation
            self.monitor.unregister_operation(operation_id)
            
            # Optional cleanup after operation
            if self.auto_gc_enabled:
                gc.collect()
    
    async def scheduled_cleanup(self):
        """Perform scheduled cleanup"""
        logger.info("Starting scheduled cleanup")
        
        try:
            results = await self.cleanup_manager.cleanup_files(dry_run=False)
            
            logger.info(f"Scheduled cleanup completed: "
                       f"removed {results['total_files_removed']} files, "
                       f"freed {results['total_size_freed_mb']:.1f}MB")
            
            return results
            
        except Exception as e:
            logger.error(f"Scheduled cleanup failed: {e}")
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get current resource management status"""
        return {
            "resource_usage": self.monitor.get_resource_summary(),
            "active_operations": list(self.monitor.active_operations.keys()),
            "auto_cleanup_enabled": self.auto_cleanup_enabled,
            "auto_gc_enabled": self.auto_gc_enabled
        }

# Global resource manager instance
_resource_manager: Optional[ResourceManager] = None

async def get_resource_manager() -> ResourceManager:
    """Get or create global resource manager"""
    global _resource_manager
    
    if _resource_manager is None:
        _resource_manager = ResourceManager()
        await _resource_manager.initialize()
    
    return _resource_manager

@asynccontextmanager
async def managed_operation(operation_id: str):
    """Convenience context manager for managed operations"""
    resource_manager = await get_resource_manager()
    async with resource_manager.managed_operation(operation_id):
        yield