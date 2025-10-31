#!/usr/bin/env python3
"""
Yara ❤️ Dell YouTube Intelligence - API Client
YouTube Data API v3 and YouTube Analytics API wrapper
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/Users/arthurdell/YARADELL/config/.env')


class YouTubeAPIClient:
    """YouTube Data API v3 and Analytics API client"""
    
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        self.client_id = os.getenv('YOUTUBE_CLIENT_ID')
        self.client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
        self.channel_id = os.getenv('YOUTUBE_CHANNEL_ID')
        self.email = os.getenv('YOUTUBE_EMAIL')
        
        # API endpoints
        self.youtube_data_api = "https://www.googleapis.com/youtube/v3"
        self.youtube_analytics_api = "https://youtubeanalytics.googleapis.com/v2"
        
        # Database connection
        self.db_conn = None
        
    def connect_database(self):
        """Connect to aya_rag PostgreSQL database"""
        try:
            self.db_conn = psycopg2.connect(
                host=os.getenv('POSTGRES_HOST', 'localhost'),
                port=os.getenv('POSTGRES_PORT', '5432'),
                database=os.getenv('POSTGRES_DB', 'aya_rag'),
                user=os.getenv('POSTGRES_USER', 'postgres'),
                password=os.getenv('POSTGRES_PASSWORD')
            )
            print("✅ Connected to aya_rag database")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def get_channel_info(self, channel_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get channel metadata from YouTube Data API
        
        Args:
            channel_id: YouTube channel ID (uses self.channel_id if not provided)
            
        Returns:
            Dictionary with channel information
        """
        channel_id = channel_id or self.channel_id
        
        if not self.api_key:
            return {"error": "YouTube API key not configured"}
        
        url = f"{self.youtube_data_api}/channels"
        params = {
            'part': 'snippet,contentDetails,statistics,brandingSettings',
            'id': channel_id,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'items' in data and len(data['items']) > 0:
                channel = data['items'][0]
                return {
                    'channel_id': channel['id'],
                    'channel_name': channel['snippet']['title'],
                    'channel_handle': channel['snippet'].get('customUrl', ''),
                    'description': channel['snippet']['description'],
                    'subscriber_count': int(channel['statistics']['subscriberCount']),
                    'video_count': int(channel['statistics']['videoCount']),
                    'view_count': int(channel['statistics']['viewCount']),
                    'published_at': channel['snippet']['publishedAt'],
                    'thumbnail_url': channel['snippet']['thumbnails']['high']['url'],
                    'metadata': {
                        'keywords': channel['brandingSettings'].get('channel', {}).get('keywords', ''),
                        'country': channel['snippet'].get('country', '')
                    }
                }
            else:
                return {"error": "Channel not found"}
                
        except requests.exceptions.RequestException as e:
            return {"error": f"API request failed: {str(e)}"}
    
    def get_channel_videos(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Get list of recent videos from channel
        
        Args:
            max_results: Maximum number of videos to retrieve
            
        Returns:
            List of video metadata dictionaries
        """
        if not self.api_key or not self.channel_id:
            return []
        
        # First get the uploads playlist ID
        channel_info = self.get_channel_info()
        if 'error' in channel_info:
            return []
        
        url = f"{self.youtube_data_api}/search"
        params = {
            'part': 'snippet',
            'channelId': self.channel_id,
            'type': 'video',
            'order': 'date',
            'maxResults': max_results,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            videos = []
            for item in data.get('items', []):
                videos.append({
                    'video_id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'published_at': item['snippet']['publishedAt'],
                    'thumbnail_url': item['snippet']['thumbnails']['high']['url']
                })
            
            return videos
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to fetch videos: {e}")
            return []
    
    def get_video_statistics(self, video_id: str) -> Dict[str, Any]:
        """
        Get detailed statistics for a specific video
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary with video statistics
        """
        if not self.api_key:
            return {"error": "YouTube API key not configured"}
        
        url = f"{self.youtube_data_api}/videos"
        params = {
            'part': 'statistics,contentDetails,snippet',
            'id': video_id,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'items' in data and len(data['items']) > 0:
                video = data['items'][0]
                stats = video['statistics']
                details = video['contentDetails']
                
                return {
                    'video_id': video_id,
                    'views': int(stats.get('viewCount', 0)),
                    'likes': int(stats.get('likeCount', 0)),
                    'comments': int(stats.get('commentCount', 0)),
                    'duration': details['duration'],
                    'published_at': video['snippet']['publishedAt'],
                    'title': video['snippet']['title'],
                    'tags': video['snippet'].get('tags', []),
                    'category_id': video['snippet']['categoryId']
                }
            else:
                return {"error": "Video not found"}
                
        except requests.exceptions.RequestException as e:
            return {"error": f"API request failed: {str(e)}"}
    
    def save_channel_to_database(self, channel_data: Dict[str, Any]) -> bool:
        """
        Save or update channel information in database
        
        Args:
            channel_data: Channel information dictionary
            
        Returns:
            True if successful, False otherwise
        """
        if not self.db_conn:
            if not self.connect_database():
                return False
        
        try:
            cursor = self.db_conn.cursor()
            
            query = """
            INSERT INTO youtube_channels (
                channel_id, channel_name, channel_handle, 
                subscriber_count, video_count, view_count,
                tracking_enabled, updated_at, metadata
            ) VALUES (
                %s, %s, %s, %s, %s, %s, true, NOW(), %s
            )
            ON CONFLICT (channel_id) 
            DO UPDATE SET
                channel_name = EXCLUDED.channel_name,
                channel_handle = EXCLUDED.channel_handle,
                subscriber_count = EXCLUDED.subscriber_count,
                video_count = EXCLUDED.video_count,
                view_count = EXCLUDED.view_count,
                updated_at = NOW(),
                metadata = EXCLUDED.metadata
            """
            
            cursor.execute(query, (
                channel_data['channel_id'],
                channel_data['channel_name'],
                channel_data['channel_handle'],
                channel_data['subscriber_count'],
                channel_data['video_count'],
                channel_data['view_count'],
                json.dumps(channel_data.get('metadata', {}))
            ))
            
            self.db_conn.commit()
            cursor.close()
            
            print(f"✅ Saved channel data for: {channel_data['channel_name']}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save channel data: {e}")
            if self.db_conn:
                self.db_conn.rollback()
            return False
    
    def close(self):
        """Close database connection"""
        if self.db_conn:
            self.db_conn.close()
            print("✅ Database connection closed")


def main():
    """Test the YouTube API client"""
    print("=" * 60)
    print("Yara ❤️ Dell YouTube Intelligence - API Client Test")
    print("=" * 60)
    
    client = YouTubeAPIClient()
    
    # Check configuration
    print("\n📋 Configuration Status:")
    print(f"  Email: {client.email}")
    print(f"  API Key: {'✅ Set' if client.api_key else '❌ Not set'}")
    print(f"  Client ID: {'✅ Set' if client.client_id else '❌ Not set'}")
    print(f"  Channel ID: {client.channel_id if client.channel_id else '❌ Not set'}")
    
    if not client.api_key:
        print("\n⚠️  YouTube API credentials not configured.")
        print("   Follow these steps:")
        print("   1. Go to: https://console.cloud.google.com/")
        print("   2. Create a new project or select existing")
        print("   3. Enable YouTube Data API v3 and YouTube Analytics API")
        print("   4. Create API credentials (API key and OAuth 2.0)")
        print("   5. Add credentials to /Users/arthurdell/YARADELL/config/.env")
        return
    
    # Test database connection
    print("\n🔗 Testing database connection...")
    if client.connect_database():
        print("  ✅ Database connection successful")
    else:
        print("  ❌ Database connection failed")
        return
    
    # If channel ID is set, fetch channel info
    if client.channel_id:
        print(f"\n📺 Fetching channel information for: {client.channel_id}")
        channel_info = client.get_channel_info()
        
        if 'error' not in channel_info:
            print(f"  Channel: {channel_info['channel_name']}")
            print(f"  Subscribers: {channel_info['subscriber_count']:,}")
            print(f"  Videos: {channel_info['video_count']:,}")
            print(f"  Total Views: {channel_info['view_count']:,}")
            
            # Save to database
            if client.save_channel_to_database(channel_info):
                print("  ✅ Channel data saved to database")
        else:
            print(f"  ❌ {channel_info['error']}")
    else:
        print("\n⚠️  Channel ID not configured in .env file")
    
    client.close()
    print("\n✅ Test complete")


if __name__ == "__main__":
    main()

