-- Code Validation Audit Trail Schema
-- Database: aya_rag (PostgreSQL 18.0)
-- Purpose: Track all code validations and compliance metrics
-- Created: 2025-10-29

-- =============================================================================
-- CODE VALIDATIONS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS code_validations (
    id SERIAL PRIMARY KEY,
    validation_id VARCHAR(100) UNIQUE NOT NULL,
    file_path TEXT,
    filename VARCHAR(255),
    agent_name VARCHAR(100),
    validation_time TIMESTAMP DEFAULT NOW(),
    model_used VARCHAR(100),
    response_time DECIMAL(10,3),
    issues_detected INTEGER DEFAULT 0,
    severity_counts JSONB DEFAULT '{}',
    enforcement_action VARCHAR(20),
    review_text TEXT,
    code_hash VARCHAR(64),
    n8n_execution_id VARCHAR(100),
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    metadata JSONB DEFAULT '{}'
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_code_validations_time ON code_validations(validation_time);
CREATE INDEX IF NOT EXISTS idx_code_validations_agent ON code_validations(agent_name);
CREATE INDEX IF NOT EXISTS idx_code_validations_file ON code_validations(file_path);
CREATE INDEX IF NOT EXISTS idx_code_validations_execution ON code_validations(n8n_execution_id);
CREATE INDEX IF NOT EXISTS idx_code_validations_action ON code_validations(enforcement_action);

-- =============================================================================
-- COMPLIANCE METRICS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS compliance_metrics (
    date DATE PRIMARY KEY,
    files_validated INTEGER DEFAULT 0,
    critical_issues INTEGER DEFAULT 0,
    high_issues INTEGER DEFAULT 0,
    medium_issues INTEGER DEFAULT 0,
    low_issues INTEGER DEFAULT 0,
    blocked_operations INTEGER DEFAULT 0,
    warned_operations INTEGER DEFAULT 0,
    compliance_score DECIMAL(5,2),
    avg_response_time DECIMAL(10,3),
    metadata JSONB DEFAULT '{}',
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for date queries
CREATE INDEX IF NOT EXISTS idx_compliance_metrics_date ON compliance_metrics(date DESC);

-- =============================================================================
-- CODE VALIDATION OVERRIDES TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS code_validation_overrides (
    id SERIAL PRIMARY KEY,
    validation_id VARCHAR(100) REFERENCES code_validations(validation_id),
    agent_name VARCHAR(100),
    override_reason TEXT NOT NULL,
    approved_by VARCHAR(100),
    override_time TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Index for tracking overrides
CREATE INDEX IF NOT EXISTS idx_overrides_validation ON code_validation_overrides(validation_id);
CREATE INDEX IF NOT EXISTS idx_overrides_agent ON code_validation_overrides(agent_name);

-- =============================================================================
-- COMMENTS
-- =============================================================================

COMMENT ON TABLE code_validations IS 'Complete audit trail of all code validations performed';
COMMENT ON COLUMN code_validations.validation_id IS 'Unique validation identifier';
COMMENT ON COLUMN code_validations.severity_counts IS 'JSONB: {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}';
COMMENT ON COLUMN code_validations.enforcement_action IS 'block, warn, log, pass';
COMMENT ON COLUMN code_validations.code_hash IS 'SHA256 hash of validated code for deduplication';

COMMENT ON TABLE compliance_metrics IS 'Daily aggregated compliance metrics';
COMMENT ON COLUMN compliance_metrics.compliance_score IS 'Percentage (0-100) of files meeting standards';

COMMENT ON TABLE code_validation_overrides IS 'Track manual overrides of blocked validations';

-- =============================================================================
-- HELPER FUNCTIONS
-- =============================================================================

-- Function to update compliance metrics
CREATE OR REPLACE FUNCTION update_compliance_metrics()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO compliance_metrics (
        date,
        files_validated,
        critical_issues,
        high_issues,
        medium_issues,
        low_issues,
        blocked_operations,
        warned_operations,
        avg_response_time
    )
    SELECT
        DATE(validation_time) as date,
        COUNT(*) as files_validated,
        SUM((severity_counts->>'CRITICAL')::INTEGER) as critical_issues,
        SUM((severity_counts->>'HIGH')::INTEGER) as high_issues,
        SUM((severity_counts->>'MEDIUM')::INTEGER) as medium_issues,
        SUM((severity_counts->>'LOW')::INTEGER) as low_issues,
        SUM(CASE WHEN enforcement_action = 'block' THEN 1 ELSE 0 END) as blocked_operations,
        SUM(CASE WHEN enforcement_action = 'warn' THEN 1 ELSE 0 END) as warned_operations,
        AVG(response_time) as avg_response_time
    FROM code_validations
    WHERE DATE(validation_time) = CURRENT_DATE
        AND success = true
    GROUP BY DATE(validation_time)
    ON CONFLICT (date) DO UPDATE SET
        files_validated = EXCLUDED.files_validated,
        critical_issues = EXCLUDED.critical_issues,
        high_issues = EXCLUDED.high_issues,
        medium_issues = EXCLUDED.medium_issues,
        low_issues = EXCLUDED.low_issues,
        blocked_operations = EXCLUDED.blocked_operations,
        warned_operations = EXCLUDED.warned_operations,
        avg_response_time = EXCLUDED.avg_response_time,
        updated_at = NOW();
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update metrics (runs daily via scheduled job)
-- Note: This would typically be called by a scheduled n8n workflow

-- =============================================================================
-- INITIAL DATA
-- =============================================================================

-- Insert today's initial metrics record (if not exists)
INSERT INTO compliance_metrics (date, compliance_score)
VALUES (CURRENT_DATE, 100.0)
ON CONFLICT (date) DO NOTHING;

