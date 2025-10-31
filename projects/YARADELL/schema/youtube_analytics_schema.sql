-- Yara ❤️ Dell YouTube Intelligence - Database Schema
-- Applied to: aya_rag
-- Date: 2025-10-25
-- Purpose: Store YouTube audience demographics and behavior analytics

-- =============================================================================
-- CHANNEL TRACKING
-- =============================================================================

CREATE TABLE IF NOT EXISTS youtube_channels (
    id SERIAL PRIMARY KEY,
    channel_id VARCHAR(100) UNIQUE NOT NULL,
    channel_name VARCHAR(255) NOT NULL,
    channel_handle VARCHAR(100),
    subscriber_count BIGINT,
    video_count INTEGER,
    view_count BIGINT,
    tracking_enabled BOOLEAN DEFAULT true,
    agent_session_id VARCHAR(100) REFERENCES agent_sessions(session_id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- =============================================================================
-- AUDIENCE DEMOGRAPHICS
-- =============================================================================

CREATE TABLE IF NOT EXISTS youtube_audience_demographics (
    id SERIAL PRIMARY KEY,
    channel_id VARCHAR(100) REFERENCES youtube_channels(channel_id),
    snapshot_date DATE NOT NULL,
    
    -- Age Distribution
    age_13_17_percent DECIMAL(5,2),
    age_18_24_percent DECIMAL(5,2),
    age_25_34_percent DECIMAL(5,2),
    age_35_44_percent DECIMAL(5,2),
    age_45_54_percent DECIMAL(5,2),
    age_55_64_percent DECIMAL(5,2),
    age_65_plus_percent DECIMAL(5,2),
    
    -- Gender Distribution
    gender_male_percent DECIMAL(5,2),
    gender_female_percent DECIMAL(5,2),
    gender_other_percent DECIMAL(5,2),
    
    -- Geographic Distribution (Top 10)
    geography_data JSONB DEFAULT '[]',
    
    -- Device Distribution
    device_mobile_percent DECIMAL(5,2),
    device_desktop_percent DECIMAL(5,2),
    device_tablet_percent DECIMAL(5,2),
    device_tv_percent DECIMAL(5,2),
    
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    
    UNIQUE(channel_id, snapshot_date)
);

-- =============================================================================
-- AUDIENCE BEHAVIOR
-- =============================================================================

CREATE TABLE IF NOT EXISTS youtube_audience_behavior (
    id SERIAL PRIMARY KEY,
    channel_id VARCHAR(100) REFERENCES youtube_channels(channel_id),
    snapshot_date DATE NOT NULL,
    
    -- Watch Time Metrics
    total_watch_time_hours DECIMAL(12,2),
    average_view_duration_seconds INTEGER,
    average_view_percentage DECIMAL(5,2),
    
    -- Engagement Metrics
    views_total BIGINT,
    likes_total BIGINT,
    comments_total BIGINT,
    shares_total BIGINT,
    engagement_rate DECIMAL(5,2),
    
    -- Viewer Retention
    returning_viewers_percent DECIMAL(5,2),
    new_viewers_percent DECIMAL(5,2),
    subscribers_gained INTEGER,
    subscribers_lost INTEGER,
    
    -- Traffic Sources
    traffic_sources JSONB DEFAULT '{}',
    
    -- Peak Engagement Times (UTC)
    peak_hours JSONB DEFAULT '[]',
    
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    
    UNIQUE(channel_id, snapshot_date)
);

-- =============================================================================
-- CONTENT PERFORMANCE
-- =============================================================================

CREATE TABLE IF NOT EXISTS youtube_content_performance (
    id SERIAL PRIMARY KEY,
    channel_id VARCHAR(100) REFERENCES youtube_channels(channel_id),
    video_id VARCHAR(100) NOT NULL,
    video_title VARCHAR(500),
    published_at TIMESTAMP,
    snapshot_date DATE NOT NULL,
    
    -- Performance Metrics
    views BIGINT,
    likes INTEGER,
    comments INTEGER,
    shares INTEGER,
    watch_time_hours DECIMAL(10,2),
    average_view_duration_seconds INTEGER,
    click_through_rate DECIMAL(5,2),
    
    -- Audience Response
    likes_per_view DECIMAL(8,6),
    comments_per_view DECIMAL(8,6),
    retention_rate DECIMAL(5,2),
    
    -- Content Analysis
    video_duration_seconds INTEGER,
    video_tags JSONB DEFAULT '[]',
    video_category VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    
    UNIQUE(video_id, snapshot_date)
);

-- =============================================================================
-- AI-GENERATED INSIGHTS
-- =============================================================================

CREATE TABLE IF NOT EXISTS youtube_insights_log (
    id SERIAL PRIMARY KEY,
    channel_id VARCHAR(100) REFERENCES youtube_channels(channel_id),
    insight_date DATE NOT NULL,
    insight_type VARCHAR(50), -- 'daily', 'weekly', 'on-demand'
    
    -- Analysis Results
    summary TEXT,
    key_findings JSONB DEFAULT '[]',
    recommendations JSONB DEFAULT '[]',
    
    -- Metrics Context
    analysis_period_start DATE,
    analysis_period_end DATE,
    data_points_analyzed INTEGER,
    
    -- AI Generation
    ai_model_used VARCHAR(100),
    confidence_score DECIMAL(3,2),
    agent_session_id VARCHAR(100) REFERENCES agent_sessions(session_id),
    
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- =============================================================================
-- PERFORMANCE INDEXES
-- =============================================================================

-- Channel lookups
CREATE INDEX IF NOT EXISTS idx_youtube_channels_id ON youtube_channels(channel_id);
CREATE INDEX IF NOT EXISTS idx_youtube_channels_tracking ON youtube_channels(tracking_enabled);

-- Demographics time-series queries
CREATE INDEX IF NOT EXISTS idx_demographics_channel_date ON youtube_audience_demographics(channel_id, snapshot_date DESC);
CREATE INDEX IF NOT EXISTS idx_demographics_date ON youtube_audience_demographics(snapshot_date DESC);

-- Behavior time-series queries
CREATE INDEX IF NOT EXISTS idx_behavior_channel_date ON youtube_audience_behavior(channel_id, snapshot_date DESC);
CREATE INDEX IF NOT EXISTS idx_behavior_engagement ON youtube_audience_behavior(engagement_rate DESC);

-- Content performance queries
CREATE INDEX IF NOT EXISTS idx_content_channel_date ON youtube_content_performance(channel_id, snapshot_date DESC);
CREATE INDEX IF NOT EXISTS idx_content_video ON youtube_content_performance(video_id);
CREATE INDEX IF NOT EXISTS idx_content_published ON youtube_content_performance(published_at DESC);

-- Insights queries
CREATE INDEX IF NOT EXISTS idx_insights_channel_date ON youtube_insights_log(channel_id, insight_date DESC);
CREATE INDEX IF NOT EXISTS idx_insights_type ON youtube_insights_log(insight_type);

-- =============================================================================
-- ANALYTICAL VIEWS
-- =============================================================================

-- Audience Growth Trends (Week-over-week changes)
CREATE OR REPLACE VIEW audience_growth_trends AS
SELECT 
    current_week.channel_id,
    current_week.snapshot_date as current_date,
    prev_week.snapshot_date as previous_date,
    
    -- Subscriber Growth
    (SELECT subscriber_count FROM youtube_channels WHERE channel_id = current_week.channel_id) as current_subscribers,
    
    -- Age Distribution Changes
    (current_week.age_18_24_percent - COALESCE(prev_week.age_18_24_percent, 0)) as age_18_24_change,
    (current_week.age_25_34_percent - COALESCE(prev_week.age_25_34_percent, 0)) as age_25_34_change,
    (current_week.age_35_44_percent - COALESCE(prev_week.age_35_44_percent, 0)) as age_35_44_change,
    
    -- Gender Distribution Changes
    (current_week.gender_male_percent - COALESCE(prev_week.gender_male_percent, 0)) as male_percent_change,
    (current_week.gender_female_percent - COALESCE(prev_week.gender_female_percent, 0)) as female_percent_change
    
FROM youtube_audience_demographics current_week
LEFT JOIN youtube_audience_demographics prev_week 
    ON current_week.channel_id = prev_week.channel_id 
    AND prev_week.snapshot_date = current_week.snapshot_date - INTERVAL '7 days'
ORDER BY current_week.snapshot_date DESC;

-- Engagement Patterns
CREATE OR REPLACE VIEW engagement_patterns AS
SELECT 
    b.channel_id,
    b.snapshot_date,
    b.engagement_rate,
    b.returning_viewers_percent,
    b.peak_hours,
    
    -- Calculate engagement efficiency
    CASE 
        WHEN b.views_total > 0 
        THEN (b.likes_total + b.comments_total + b.shares_total)::DECIMAL / b.views_total 
        ELSE 0 
    END as engagement_efficiency,
    
    -- Traffic source dominance
    b.traffic_sources,
    
    -- Watch time quality
    b.average_view_percentage as retention_quality
    
FROM youtube_audience_behavior b
ORDER BY b.snapshot_date DESC, b.engagement_rate DESC;

-- Actionable Recommendations (Latest AI insights)
CREATE OR REPLACE VIEW actionable_recommendations AS
SELECT 
    i.channel_id,
    c.channel_name,
    i.insight_date,
    i.insight_type,
    i.summary,
    i.recommendations,
    i.confidence_score,
    i.created_at
FROM youtube_insights_log i
JOIN youtube_channels c ON i.channel_id = c.channel_id
WHERE i.insight_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY i.insight_date DESC, i.confidence_score DESC;

-- Content Performance Leaderboard
CREATE OR REPLACE VIEW top_performing_content AS
SELECT 
    cp.channel_id,
    cp.video_id,
    cp.video_title,
    cp.published_at,
    cp.views,
    cp.likes,
    cp.comments,
    cp.watch_time_hours,
    cp.retention_rate,
    cp.click_through_rate,
    
    -- Performance Score (weighted algorithm)
    (
        (cp.views / NULLIF((SELECT MAX(views) FROM youtube_content_performance WHERE channel_id = cp.channel_id), 0)) * 0.3 +
        (cp.retention_rate / 100.0) * 0.3 +
        (cp.click_through_rate / 100.0) * 0.2 +
        (cp.likes_per_view * 1000) * 0.2
    ) as performance_score
    
FROM youtube_content_performance cp
WHERE cp.snapshot_date >= CURRENT_DATE - INTERVAL '90 days'
ORDER BY performance_score DESC
LIMIT 50;

-- =============================================================================
-- HELPER FUNCTIONS
-- =============================================================================

-- Function to calculate engagement rate
CREATE OR REPLACE FUNCTION calculate_engagement_rate(
    likes_count BIGINT,
    comments_count BIGINT,
    shares_count BIGINT,
    views_count BIGINT
) RETURNS DECIMAL(5,2) AS $$
BEGIN
    IF views_count = 0 THEN
        RETURN 0;
    END IF;
    RETURN ((likes_count + comments_count + shares_count)::DECIMAL / views_count * 100);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Grant permissions (if needed)
-- GRANT ALL PRIVILEGES ON youtube_channels, youtube_audience_demographics, 
-- youtube_audience_behavior, youtube_content_performance, youtube_insights_log 
-- TO n8n_user;

-- =============================================================================
-- SCHEMA VERIFICATION
-- =============================================================================

-- Verify tables created
SELECT 
    table_name, 
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public' 
AND table_name LIKE 'youtube_%'
ORDER BY table_name;

