#!/usr/bin/env python3
"""
AutoMagic Optimized - Next-Generation Content Creation System
Consolidated, high-performance video production pipeline with async processing,
resource management, and intelligent error handling.
"""

import asyncio
import logging
import time
import argparse
import sys
import signal
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime, timedelta
import schedule

# Import optimized components
from core.config import get_config, validate_config
from core.api import get_api_client
from core.video import create_video_from_assets, VideoSettings
from core.utils.resource_manager import get_resource_manager, managed_operation

# Setup logging
logger = logging.getLogger("AutoMagic.Main")

class OptimizedVideoProduction:
    """Next-generation video production system with async processing"""
    
    def __init__(self):
        self.config = get_config()
        self.resource_manager = None
        self.running = False
        self._shutdown_event = asyncio.Event()
        
        # Performance metrics
        self.metrics = {
            "videos_created": 0,
            "total_processing_time": 0,
            "average_processing_time": 0,
            "api_calls_made": 0,
            "cache_hits": 0,
            "errors_encountered": 0
        }
        
        logger.info("OptimizedVideoProduction initialized")
    
    async def initialize(self):
        """Initialize all components"""
        try:
            # Validate configuration
            if not validate_config():
                logger.error("Configuration validation failed")
                sys.exit(1)
            
            # Initialize resource manager
            self.resource_manager = await get_resource_manager()
            
            # Schedule cleanup
            asyncio.create_task(self._schedule_maintenance())
            
            logger.info("AutoMagic Optimized initialized successfully")
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("Initiating graceful shutdown...")
        self.running = False
        self._shutdown_event.set()
        
        if self.resource_manager:
            await self.resource_manager.shutdown()
        
        logger.info("Shutdown completed")
    
    async def _schedule_maintenance(self):
        """Schedule periodic maintenance tasks"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                if self.resource_manager:
                    await self.resource_manager.scheduled_cleanup()
                    
                    # Log resource status
                    status = self.resource_manager.get_status()
                    logger.info(f"Resource status: {status['resource_usage']}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Maintenance task failed: {e}")
    
    async def create_daily_content(self, custom_topic: Optional[str] = None) -> Dict[str, Any]:
        """Create daily content using optimized pipeline"""
        start_time = time.time()
        operation_id = f"daily_content_{int(start_time)}"
        
        try:
            async with managed_operation(operation_id):
                logger.info(f"Starting daily content creation (Operation: {operation_id})")
                
                # Step 1: Content Planning
                async with get_api_client() as api_client:
                    if custom_topic:
                        topic = custom_topic
                        logger.info(f"Using custom topic: {topic}")
                    else:
                        topic = await api_client.generate_content_idea()
                        logger.info(f"Generated topic: {topic}")
                    
                    # Step 2: Script Generation
                    script = await api_client.generate_script(topic)
                    logger.info("Script generated successfully")
                    
                    # Step 3: Asset Generation (Parallel)
                    image_task = asyncio.create_task(
                        api_client.generate_images(script, count=3)
                    )
                    audio_task = asyncio.create_task(
                        api_client.generate_voice(script)
                    )
                    
                    # Wait for assets with timeout
                    try:
                        images, audio_path = await asyncio.wait_for(
                            asyncio.gather(image_task, audio_task),
                            timeout=300  # 5 minutes timeout
                        )
                    except asyncio.TimeoutError:
                        logger.error("Asset generation timed out")
                        raise
                
                # Step 4: Video Creation
                video_settings = VideoSettings.from_config()
                video_path = await create_video_from_assets(
                    images, audio_path, settings=video_settings
                )
                
                # Step 5: Platform Optimization (if needed)
                # Could add platform-specific versions here
                
                # Step 6: Upload (if configured)
                upload_success = await self._upload_if_configured(video_path, topic, script)
                
                # Update metrics
                processing_time = time.time() - start_time
                self._update_metrics(processing_time, upload_success)
                
                # Update day counter
                if upload_success:
                    self.config.update_production_day(self.config.production.day_number + 1)
                
                result = {
                    "success": True,
                    "video_path": video_path,
                    "topic": topic,
                    "processing_time": processing_time,
                    "upload_success": upload_success,
                    "metrics": self.metrics.copy()
                }
                
                logger.info(f"Daily content creation completed successfully in {processing_time:.1f}s")
                return result
                
        except Exception as e:
            self.metrics["errors_encountered"] += 1
            logger.error(f"Daily content creation failed: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time,
                "metrics": self.metrics.copy()
            }
    
    async def _upload_if_configured(self, video_path: str, topic: str, script: str) -> bool:
        """Upload video if YouTube is configured"""
        try:
            # Check if YouTube credentials are available
            if not self.config.api.youtube_client_id or self.config.api.youtube_client_id.startswith("YOUR_"):
                logger.info("YouTube not configured, skipping upload")
                return False
            
            # Import YouTube uploader
            from OTTO_Magic.core.pipelines.youtube_uploader import upload_to_youtube
            
            # Create metadata
            today = datetime.now().strftime("%Y-%m-%d")
            title = f"S{self.config.production.season:02d}D{self.config.production.day_number:02d}: {topic} ({today})"
            
            # Enhanced description
            description = f"""{script}

Generated by AutoMagic AI on {today}
Season {self.config.production.season}, Day {self.config.production.day_number}

#AutoMagic #AI #GeneratedContent #YouTube
            """.strip()
            
            tags = ["AutoMagic", "AI", "Generated", topic.split()[0] if topic.split() else "Content"]
            
            # Upload with retry logic
            for attempt in range(3):
                try:
                    success = await asyncio.to_thread(
                        upload_to_youtube, 
                        video_path, 
                        title, 
                        description, 
                        tags
                    )
                    
                    if success:
                        logger.info(f"Video uploaded to YouTube successfully: {title}")
                        return True
                    else:
                        logger.warning(f"Upload attempt {attempt + 1} failed")
                        if attempt < 2:
                            await asyncio.sleep(30)  # Wait before retry
                        
                except Exception as e:
                    logger.error(f"Upload attempt {attempt + 1} failed: {e}")
                    if attempt < 2:
                        await asyncio.sleep(30)
            
            logger.error("All upload attempts failed")
            return False
            
        except Exception as e:
            logger.error(f"Upload process failed: {e}")
            return False
    
    def _update_metrics(self, processing_time: float, upload_success: bool):
        """Update performance metrics"""
        self.metrics["videos_created"] += 1
        self.metrics["total_processing_time"] += processing_time
        self.metrics["average_processing_time"] = (
            self.metrics["total_processing_time"] / self.metrics["videos_created"]
        )
        
        if upload_success:
            self.metrics["api_calls_made"] += 1
    
    async def run_scheduled_production(self):
        """Run scheduled daily production"""
        self.running = True
        
        # Get schedule time
        run_time = self.config.production.daily_run_time
        logger.info(f"Scheduled for daily run at {run_time}")
        
        # Schedule the job
        schedule.every().day.at(run_time).do(
            lambda: asyncio.create_task(self.create_daily_content())
        )
        
        logger.info("Entering scheduled mode. Press Ctrl+C to stop.")
        
        try:
            while self.running and not self._shutdown_event.is_set():
                # Check for scheduled jobs
                schedule.run_pending()
                
                # Sleep with cancellation support
                try:
                    await asyncio.wait_for(asyncio.sleep(60), timeout=60)
                except asyncio.TimeoutError:
                    pass  # Normal timeout, continue loop
                    
        except asyncio.CancelledError:
            logger.info("Scheduled production cancelled")
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            await self.shutdown()
    
    async def test_component(self, component: str) -> Dict[str, Any]:
        """Test individual components"""
        logger.info(f"Testing component: {component}")
        
        try:
            if component == "config":
                return {"success": validate_config(), "config_status": "validated"}
            
            elif component == "api":
                async with get_api_client() as api_client:
                    topic = await api_client.generate_content_idea(["test"])
                    return {"success": True, "test_topic": topic}
            
            elif component == "images":
                async with get_api_client() as api_client:
                    script = "Test script for image generation. [Show a test image] This is a test."
                    images = await api_client.generate_images(script, count=1)
                    return {"success": bool(images), "images_generated": len(images)}
            
            elif component == "audio":
                async with get_api_client() as api_client:
                    audio_path = await api_client.generate_voice("This is a test of the voice generation system.")
                    return {"success": bool(audio_path), "audio_path": audio_path}
            
            elif component == "video":
                # Create test video with mock assets
                async with get_api_client() as api_client:
                    script = "Test video creation. [Show test image 1] [Show test image 2] Test complete."
                    images = await api_client.generate_images(script, count=2)
                    audio_path = await api_client.generate_voice("Test video creation script.")
                    
                    if images and audio_path:
                        video_path = await create_video_from_assets(images, audio_path)
                        return {"success": bool(video_path), "video_path": video_path}
                    else:
                        return {"success": False, "error": "Failed to generate test assets"}
            
            elif component == "resources":
                if self.resource_manager:
                    status = self.resource_manager.get_status()
                    cleanup_result = await self.resource_manager.scheduled_cleanup()
                    return {
                        "success": True, 
                        "resource_status": status,
                        "cleanup_result": cleanup_result
                    }
                else:
                    return {"success": False, "error": "Resource manager not initialized"}
            
            else:
                return {"success": False, "error": f"Unknown component: {component}"}
                
        except Exception as e:
            logger.error(f"Component test failed for {component}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return {
            "metrics": self.metrics.copy(),
            "config_summary": {
                "season": self.config.production.season,
                "day_number": self.config.production.day_number,
                "scheduled_time": self.config.production.daily_run_time
            },
            "system_status": self.resource_manager.get_status() if self.resource_manager else {}
        }

# Signal handler for graceful shutdown
production_instance = None

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    global production_instance
    logger.info(f"Received signal {signum}")
    if production_instance:
        asyncio.create_task(production_instance.shutdown())

async def main():
    """Main entry point with enhanced CLI"""
    global production_instance
    
    parser = argparse.ArgumentParser(
        description="AutoMagic Optimized - Next-Generation Content Creation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python automagic_optimized.py --now                    # Create content immediately
  python automagic_optimized.py --scheduled             # Run in scheduled mode
  python automagic_optimized.py --test api              # Test API components
  python automagic_optimized.py --topic "AI Revolution" # Custom topic
  python automagic_optimized.py --metrics               # Show performance metrics
        """
    )
    
    # Execution modes
    parser.add_argument("--now", action="store_true", 
                       help="Create content immediately")
    parser.add_argument("--scheduled", action="store_true",
                       help="Run in scheduled mode")
    parser.add_argument("--topic", type=str,
                       help="Custom topic for content creation")
    
    # Testing
    parser.add_argument("--test", choices=["config", "api", "images", "audio", "video", "resources"],
                       help="Test specific component")
    
    # Information
    parser.add_argument("--metrics", action="store_true",
                       help="Show performance metrics and exit")
    parser.add_argument("--status", action="store_true",
                       help="Show system status and exit")
    
    # Configuration
    parser.add_argument("--debug", action="store_true",
                       help="Enable debug logging")
    parser.add_argument("--cleanup", action="store_true",
                       help="Run cleanup and exit")
    
    args = parser.parse_args()
    
    # Set debug logging
    if args.debug:
        logging.getLogger("AutoMagic").setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    try:
        # Initialize production system
        production_instance = OptimizedVideoProduction()
        await production_instance.initialize()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Handle different modes
        if args.metrics:
            metrics = production_instance.get_metrics()
            print("\n=== AutoMagic Performance Metrics ===")
            for key, value in metrics["metrics"].items():
                print(f"{key.replace('_', ' ').title()}: {value}")
            print("\n=== Configuration Summary ===")
            for key, value in metrics["config_summary"].items():
                print(f"{key.replace('_', ' ').title()}: {value}")
            return
        
        elif args.status:
            if production_instance.resource_manager:
                status = production_instance.resource_manager.get_status()
                print("\n=== System Status ===")
                print(f"Resource Usage: {status['resource_usage']}")
                print(f"Active Operations: {status['active_operations']}")
            return
        
        elif args.cleanup:
            if production_instance.resource_manager:
                logger.info("Running manual cleanup...")
                result = await production_instance.resource_manager.scheduled_cleanup()
                if result:
                    print(f"Cleanup completed: {result['total_files_removed']} files removed, "
                          f"{result['total_size_freed_mb']:.1f}MB freed")
            return
        
        elif args.test:
            result = await production_instance.test_component(args.test)
            print(f"\n=== Component Test: {args.test} ===")
            if result["success"]:
                print("✅ Test passed")
                for key, value in result.items():
                    if key != "success":
                        print(f"{key}: {value}")
            else:
                print("❌ Test failed")
                print(f"Error: {result.get('error', 'Unknown error')}")
            return
        
        elif args.now:
            logger.info("Creating content immediately...")
            result = await production_instance.create_daily_content(args.topic)
            
            if result["success"]:
                print(f"\n✅ Content created successfully!")
                print(f"Video: {result['video_path']}")
                print(f"Topic: {result['topic']}")
                print(f"Processing time: {result['processing_time']:.1f}s")
                if result["upload_success"]:
                    print("✅ Uploaded to YouTube")
                else:
                    print("⚠️ Upload skipped or failed")
            else:
                print(f"\n❌ Content creation failed: {result['error']}")
                print(f"Processing time: {result['processing_time']:.1f}s")
            return
        
        elif args.scheduled:
            logger.info("Starting scheduled mode...")
            await production_instance.run_scheduled_production()
            return
        
        else:
            # Default: show help and current status
            parser.print_help()
            print("\n=== Current Status ===")
            if validate_config():
                print("✅ Configuration valid")
            else:
                print("❌ Configuration has issues")
            
            metrics = production_instance.get_metrics()
            print(f"Season: {metrics['config_summary']['season']}")
            print(f"Day: {metrics['config_summary']['day_number']}")
            print(f"Scheduled time: {metrics['config_summary']['scheduled_time']}")
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        if production_instance:
            await production_instance.shutdown()

if __name__ == "__main__":
    # Run with proper async support
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)