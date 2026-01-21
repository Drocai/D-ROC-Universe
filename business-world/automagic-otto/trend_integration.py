#!/usr/bin/env python3
"""
Trend Integration Module for AutoMagic O.T.T.O.

This module interfaces with the trend_scraper to safely provide trending topics
for the main automation script.
"""
import os
import logging
import random
import time
from pathlib import Path
from typing import List, Dict, Optional, Any, Union

# Setup logging
logger = logging.getLogger("trend_integration")

# Default content ideas if trend scraper fails
DEFAULT_CONTENT_IDEAS = [
    "The science behind why we dream",
    "How pandas adapted to eating bamboo",
    "The surprising benefits of daydreaming",
    "Why the sky appears blue: a simple explanation",
    "How butterflies navigate during migration",
    "The importance of bees to our ecosystem",
    "How clouds form and what they can tell us",
    "Why leaves change color in autumn",
    "How animals communicate with each other",
    "The fascinating life cycle of a star"
]

def get_trending_topic() -> Dict[str, Any]:
    """
    Get a trending topic with fallbacks if trend scraper fails.
    
    Returns:
        Dict with 'topic', 'source', and 'category' keys
    """
    try:
        # Try to import the working trend scraper first, then fall back to original
        try:
            from working_trend_scraper import get_trending_topics
            logger.info("Using working trend scraper module")
        except ImportError:
            from trend_scraper import get_trending_topics
            logger.info("Using original trend scraper module")
        
        logger.info("Fetching trending topics from trend_scraper module")
        trends = get_trending_topics(count=1)
        
        # If we got valid results, use them
        if trends and isinstance(trends, list) and len(trends) > 0:
            trend = trends[0]
            # Handle both old and new trend format
            if 'adapted_title' in trend:
                # New working scraper format
                topic_title = trend.get('adapted_title', trend.get('original_trend', 'Unknown'))
                logger.info(f"Using adapted trending topic: {topic_title} (original: {trend.get('original_trend', 'Unknown')}) from {trend.get('source', 'Unknown')}")
            else:
                # Original format
                topic_title = trend.get('title', 'Unknown')
                logger.info(f"Using trending topic: {topic_title} from {trend.get('source', 'Unknown')}")
                
            return {
                'topic': topic_title or random.choice(DEFAULT_CONTENT_IDEAS),
                'source': trend.get('source', 'trend_scraper'),
                'category': trend.get('category', 'general')
            }
        else:
            logger.warning("Trend scraper returned no results, using fallback")
            return {
                'topic': random.choice(DEFAULT_CONTENT_IDEAS),
                'source': 'default',
                'category': 'general'
            }
    
    except ImportError:
        logger.warning("Trend scraper module not found, using fallback content ideas")
        return {
            'topic': random.choice(DEFAULT_CONTENT_IDEAS),
            'source': 'default',
            'category': 'general'
        }
    except Exception as e:
        logger.error(f"Error using trend scraper: {str(e)}")
        return {
            'topic': random.choice(DEFAULT_CONTENT_IDEAS),
            'source': 'default',
            'category': 'general'
        }

def get_content_adaptation(topic: str) -> List[str]:
    """
    Generate content adaptation ideas based on a topic.
    
    Args:
        topic: The topic to adapt
        
    Returns:
        List of adaptation ideas
    """
    try:
        # Try to use the trend scraper's adaptation function
        from trend_scraper import get_adaptation_for_children
        
        logger.info(f"Generating child-friendly adaptations for: {topic}")
        adaptations = get_adaptation_for_children(topic)
        
        if adaptations and isinstance(adaptations, list) and len(adaptations) > 0:
            return adaptations
        else:
            return _generate_fallback_adaptations(topic)
    
    except ImportError:
        logger.warning("Trend scraper module not available for adaptations, using fallback")
        return _generate_fallback_adaptations(topic)
    except Exception as e:
        logger.error(f"Error generating adaptations: {str(e)}")
        return _generate_fallback_adaptations(topic)

def _generate_fallback_adaptations(topic: str) -> List[str]:
    """Generate fallback adaptation ideas if trend scraper fails."""
    templates = [
        f"Learning about {topic} through a friendly woodland creature's adventure",
        f"The curious squirrel discovers {topic} and shares with friends",
        f"A day at the pond: How tiny frogs understand {topic}",
        f"Bedtime stories about {topic} for young minds",
        f"How to explain {topic} to children with fun activities"
    ]
    
    # Return 2-3 random templates
    return random.sample(templates, min(3, len(templates)))

if __name__ == "__main__":
    # Simple test of functionality
    logging.basicConfig(level=logging.INFO)
    
    print("\nTesting trend integration module:")
    print("-" * 40)
    
    trend = get_trending_topic()
    print(f"Trending Topic: {trend['topic']}")
    print(f"Source: {trend['source']}")
    print(f"Category: {trend['category']}")
    
    print("\nContent Adaptations:")
    adaptations = get_content_adaptation(trend['topic'])
    for i, adaptation in enumerate(adaptations, 1):
        print(f"{i}. {adaptation}")
