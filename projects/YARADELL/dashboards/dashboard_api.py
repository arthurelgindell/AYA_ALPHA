#!/usr/bin/env python3
"""
Yara ❤️ Dell YouTube Intelligence - Dashboard API
Flask API to serve real-time data to dashboards
"""

import os
import json
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/Users/arthurdell/YARADELL/config/.env')

app = Flask(__name__)
CORS(app)


def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=os.getenv('POSTGRES_PORT', '5432'),
        database=os.getenv('POSTGRES_DB', 'aya_rag'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD')
    )


@app.route('/')
def index():
    """Serve main dashboard"""
    return send_from_directory('/Users/arthurdell/YARADELL/dashboards', 'audience_insights.html')


@app.route('/api/channel/stats')
def get_channel_stats():
    """Get channel statistics"""
    try:
        channel_id = os.getenv('YOUTUBE_CHANNEL_ID')
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get channel info
        cursor.execute("""
            SELECT subscriber_count, video_count, view_count
            FROM youtube_channels
            WHERE channel_id = %s
        """, (channel_id,))
        
        channel = cursor.fetchone()
        
        # Get latest behavior metrics
        cursor.execute("""
            SELECT 
                engagement_rate,
                total_watch_time_hours,
                views_total
            FROM youtube_audience_behavior
            WHERE channel_id = %s
            ORDER BY snapshot_date DESC
            LIMIT 1
        """, (channel_id,))
        
        behavior = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'subscribers': channel['subscriber_count'] if channel else 0,
            'total_views': channel['view_count'] if channel else 0,
            'engagement_rate': float(behavior['engagement_rate']) if behavior else 0,
            'watch_time_hours': float(behavior['total_watch_time_hours']) if behavior else 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/demographics/age')
def get_age_demographics():
    """Get age distribution"""
    try:
        channel_id = os.getenv('YOUTUBE_CHANNEL_ID')
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT 
                age_13_17_percent,
                age_18_24_percent,
                age_25_34_percent,
                age_35_44_percent,
                age_45_54_percent,
                age_55_64_percent,
                age_65_plus_percent
            FROM youtube_audience_demographics
            WHERE channel_id = %s
            ORDER BY snapshot_date DESC
            LIMIT 1
        """, (channel_id,))
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            return jsonify({
                '13-17': float(row['age_13_17_percent'] or 0),
                '18-24': float(row['age_18_24_percent'] or 0),
                '25-34': float(row['age_25_34_percent'] or 0),
                '35-44': float(row['age_35_44_percent'] or 0),
                '45-54': float(row['age_45_54_percent'] or 0),
                '55-64': float(row['age_55_64_percent'] or 0),
                '65+': float(row['age_65_plus_percent'] or 0)
            })
        else:
            return jsonify({'error': 'No data'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/demographics/gender')
def get_gender_demographics():
    """Get gender distribution"""
    try:
        channel_id = os.getenv('YOUTUBE_CHANNEL_ID')
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT 
                gender_male_percent,
                gender_female_percent,
                gender_other_percent
            FROM youtube_audience_demographics
            WHERE channel_id = %s
            ORDER BY snapshot_date DESC
            LIMIT 1
        """, (channel_id,))
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            return jsonify({
                'male': float(row['gender_male_percent'] or 0),
                'female': float(row['gender_female_percent'] or 0),
                'other': float(row['gender_other_percent'] or 0)
            })
        else:
            return jsonify({'error': 'No data'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/demographics/devices')
def get_device_demographics():
    """Get device distribution"""
    try:
        channel_id = os.getenv('YOUTUBE_CHANNEL_ID')
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT 
                device_mobile_percent,
                device_desktop_percent,
                device_tablet_percent,
                device_tv_percent
            FROM youtube_audience_demographics
            WHERE channel_id = %s
            ORDER BY snapshot_date DESC
            LIMIT 1
        """, (channel_id,))
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            return jsonify({
                'mobile': float(row['device_mobile_percent'] or 0),
                'desktop': float(row['device_desktop_percent'] or 0),
                'tablet': float(row['device_tablet_percent'] or 0),
                'tv': float(row['device_tv_percent'] or 0)
            })
        else:
            return jsonify({'error': 'No data'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/engagement/trend')
def get_engagement_trend():
    """Get engagement rate trend (last 7 days)"""
    try:
        channel_id = os.getenv('YOUTUBE_CHANNEL_ID')
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT 
                snapshot_date,
                engagement_rate
            FROM youtube_audience_behavior
            WHERE channel_id = %s
                AND snapshot_date >= CURRENT_DATE - INTERVAL '7 days'
            ORDER BY snapshot_date ASC
        """, (channel_id,))
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            'dates': [row['snapshot_date'].strftime('%Y-%m-%d') for row in rows],
            'engagement': [float(row['engagement_rate']) for row in rows]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/insights/latest')
def get_latest_insights():
    """Get latest AI-generated insights"""
    try:
        channel_id = os.getenv('YOUTUBE_CHANNEL_ID')
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT 
                summary,
                key_findings,
                recommendations,
                confidence_score,
                insight_date
            FROM youtube_insights_log
            WHERE channel_id = %s
            ORDER BY insight_date DESC
            LIMIT 1
        """, (channel_id,))
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            return jsonify({
                'summary': row['summary'],
                'key_findings': json.loads(row['key_findings']),
                'recommendations': json.loads(row['recommendations']),
                'confidence': float(row['confidence_score']),
                'date': row['insight_date'].strftime('%Y-%m-%d')
            })
        else:
            return jsonify({'error': 'No insights available'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('DASHBOARD_PORT', 8080))
    print(f"🚀 Yara ❤️ Dell Dashboard API starting on port {port}")
    print(f"   Dashboard: http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)

