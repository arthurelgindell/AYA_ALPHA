#!/usr/bin/env python3
"""
Yara ❤️ Dell YouTube Intelligence - Audience Analyzer
Demographics and behavior analysis engine with LM Studio insights
"""

import os
import json
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/Users/arthurdell/YARADELL/config/.env')


class AudienceAnalyzer:
    """Analyze YouTube audience demographics and behavior patterns"""
    
    def __init__(self):
        self.db_conn = None
        self.lm_studio_host = os.getenv('LM_STUDIO_HOST', 'http://alpha.tail5f2bae.ts.net:1234')
        
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
    
    def get_demographic_trends(self, channel_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Analyze demographic trends over time period
        
        Args:
            channel_id: YouTube channel ID
            days: Number of days to analyze
            
        Returns:
            Dictionary with demographic analysis
        """
        if not self.db_conn:
            self.connect_database()
        
        try:
            cursor = self.db_conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
            SELECT 
                snapshot_date,
                age_18_24_percent,
                age_25_34_percent,
                age_35_44_percent,
                age_45_54_percent,
                gender_male_percent,
                gender_female_percent,
                geography_data,
                device_mobile_percent,
                device_desktop_percent
            FROM youtube_audience_demographics
            WHERE channel_id = %s 
                AND snapshot_date >= CURRENT_DATE - INTERVAL '%s days'
            ORDER BY snapshot_date ASC
            """
            
            cursor.execute(query, (channel_id, days))
            rows = cursor.fetchall()
            cursor.close()
            
            if not rows:
                return {"error": "No demographic data found"}
            
            # Calculate trends
            first_snapshot = dict(rows[0])
            latest_snapshot = dict(rows[-1])
            
            analysis = {
                'period_days': days,
                'snapshots_count': len(rows),
                'age_distribution': {
                    '18-24': latest_snapshot.get('age_18_24_percent', 0),
                    '25-34': latest_snapshot.get('age_25_34_percent', 0),
                    '35-44': latest_snapshot.get('age_35_44_percent', 0),
                    '45-54': latest_snapshot.get('age_45_54_percent', 0)
                },
                'age_trends': {
                    '18-24_change': self._calculate_change(
                        first_snapshot.get('age_18_24_percent'),
                        latest_snapshot.get('age_18_24_percent')
                    ),
                    '25-34_change': self._calculate_change(
                        first_snapshot.get('age_25_34_percent'),
                        latest_snapshot.get('age_25_34_percent')
                    )
                },
                'gender_distribution': {
                    'male': latest_snapshot.get('gender_male_percent', 0),
                    'female': latest_snapshot.get('gender_female_percent', 0)
                },
                'device_preferences': {
                    'mobile': latest_snapshot.get('device_mobile_percent', 0),
                    'desktop': latest_snapshot.get('device_desktop_percent', 0)
                },
                'top_geographies': latest_snapshot.get('geography_data', [])
            }
            
            return analysis
            
        except Exception as e:
            print(f"❌ Failed to analyze demographics: {e}")
            return {"error": str(e)}
    
    def get_behavior_insights(self, channel_id: str, days: int = 7) -> Dict[str, Any]:
        """
        Analyze audience behavior patterns
        
        Args:
            channel_id: YouTube channel ID
            days: Number of days to analyze
            
        Returns:
            Dictionary with behavior insights
        """
        if not self.db_conn:
            self.connect_database()
        
        try:
            cursor = self.db_conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
            SELECT 
                snapshot_date,
                total_watch_time_hours,
                average_view_duration_seconds,
                average_view_percentage,
                views_total,
                likes_total,
                comments_total,
                engagement_rate,
                returning_viewers_percent,
                new_viewers_percent,
                subscribers_gained,
                subscribers_lost,
                traffic_sources,
                peak_hours
            FROM youtube_audience_behavior
            WHERE channel_id = %s 
                AND snapshot_date >= CURRENT_DATE - INTERVAL '%s days'
            ORDER BY snapshot_date ASC
            """
            
            cursor.execute(query, (channel_id, days))
            rows = cursor.fetchall()
            cursor.close()
            
            if not rows:
                return {"error": "No behavior data found"}
            
            # Aggregate metrics
            total_watch_time = sum(r.get('total_watch_time_hours', 0) for r in rows)
            total_views = sum(r.get('views_total', 0) for r in rows)
            total_engagement = sum(r.get('engagement_rate', 0) for r in rows)
            avg_engagement = total_engagement / len(rows) if rows else 0
            
            latest = dict(rows[-1])
            
            insights = {
                'period_days': days,
                'watch_time': {
                    'total_hours': round(total_watch_time, 2),
                    'average_duration_seconds': latest.get('average_view_duration_seconds', 0),
                    'retention_percent': latest.get('average_view_percentage', 0)
                },
                'engagement': {
                    'total_views': total_views,
                    'total_likes': sum(r.get('likes_total', 0) for r in rows),
                    'total_comments': sum(r.get('comments_total', 0) for r in rows),
                    'average_engagement_rate': round(avg_engagement, 2)
                },
                'audience_loyalty': {
                    'returning_viewers': latest.get('returning_viewers_percent', 0),
                    'new_viewers': latest.get('new_viewers_percent', 0),
                    'net_subscribers': latest.get('subscribers_gained', 0) - latest.get('subscribers_lost', 0)
                },
                'traffic_sources': latest.get('traffic_sources', {}),
                'peak_engagement_hours': latest.get('peak_hours', [])
            }
            
            return insights
            
        except Exception as e:
            print(f"❌ Failed to analyze behavior: {e}")
            return {"error": str(e)}
    
    def get_content_performance(self, channel_id: str, days: int = 30, limit: int = 10) -> List[Dict]:
        """
        Analyze top performing content
        
        Args:
            channel_id: YouTube channel ID
            days: Number of days to analyze
            limit: Maximum number of videos to return
            
        Returns:
            List of top performing videos
        """
        if not self.db_conn:
            self.connect_database()
        
        try:
            cursor = self.db_conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
            SELECT 
                video_id,
                video_title,
                published_at,
                views,
                likes,
                comments,
                watch_time_hours,
                retention_rate,
                click_through_rate,
                (views * retention_rate * click_through_rate) as performance_score
            FROM youtube_content_performance
            WHERE channel_id = %s 
                AND snapshot_date >= CURRENT_DATE - INTERVAL '%s days'
            ORDER BY performance_score DESC
            LIMIT %s
            """
            
            cursor.execute(query, (channel_id, days, limit))
            rows = cursor.fetchall()
            cursor.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            print(f"❌ Failed to analyze content: {e}")
            return []
    
    def generate_insights_with_lm_studio(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate actionable insights using LM Studio AI
        
        Args:
            analysis_data: Combined analysis data from demographics and behavior
            
        Returns:
            Dictionary with AI-generated insights and recommendations
        """
        prompt = f"""Analyze this YouTube channel audience data and provide 3 specific, actionable recommendations for channel growth:

DEMOGRAPHICS:
{json.dumps(analysis_data.get('demographics', {}), indent=2)}

BEHAVIOR:
{json.dumps(analysis_data.get('behavior', {}), indent=2)}

TOP CONTENT:
{json.dumps(analysis_data.get('top_content', [])[:3], indent=2)}

Provide your response in this exact JSON format:
{{
    "summary": "Brief 2-3 sentence overview of key findings",
    "key_findings": ["Finding 1", "Finding 2", "Finding 3"],
    "recommendations": [
        {{"action": "Specific action to take", "reason": "Why this matters", "expected_impact": "What to expect"}},
        {{"action": "Specific action to take", "reason": "Why this matters", "expected_impact": "What to expect"}},
        {{"action": "Specific action to take", "reason": "Why this matters", "expected_impact": "What to expect"}}
    ],
    "confidence": 0.85
}}"""
        
        try:
            response = requests.post(
                f"{self.lm_studio_host}/v1/chat/completions",
                json={
                    "model": "default",
                    "messages": [
                        {"role": "system", "content": "You are a YouTube growth strategist analyzing Yara ❤️ Dell's channel data."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content']
                
                # Try to parse as JSON
                try:
                    insights = json.loads(ai_response)
                    return insights
                except json.JSONDecodeError:
                    # If not JSON, return as text
                    return {
                        "summary": ai_response,
                        "key_findings": [],
                        "recommendations": [],
                        "confidence": 0.5
                    }
            else:
                print(f"❌ LM Studio error: {response.status_code}")
                return {"error": "Failed to generate insights"}
                
        except Exception as e:
            print(f"❌ LM Studio request failed: {e}")
            return {"error": str(e)}
    
    def save_insights_to_database(self, channel_id: str, insights: Dict[str, Any], 
                                   insight_type: str = 'daily') -> bool:
        """
        Save AI-generated insights to database
        
        Args:
            channel_id: YouTube channel ID
            insights: Insights dictionary from LM Studio
            insight_type: Type of insight ('daily', 'weekly', 'on-demand')
            
        Returns:
            True if successful
        """
        if not self.db_conn:
            self.connect_database()
        
        try:
            cursor = self.db_conn.cursor()
            
            query = """
            INSERT INTO youtube_insights_log (
                channel_id,
                insight_date,
                insight_type,
                summary,
                key_findings,
                recommendations,
                analysis_period_start,
                analysis_period_end,
                ai_model_used,
                confidence_score
            ) VALUES (
                %s, CURRENT_DATE, %s, %s, %s, %s, 
                CURRENT_DATE - INTERVAL '7 days',
                CURRENT_DATE,
                'lm-studio',
                %s
            )
            """
            
            cursor.execute(query, (
                channel_id,
                insight_type,
                insights.get('summary', ''),
                json.dumps(insights.get('key_findings', [])),
                json.dumps(insights.get('recommendations', [])),
                insights.get('confidence', 0.5)
            ))
            
            self.db_conn.commit()
            cursor.close()
            
            print(f"✅ Saved insights to database")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save insights: {e}")
            if self.db_conn:
                self.db_conn.rollback()
            return False
    
    def run_complete_analysis(self, channel_id: str) -> Dict[str, Any]:
        """
        Run complete audience analysis pipeline
        
        Args:
            channel_id: YouTube channel ID
            
        Returns:
            Complete analysis with AI insights
        """
        print("=" * 60)
        print("Yara ❤️ Dell - Complete Audience Analysis")
        print("=" * 60)
        
        # Gather all data
        demographics = self.get_demographic_trends(channel_id, days=30)
        behavior = self.get_behavior_insights(channel_id, days=7)
        top_content = self.get_content_performance(channel_id, days=30, limit=10)
        
        analysis_data = {
            'demographics': demographics,
            'behavior': behavior,
            'top_content': top_content
        }
        
        print("\n📊 Analysis Data Collected:")
        print(f"  Demographics: {'✅' if 'error' not in demographics else '❌'}")
        print(f"  Behavior: {'✅' if 'error' not in behavior else '❌'}")
        print(f"  Top Content: {len(top_content)} videos")
        
        # Generate AI insights
        print("\n🤖 Generating insights with LM Studio...")
        insights = self.generate_insights_with_lm_studio(analysis_data)
        
        if 'error' not in insights:
            print("✅ Insights generated successfully")
            # Save to database
            self.save_insights_to_database(channel_id, insights, 'on-demand')
        else:
            print(f"❌ Insights generation failed: {insights['error']}")
        
        return {
            'analysis': analysis_data,
            'insights': insights,
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_change(self, old_value: Optional[float], new_value: Optional[float]) -> float:
        """Calculate percentage change between two values"""
        if old_value is None or new_value is None or old_value == 0:
            return 0.0
        return round(((new_value - old_value) / old_value) * 100, 2)
    
    def close(self):
        """Close database connection"""
        if self.db_conn:
            self.db_conn.close()
            print("✅ Database connection closed")


def main():
    """Test the audience analyzer"""
    analyzer = AudienceAnalyzer()
    
    # Get channel ID from environment
    channel_id = os.getenv('YOUTUBE_CHANNEL_ID')
    
    if not channel_id:
        print("❌ YOUTUBE_CHANNEL_ID not configured in .env")
        return
    
    # Run complete analysis
    result = analyzer.run_complete_analysis(channel_id)
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(json.dumps(result, indent=2))
    
    analyzer.close()


if __name__ == "__main__":
    main()

