# core/strategy/trend_analyzer.py - Fetches and analyzes trends
import os
from datetime import date, timedelta
from pytrends.request import TrendReq
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_trending_topics(pillars: list[str]) -> dict | None:
    """Fetches trending topics from Google and YouTube."""
    print("📈 Analyzing trends...")
    try:
        pytrend = TrendReq()
        youtube = build("youtube", "v3", developerKey=os.getenv("YT_API_KEY"))
        trends = {}
        for topic in pillars:
            pytrend.build_payload([topic], timeframe='now 1-d')
            rising_topics = pytrend.related_topics().get(topic, {}).get('rising', {}).head(3)
            trends[topic] = {
                "google": rising_topics['topic_title'].tolist() if not rising_topics.empty else [],
                "youtube": []
            }
            search_term = f"{topic} {trends[topic]['google'][0]}" if trends[topic]["google"] else topic
            req = youtube.search().list(q=search_term, part="snippet", order="viewCount", type="video", maxResults=3).execute()
            trends[topic]["youtube"] = [v["snippet"]["title"] for v in req.get("items", [])]
        return trends
    except Exception as e:
        print(f"❌ Trend analysis failed: {e}")
        return None
