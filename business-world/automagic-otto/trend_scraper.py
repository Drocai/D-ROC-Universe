"""
Trend Scraper Module for OTTO Content Generation System.

This module is responsible for scraping trending topics from various social media
and search platforms to provide real-time trend data for content generation.
"""
import os
import json
import re
import random
import time
import logging
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import pytz
from pytrends.request import TrendReq

# Initialize logging
logger = logging.getLogger('trend_scraper')
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Optional: Reddit API credentials (if using PRAW)
# To use Reddit, you'll need to create a Reddit app at https://www.reddit.com/prefs/apps
# and set these values in your .env file
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'OTTO Trend Scraper v1.0')

class TrendScraper:
    """Main class for scraping trends from various platforms."""
    
    def __init__(self):
        """Initialize the trend scraper with session and cache setup."""
        self.session = HTMLSession()
        self.trends_cache = {
            'google': {'data': None, 'timestamp': None},
            'youtube': {'data': None, 'timestamp': None},
            'twitter': {'data': None, 'timestamp': None},
            'tiktok': {'data': None, 'timestamp': None},
            'reddit': {'data': None, 'timestamp': None},
        }
        self.cache_expiry = {
            'google': timedelta(hours=6),
            'youtube': timedelta(hours=12),
            'twitter': timedelta(hours=4),
            'tiktok': timedelta(hours=8),
            'reddit': timedelta(hours=6),
        }
        self.google_trends = TrendReq(hl='en-US', tz=360)
        
        # If cache file exists, load it
        self.cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trends_cache.json')
        self._load_cache()
        
    def _load_cache(self):
        """Load cached trends data if available."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                    
                # Convert string timestamps back to datetime objects
                for platform in self.trends_cache:
                    if platform in cache_data and cache_data[platform]['timestamp']:
                        cache_data[platform]['timestamp'] = datetime.fromisoformat(cache_data[platform]['timestamp'])
                        
                self.trends_cache.update(cache_data)
                logger.info(f"Loaded trend cache from {self.cache_file}")
        except Exception as e:
            logger.error(f"Error loading trends cache: {e}")
    
    def _save_cache(self):
        """Save the current trends cache to disk."""
        try:
            # Convert datetime objects to ISO format strings for JSON serialization
            serializable_cache = {}
            for platform, data in self.trends_cache.items():
                serializable_cache[platform] = {
                    'data': data['data'],
                    'timestamp': data['timestamp'].isoformat() if data['timestamp'] else None
                }
                
            with open(self.cache_file, 'w') as f:
                json.dump(serializable_cache, f, indent=2)
            logger.info(f"Saved trend cache to {self.cache_file}")
        except Exception as e:
            logger.error(f"Error saving trends cache: {e}")
            
    def _is_cache_valid(self, platform):
        """Check if the cached data for a platform is still valid."""
        cache_data = self.trends_cache.get(platform)
        if not cache_data or not cache_data['timestamp'] or not cache_data['data']:
            return False
            
        now = datetime.now()
        expiry_time = cache_data['timestamp'] + self.cache_expiry[platform]
        return now < expiry_time
        
    def get_google_trends(self, region='US', category=0):
        """Fetch trending searches from Google Trends.
        
        Args:
            region: Country code (default 'US')
            category: Category ID (default 0 for all categories)
            
        Returns:
            List of trending search terms
        """
        if self._is_cache_valid('google'):
            logger.info("Using cached Google Trends data")
            return self.trends_cache['google']['data']
            
        try:
            logger.info("Fetching Google trending searches...")
            # Get real-time trends
            trends = self.google_trends.trending_searches(pn=region)
            
            # Process the results
            trend_items = []
            if not trends.empty:
                for trend in trends[0].tolist():
                    trend_items.append({
                        'title': trend,
                        'source': 'google',
                        'category': self._categorize_trend(trend)
                    })
                    
            # Cache the results
            self.trends_cache['google']['data'] = trend_items
            self.trends_cache['google']['timestamp'] = datetime.now()
            self._save_cache()
            
            return trend_items
            
        except Exception as e:
            logger.error(f"Error fetching Google Trends: {e}")
            # Fall back to cached data even if expired
            if self.trends_cache['google']['data']:
                return self.trends_cache['google']['data']
            return []
    
    def get_youtube_trends(self, region='US', category=0):
        """Fetch trending videos from YouTube.
        Note: This method uses web scraping rather than the API for simplicity.
        
        Args:
            region: Country code (default 'US')
            category: Category ID (default 0 for all categories)
            
        Returns:
            List of trending video titles and metadata
        """
        if self._is_cache_valid('youtube'):
            logger.info("Using cached YouTube Trends data")
            return self.trends_cache['youtube']['data']
            
        try:
            logger.info("Fetching YouTube trending videos...")
            url = f"https://www.youtube.com/feed/trending?gl={region}"
            response = self.session.get(url)
            
            trend_items = []
            videos = []
            
            # Extract video titles using regex (more robust than relying on specific CSS)
            titles = re.findall(r'"title":{"runs":\[{"text":"(.*?)"}]', response.text)
            
            # Process up to 10 unique titles
            seen_titles = set()
            for title in titles:
                if title not in seen_titles and len(trend_items) < 10:
                    seen_titles.add(title)
                    trend_items.append({
                        'title': title,
                        'source': 'youtube',
                        'category': self._categorize_trend(title)
                    })
            
            # Cache the results
            self.trends_cache['youtube']['data'] = trend_items
            self.trends_cache['youtube']['timestamp'] = datetime.now()
            self._save_cache()
            
            return trend_items
            
        except Exception as e:
            logger.error(f"Error fetching YouTube Trends: {e}")
            # Fall back to cached data even if expired
            if self.trends_cache['youtube']['data']:
                return self.trends_cache['youtube']['data']
            return []
    
    def get_twitter_trends(self, woeid=23424977):  # 23424977 is the WOEID for United States
        """Fetch trending topics from Twitter using web scraping.
        
        Args:
            woeid: The "Where On Earth ID" for location-based trends (default is US)
            
        Returns:
            List of trending hashtags and topics
        """
        if self._is_cache_valid('twitter'):
            logger.info("Using cached Twitter Trends data")
            return self.trends_cache['twitter']['data']
            
        try:
            logger.info("Fetching Twitter trending topics...")
            # Since Twitter's API requires authentication and has usage limits,
            # we'll use a simplified approach with some example trends
            # In a production system, you'd want to use the official API
            
            # Simulated response with common trending structures
            trend_items = [
                {
                    'title': '#AI',
                    'source': 'twitter',
                    'category': 'technology'
                },
                {
                    'title': 'Climate Change',
                    'source': 'twitter',
                    'category': 'environment'
                },
                {
                    'title': '#WednesdayWisdom',
                    'source': 'twitter',
                    'category': 'lifestyle'
                }
            ]
            
            # In a real implementation, you'd make API calls here
            # For now, we're using placeholder data
            
            # Cache the results
            self.trends_cache['twitter']['data'] = trend_items
            self.trends_cache['twitter']['timestamp'] = datetime.now()
            self._save_cache()
            
            return trend_items
            
        except Exception as e:
            logger.error(f"Error fetching Twitter Trends: {e}")
            # Fall back to cached data even if expired
            if self.trends_cache['twitter']['data']:
                return self.trends_cache['twitter']['data']
            return []
    
    def get_tiktok_trends(self):
        """Fetch trending hashtags and sounds from TikTok using web scraping.
        
        Returns:
            List of trending hashtags and sounds
        """
        if self._is_cache_valid('tiktok'):
            logger.info("Using cached TikTok Trends data")
            return self.trends_cache['tiktok']['data']
            
        try:
            logger.info("Fetching TikTok trending hashtags...")
            # TikTok is particularly challenging to scrape and has strong anti-scraping measures
            # A more robust implementation would use a specialized TikTok scraping library
            # or a third-party API service
            
            # For now, we'll use some representative examples
            trend_items = [
                {
                    'title': '#BookTok',
                    'source': 'tiktok',
                    'type': 'hashtag',
                    'category': 'entertainment'
                },
                {
                    'title': 'Aesthetic Morning Routine',
                    'source': 'tiktok',
                    'type': 'content',
                    'category': 'lifestyle'
                },
                {
                    'title': "That's What I Want - Lil Nas X",
                    'source': 'tiktok',
                    'type': 'sound',
                    'category': 'music'
                }
            ]
            
            # Cache the results
            self.trends_cache['tiktok']['data'] = trend_items
            self.trends_cache['tiktok']['timestamp'] = datetime.now()
            self._save_cache()
            
            return trend_items
            
        except Exception as e:
            logger.error(f"Error fetching TikTok Trends: {e}")
            # Fall back to cached data even if expired
            if self.trends_cache['tiktok']['data']:
                return self.trends_cache['tiktok']['data']
            return []
    
    def get_reddit_trends(self):
        """Fetch trending topics from Reddit.
        
        Returns:
            List of trending post titles and subreddits
        """
        if self._is_cache_valid('reddit'):
            logger.info("Using cached Reddit Trends data")
            return self.trends_cache['reddit']['data']
            
        try:
            logger.info("Fetching Reddit trending posts...")
            
            # For a full implementation, you'd use PRAW (Python Reddit API Wrapper)
            # but it requires authentication
            
            # Here's a simpler approach using direct requests to Reddit's JSON API
            url = "https://www.reddit.com/r/popular.json"
            headers = {'User-Agent': REDDIT_USER_AGENT or 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                trend_items = []
                
                for post in data['data']['children'][:10]:  # Get top 10 posts
                    post_data = post['data']
                    trend_items.append({
                        'title': post_data['title'],
                        'subreddit': post_data['subreddit'],
                        'source': 'reddit',
                        'category': self._categorize_trend(post_data['title'])
                    })
                
                # Cache the results
                self.trends_cache['reddit']['data'] = trend_items
                self.trends_cache['reddit']['timestamp'] = datetime.now()
                self._save_cache()
                
                return trend_items
                
            else:
                logger.error(f"Reddit API returned status code {response.status_code}")
                if self.trends_cache['reddit']['data']:
                    return self.trends_cache['reddit']['data']
                return []
                
        except Exception as e:
            logger.error(f"Error fetching Reddit Trends: {e}")
            # Fall back to cached data even if expired
            if self.trends_cache['reddit']['data']:
                return self.trends_cache['reddit']['data']
            return []
    
    def get_all_trends(self):
        """Fetch trends from all supported platforms and combine them.
        
        Returns:
            Dictionary containing trends from all platforms and combined analysis
        """
        # Get trends from each platform
        google_trends = self.get_google_trends()
        youtube_trends = self.get_youtube_trends()
        twitter_trends = self.get_twitter_trends()
        tiktok_trends = self.get_tiktok_trends()
        reddit_trends = self.get_reddit_trends()
        
        # Combine all trends
        all_trends = {
            'google': google_trends,
            'youtube': youtube_trends,
            'twitter': twitter_trends,
            'tiktok': tiktok_trends,
            'reddit': reddit_trends,
            'combined': google_trends + youtube_trends + twitter_trends + tiktok_trends + reddit_trends
        }
        
        # Add timestamp
        all_trends['timestamp'] = datetime.now().isoformat()
        
        # Add analysis
        all_trends['analysis'] = self._analyze_trends(all_trends['combined'])
        
        return all_trends
    
    def _categorize_trend(self, trend_text):
        """Categorize a trend based on its text content.
        
        Args:
            trend_text: The text of the trend to categorize
            
        Returns:
            The category of the trend
        """
        trend_text = trend_text.lower()
        
        # Define category keywords
        categories = {
            'technology': ['ai', 'tech', 'iphone', 'android', 'gadget', 'computer', 'robot', 'software', 'app', 'digital'],
            'entertainment': ['movie', 'tv', 'show', 'film', 'actor', 'actress', 'celebrity', 'hollywood', 'netflix', 'disney'],
            'politics': ['government', 'election', 'president', 'congress', 'senate', 'democrat', 'republican', 'policy'],
            'sports': ['game', 'team', 'player', 'score', 'match', 'championship', 'tournament', 'nba', 'nfl', 'mlb', 'soccer'],
            'music': ['song', 'album', 'artist', 'band', 'concert', 'spotify', 'playlist', 'hit', 'rapper', 'singer'],
            'gaming': ['game', 'gaming', 'playstation', 'xbox', 'nintendo', 'twitch', 'streamer', 'level', 'player'],
            'health': ['covid', 'virus', 'health', 'fitness', 'diet', 'wellness', 'exercise', 'vaccine', 'medical'],
            'business': ['stock', 'market', 'company', 'ceo', 'startup', 'investor', 'economy', 'finance', 'billion'],
            'environment': ['climate', 'environment', 'sustainable', 'green', 'recycle', 'energy', 'pollution'],
            'lifestyle': ['fashion', 'beauty', 'style', 'trend', 'makeup', 'clothing', 'design', 'home', 'decor', 'food']
        }
        
        # Check each category
        scores = {category: 0 for category in categories}
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in trend_text:
                    scores[category] += 1
                    
        # Get the highest scoring category
        best_category = max(scores.items(), key=lambda x: x[1])
        
        # If no clear winner, fallback to 'other'
        if best_category[1] == 0:
            return 'other'
        
        return best_category[0]
    
    def _analyze_trends(self, trends):
        """Analyze combined trends to find patterns and high-impact topics.
        
        Args:
            trends: List of trend dictionaries
            
        Returns:
            Dictionary with analysis results
        """
        # Count categories
        categories = {}
        for trend in trends:
            if 'category' in trend:
                category = trend['category']
                categories[category] = categories.get(category, 0) + 1
                
        # Find most popular category
        most_popular_category = max(categories.items(), key=lambda x: x[1]) if categories else ('unknown', 0)
        
        # Get sources distribution
        sources = {}
        for trend in trends:
            source = trend.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
            
        # Create word frequency map (simple implementation)
        word_freq = {}
        for trend in trends:
            title = trend.get('title', '')
            words = re.findall(r'\w+', title.lower())
            for word in words:
                if len(word) > 3:  # Filter out short words
                    word_freq[word] = word_freq.get(word, 0) + 1
                    
        # Get most frequent words
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        top_words = sorted_words[:10] if len(sorted_words) >= 10 else sorted_words
        
        return {
            'categories': categories,
            'most_popular_category': most_popular_category,
            'sources': sources,
            'top_words': dict(top_words)
        }

    def get_trend_recommendations(self, count=5):
        """Generate content recommendations based on current trends.
        
        Args:
            count: Number of recommendations to generate
            
        Returns:
            List of trend-based content recommendations
        """
        all_trends = self.get_all_trends()
        combined_trends = all_trends['combined']
        
        # Shuffle to ensure variety
        random.shuffle(combined_trends)
        
        recommendations = []
        for _ in range(min(count, len(combined_trends))):
            if not combined_trends:
                break
                
            # Pop a random trend
            trend = combined_trends.pop(random.randint(0, len(combined_trends) - 1))
            
            source_prefix = {
                'google': "People are searching for",
                'youtube': "YouTube viewers are watching",
                'twitter': "Twitter users are discussing",
                'tiktok': "TikTok users are sharing",
                'reddit': "Reddit is talking about"
            }
            
            prefix = source_prefix.get(trend.get('source', 'other'), "Trending now")
            title = trend.get('title', '')
            category = trend.get('category', 'general')
            
            recommendation = {
                'title': title,
                'source': trend.get('source', 'unknown'),
                'category': category,
                'summary': f"{prefix}: {title}",
                'adaptation_ideas': self._generate_adaptation_ideas(title, category)
            }
            
            recommendations.append(recommendation)
            
        return recommendations
    
    def _generate_adaptation_ideas(self, trend_title, category):
        """Generate content adaptation ideas for a trend.
        
        Args:
            trend_title: The title of the trend
            category: The category of the trend
            
        Returns:
            List of adaptation ideas
        """
        # Category-specific adaptation templates
        templates = {
            'technology': [
                "How tiny animals discover and use {trend} in their daily lives",
                "When {trend} comes to Whispering Woods: A lesson in adapting to new technology",
                "Squeaky learns about {trend} and shares it with friends"
            ],
            'entertainment': [
                "Tiny animals put on a show inspired by {trend}",
                "Movie night in the forest: Watching {trend} and learning valuable lessons",
                "Barnaby Badger's review of {trend} teaches everyone about opinions"
            ],
            'music': [
                "The tiny animals create their own version of {trend}",
                "Dancing to {trend} helps Penelope Squirrel overcome shyness",
                "A musical adventure inspired by {trend}"
            ],
            'lifestyle': [
                "The tiny animals try the {trend} challenge with a positive twist",
                "Adopting {trend} in the cozy burrow: A story about healthy choices",
                "When {trend} becomes popular in Acorn Valley"
            ],
            'sports': [
                "The forest Olympics: Inspired by {trend}",
                "Squeaky learns teamwork from watching {trend}",
                "A friendly competition based on {trend} teaches good sportsmanship"
            ],
            'health': [
                "Staying healthy like {trend} in the animal village",
                "Wellness wisdom: What tiny animals learned from {trend}",
                "The positive affirmations of {trend} help Barnaby feel better"
            ]
        }
        
        # Default templates for any category
        default_templates = [
            "What tiny animals can teach us about {trend}",
            "When {trend} meets the whimsical world of Acorn Valley",
            "Squeaky and friends discover the positive side of {trend}",
            "Learning to say 'I can do it!' while exploring {trend}",
            "A heartwarming story about friendship, inspired by {trend}"
        ]
        
        # Get category-specific templates or fall back to default
        category_templates = templates.get(category, default_templates)
        
        # Generate 2-3 adaptation ideas
        ideas = []
        template_pool = category_templates + default_templates
        num_ideas = random.randint(2, 3)
        
        for _ in range(min(num_ideas, len(template_pool))):
            template = random.choice(template_pool)
            template_pool.remove(template)  # Avoid duplicates
            idea = template.replace('{trend}', trend_title)
            ideas.append(idea)
            
        return ideas

# Singleton instance
trend_scraper = TrendScraper()

def get_trending_topics(count=5):
    """Convenience function to get trending topic recommendations.
    
    Args:
        count: Number of trending topics to return
        
    Returns:
        List of trending topic recommendations
    """
    return trend_scraper.get_trend_recommendations(count)

def get_adaptation_for_children(trend_text):
    """Generate child-friendly adaptation ideas for any trend.
    
    Args:
        trend_text: The trend to adapt
        
    Returns:
        List of child-friendly adaptation ideas
    """
    category = trend_scraper._categorize_trend(trend_text)
    return trend_scraper._generate_adaptation_ideas(trend_text, category)

# Example usage if this module is run directly
if __name__ == "__main__":
    # Set up console logging
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)
    
    print("Fetching trending topics...")
    recommendations = get_trending_topics(5)
    
    print("\n=== TRENDING TOPIC RECOMMENDATIONS ===")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['title']} (from {rec['source']})")
        print(f"   Category: {rec['category']}")
        print(f"   Summary: {rec['summary']}")
        print("   Adaptation ideas:")
        for idea in rec['adaptation_ideas']:
            print(f"   - {idea}")
            
    print("\n=== ALL TRENDS ANALYSIS ===")
    analysis = trend_scraper.get_all_trends()['analysis']
    print(f"Most popular category: {analysis['most_popular_category'][0]} ({analysis['most_popular_category'][1]} mentions)")
    print("\nTop words in trends:")
    for word, count in analysis['top_words'].items():
        print(f"- {word}: {count}")
