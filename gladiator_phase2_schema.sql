-- =============================================================================
-- GLADIATOR PHASE 2 SCHEMA - INTELLIGENCE & PSYOPS
-- =============================================================================
-- Purpose: Document future Phase 2 capabilities in database
-- Status: PLANNED (not yet executing, Phase 0 first)
-- Execution: After Phase 0 complete (Week 0+)
-- =============================================================================

BEGIN;

-- =============================================================================
-- PART 1: BLUE → RED INTELLIGENCE HANDOFF
-- =============================================================================

CREATE TABLE IF NOT EXISTS gladiator_blue_to_red_intelligence (
    id SERIAL PRIMARY KEY,
    
    -- Source (Blue Team Detection)
    detected_at TIMESTAMP DEFAULT NOW(),
    customer_node_id VARCHAR(50),
    detection_gate NUMERIC(3,2),  -- Gate level when detected
    
    -- Attack Analysis (Blue Team)
    attack_vector VARCHAR(100),  -- 'phishing_email', 'malware_download', 'exploit_kit', 'zero_day'
    entry_point TEXT,  -- Specific URL, email, file
    ttp_sequence JSONB,  -- MITRE tactics/techniques observed
    attacker_infrastructure TEXT[],  -- IPs, domains, C2 servers
    tools_identified TEXT[],  -- Malware families, exploit kits
    
    -- Classification
    traditional_pattern_match VARCHAR(200),  -- Known CVE or MITRE technique
    gladiator_pattern_match INTEGER,  -- Match to training patterns
    zero_day_candidate BOOLEAN DEFAULT FALSE,
    confidence_score NUMERIC(5,2),
    
    -- Intelligence Value
    intelligence_priority VARCHAR(20) DEFAULT 'medium',  -- 'low', 'medium', 'high', 'critical'
    novel_ttp BOOLEAN DEFAULT FALSE,
    
    -- Red Team Handoff
    passed_to_red_team BOOLEAN DEFAULT FALSE,
    red_team_acknowledged_at TIMESTAMP,
    red_team_response_strategy VARCHAR(50),  -- 'passive', 'honeypot', 'psyops', 'combat'
    
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_blue_red_intel_priority ON gladiator_blue_to_red_intelligence(intelligence_priority);
CREATE INDEX idx_blue_red_intel_zero_day ON gladiator_blue_to_red_intelligence(zero_day_candidate);
CREATE INDEX idx_blue_red_intel_handoff ON gladiator_blue_to_red_intelligence(passed_to_red_team);

-- =============================================================================
-- PART 2: HONEYPOT DEPLOYMENT & MONITORING
-- =============================================================================

CREATE TABLE IF NOT EXISTS gladiator_honeypots (
    id SERIAL PRIMARY KEY,
    customer_node_id VARCHAR(50),
    intelligence_trigger_id INTEGER REFERENCES gladiator_blue_to_red_intelligence(id),
    
    -- Deployment
    honeypot_type VARCHAR(50),  -- 'email_server', 'database', 'ssh', 'web_app', 'api'
    deployed_at TIMESTAMP DEFAULT NOW(),
    deployment_location TEXT,  -- NOT customer infrastructure (neutral hosting)
    
    -- Target Profile
    target_attacker_profile JSONB,
    designed_to_attract VARCHAR(100),  -- What lure we're using
    
    -- Fake Assets Planted
    fake_vulnerabilities TEXT[],
    fake_data_type VARCHAR(100),  -- 'executive_emails', 'customer_db', 'financial_records'
    fake_data_volume_gb NUMERIC(8,2),
    
    -- Monitoring
    surveillance_config JSONB,
    attacker_engagements INTEGER DEFAULT 0,
    unique_attackers INTEGER DEFAULT 0,
    
    -- Intelligence Collected
    tools_observed TEXT[],
    ttps_observed JSONB,
    c2_servers_identified TEXT[],
    exfil_methods_observed TEXT[],
    zero_day_exploits_captured TEXT[],
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',  -- 'active', 'engaged', 'intel_gathered', 'decommissioned'
    clean BOOLEAN DEFAULT TRUE,  -- Part of clean state validation
    intelligence_extracted BOOLEAN DEFAULT FALSE,
    
    -- Decommission
    decommissioned_at TIMESTAMP,
    reason_decommissioned TEXT,
    
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_honeypots_customer ON gladiator_honeypots(customer_node_id);
CREATE INDEX idx_honeypots_status ON gladiator_honeypots(status);
CREATE INDEX idx_honeypots_clean ON gladiator_honeypots(clean);

-- =============================================================================
-- PART 3: DARK WEB PSYOPS OPERATIONS
-- =============================================================================

CREATE TABLE IF NOT EXISTS gladiator_psyops_operations (
    id SERIAL PRIMARY KEY,
    customer_node_id VARCHAR(50),
    intelligence_source_id INTEGER REFERENCES gladiator_blue_to_red_intelligence(id),
    
    -- Operation Type
    operation_type VARCHAR(50),  -- 'mistrust_creation', 'disinformation', 'tool_backdoor', 'financial_disruption', 'community_fracture'
    operation_name VARCHAR(200),
    
    -- Target
    target_community VARCHAR(100),  -- 'darkweb_forum_xyz', 'telegram_channel', 'irc_channel'
    target_attacker_group VARCHAR(100),
    
    -- Cover Identity (CRITICAL)
    cover_persona VARCHAR(100),  -- NEVER real identity
    persona_backstory TEXT,
    persona_burnable BOOLEAN DEFAULT TRUE,  -- Can be discarded after op
    
    -- Content
    message_planted TEXT,
    disinformation_type VARCHAR(50),  -- 'informant_accusation', 'tool_backdoor_claim', 'payment_fraud'
    evidence_fabricated JSONB,
    
    -- Breadcrumbs (False Attribution)
    false_attribution_target VARCHAR(100),  -- Who we're framing
    breadcrumbs_planted TEXT[],
    attribution_plausibility NUMERIC(3,2),  -- Must be >0.90
    
    -- Operational Security (CRITICAL)
    customer_identity_risk NUMERIC(3,2),  -- Must be <0.10
    gladiator_identity_risk NUMERIC(3,2),  -- Must be <0.10
    plausible_deniability_score NUMERIC(3,2),  -- Must be >0.90
    
    -- OPSEC Validation
    opsec_checks JSONB,
    opsec_approved BOOLEAN,
    opsec_approved_by VARCHAR(100),
    
    -- Execution
    executed_at TIMESTAMP,
    execution_method JSONB,  -- Tor config, VPN chain, compromised server details
    
    -- Results
    community_response TEXT,
    mistrust_created BOOLEAN DEFAULT FALSE,
    trust_degradation_percentage NUMERIC(5,2),
    attacker_activity_reduced BOOLEAN DEFAULT FALSE,
    operation_successful BOOLEAN,
    
    -- Risk Assessment
    identity_disclosure_detected BOOLEAN DEFAULT FALSE,
    operation_compromised BOOLEAN DEFAULT FALSE,
    
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_psyops_customer ON gladiator_psyops_operations(customer_node_id);
CREATE INDEX idx_psyops_type ON gladiator_psyops_operations(operation_type);
CREATE INDEX idx_psyops_opsec ON gladiator_psyops_operations(opsec_approved);

-- =============================================================================
-- PART 4: CLEAN STATE VALIDATIONS
-- =============================================================================

CREATE TABLE IF NOT EXISTS gladiator_clean_state_validations (
    id SERIAL PRIMARY KEY,
    customer_node_id VARCHAR(50),
    validated_at TIMESTAMP DEFAULT NOW(),
    validation_type VARCHAR(50) DEFAULT 'scheduled',  -- 'scheduled', 'on_demand', 'post_incident'
    
    -- Clean State Criteria
    no_active_intrusions BOOLEAN,
    active_intrusions_count INTEGER DEFAULT 0,
    
    no_malware_detected BOOLEAN,
    malware_items_found INTEGER DEFAULT 0,
    
    honeypots_clean BOOLEAN,
    honeypots_with_activity INTEGER DEFAULT 0,
    honeypots_intel_extracted BOOLEAN,
    
    perimeter_secure BOOLEAN,
    open_vulnerabilities INTEGER DEFAULT 0,
    
    zero_day_protection_active BOOLEAN,
    zero_days_blocked_24h INTEGER DEFAULT 0,
    
    -- Performance Metrics
    threats_blocked_24h INTEGER DEFAULT 0,
    false_positives_24h INTEGER DEFAULT 0,
    false_positive_rate NUMERIC(5,2),
    
    -- Overall Status
    clean_state_achieved BOOLEAN,
    
    -- Recommendations
    recommended_gate_level NUMERIC(3,2),
    escalation_warranted BOOLEAN DEFAULT FALSE,
    escalation_reason TEXT,
    
    -- Next Validation
    next_validation_due TIMESTAMP,
    
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_clean_state_customer ON gladiator_clean_state_validations(customer_node_id);
CREATE INDEX idx_clean_state_achieved ON gladiator_clean_state_validations(clean_state_achieved);

-- =============================================================================
-- PART 5: AGENT COORDINATION (Multi-Agent Execution)
-- =============================================================================

CREATE TABLE IF NOT EXISTS gladiator_agent_coordination (
    id SERIAL PRIMARY KEY,
    
    -- Agent Identity
    agent_id VARCHAR(50) NOT NULL,  -- 'cursor', 'agent_2', 'agent_3'
    agent_type VARCHAR(50),  -- 'autonomous', 'supervised', 'specialist'
    
    -- Work Assignment
    assigned_phase VARCHAR(20),  -- 'phase_0', 'phase_2', etc.
    assigned_week INTEGER,  -- -14, -13, etc.
    assigned_task VARCHAR(200),
    
    -- Execution
    started_at TIMESTAMP,
    last_heartbeat TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'idle',  -- 'idle', 'working', 'blocked', 'complete'
    
    -- Coordination
    depends_on_agent VARCHAR(50),  -- Another agent's work
    blocks_agent VARCHAR(50),  -- Blocking another agent
    
    -- Conflict Prevention
    locked_resources TEXT[],  -- Tables, files, systems being modified
    lock_acquired_at TIMESTAMP,
    lock_expires_at TIMESTAMP,
    
    -- Progress
    progress_percentage INTEGER DEFAULT 0,
    current_step TEXT,
    
    -- Completion
    completed_at TIMESTAMP,
    deliverables TEXT[],
    
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_agent_coord_agent ON gladiator_agent_coordination(agent_id);
CREATE INDEX idx_agent_coord_status ON gladiator_agent_coordination(status);
CREATE INDEX idx_agent_coord_phase ON gladiator_agent_coordination(assigned_phase);

-- =============================================================================
-- FUNCTIONS FOR AGENT COORDINATION
-- =============================================================================

-- Function: Acquire work lock (prevent conflicts)
CREATE OR REPLACE FUNCTION acquire_agent_lock(
    p_agent_id VARCHAR(50),
    p_resource TEXT,
    p_duration_minutes INTEGER DEFAULT 60
) RETURNS BOOLEAN AS $$
DECLARE
    existing_lock RECORD;
BEGIN
    -- Check if resource already locked
    SELECT * INTO existing_lock
    FROM gladiator_agent_coordination
    WHERE p_resource = ANY(locked_resources)
      AND lock_expires_at > NOW()
      AND agent_id != p_agent_id
      AND status = 'working';
    
    IF FOUND THEN
        -- Resource locked by another agent
        RETURN FALSE;
    END IF;
    
    -- Acquire lock
    INSERT INTO gladiator_agent_coordination (
        agent_id, locked_resources, lock_acquired_at, lock_expires_at, status
    ) VALUES (
        p_agent_id,
        ARRAY[p_resource],
        NOW(),
        NOW() + (p_duration_minutes || ' minutes')::INTERVAL,
        'working'
    );
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Function: Release work lock
CREATE OR REPLACE FUNCTION release_agent_lock(
    p_agent_id VARCHAR(50),
    p_resource TEXT
) RETURNS VOID AS $$
BEGIN
    UPDATE gladiator_agent_coordination
    SET 
        status = 'complete',
        completed_at = NOW(),
        locked_resources = array_remove(locked_resources, p_resource)
    WHERE agent_id = p_agent_id
      AND p_resource = ANY(locked_resources);
END;
$$ LANGUAGE plpgsql;

COMMIT;

-- =============================================================================
-- PHASE DEFINITIONS IN DATABASE
-- =============================================================================

-- Add phase definitions for complete project tracking
INSERT INTO gladiator_phase_milestones (
    phase, week_number, milestone_name, milestone_type,
    planned_start_date, estimated_duration_days,
    status, validation_required, blocking, notes
) VALUES 
-- Phase 2: Intelligence & PSYOPS (Post-Production)
(
    'phase_2',
    NULL,  -- Not week-based, post-Phase 0
    'Phase 2: Blue-Red Intelligence Handoff Protocol',
    'feature_development',
    '2026-03-01',  -- After Phase 0 complete
    14,
    'planned',
    TRUE,
    FALSE,
    'Implement Blue→Red intelligence handoff. Blue detects intrusion, analyzes, passes complete profile to Red Team for tactical/combat response.'
),
(
    'phase_2',
    NULL,
    'Phase 2: Honeypot Deployment System',
    'feature_development',
    '2026-03-15',
    21,
    'planned',
    TRUE,
    FALSE,
    'Deploy honeypot orchestration system. Target attacker profiles, gather intelligence on tools/TTPs/C2, extract zero-day exploits.'
),
(
    'phase_2',
    NULL,
    'Phase 2: Dark Web PSYOPS Capabilities',
    'feature_development',
    '2026-04-05',
    30,
    'planned',
    TRUE,
    TRUE,  -- BLOCKING: OPSEC critical
    'Implement dark web psychological operations. Mistrust creation, disinformation, community disruption. CRITICAL: Identity protection (customer + GLADIATOR) with <10% disclosure risk.'
),
(
    'phase_2',
    NULL,
    'Phase 2: Clean State Validation Protocol',
    'feature_development',
    '2026-05-05',
    7,
    'planned',
    TRUE,
    FALSE,
    'Define and implement clean state validation: No intrusions, no malware, clean honeypots, secure perimeter. Success criteria for customer protection.'
),
(
    'phase_2',
    NULL,
    'Phase 2: Combat Ready Tier Deployment',
    'deliverable',
    '2026-05-12',
    14,
    'planned',
    TRUE,
    TRUE,
    'Deploy complete passive→tactical→combat escalation. Liability transfer contracts. Evidence chain validation. Customer authorization workflow.'
) ON CONFLICT DO NOTHING;

-- =============================================================================
-- SUMMARY
-- =============================================================================

-- Phase 0: Red/Blue Training (Week -14 to Week 0) - IN PROGRESS
-- Phase 1: Production Deployment (Week 0+) - PLANNED
-- Phase 2: Intelligence & PSYOPS (Post-Production) - PLANNED (this schema)
-- Phase 3: Scale & Evolution (Ongoing) - PLANNED

-- Agent coordination tables ensure multiple agents can work simultaneously
-- without conflicts by acquiring locks on resources before modification

-- =============================================================================
-- END OF PHASE 2 SCHEMA
-- =============================================================================

