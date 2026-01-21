#!/usr/bin/env python3
"""
Test script for the optimized AutoMagic system
"""
import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("AutoMagic.Test")

def test_imports():
    """Test if all modules can be imported"""
    logger.info("Testing module imports...")
    
    try:
        # Test enhanced modules
        from enhanced_api_integrations import EnhancedAPIManager, get_api_status
        logger.info("✓ Enhanced API integrations imported successfully")
        
        from enhanced_video_pipeline import EnhancedVideoAssembler, assemble_video
        logger.info("✓ Enhanced video pipeline imported successfully")
        
        from resource_optimization import (
            ResourceMonitor, CacheManager, PerformanceOptimizer,
            get_system_stats, optimize_system
        )
        logger.info("✓ Resource optimization imported successfully")
        
        from comprehensive_testing_suite import AutoMagicTestSuite
        logger.info("✓ Testing suite imported successfully")
        
        return True
        
    except ImportError as e:
        logger.error(f"✗ Import failed: {e}")
        return False

if __name__ == "__main__":
    test_imports()
