-- AYA Bulletproof Orchestration Functions
-- Database: aya_rag (PostgreSQL 18.0)
-- Purpose: Relay cycle orchestration with milestone gates and verification
-- Created: 2025-10-31

-- =============================================================================
-- HELPER FUNCTION: Bulletproof Verification Checker
-- =============================================================================

-- AYA Prime Directives: Bulletproof 4-Phase Verification
CREATE OR REPLACE FUNCTION relay_cycle_fully_verified(p_cycle_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN (
        SELECT COUNT(*) >= 6 AND bool_and(verified)
        FROM aya_verification_chain
        WHERE relay_cycle_id = p_cycle_id
        AND checkpoint IN (
            -- Phase 1: Component Health
            'component_health',
            -- Phase 2: Integration
            'dependency_chain',
            'integration_functional',
            -- Phase 3: Orchestration
            'orchestration_operational',
            -- Phase 4: System Impact
            'user_workflow',
            'failure_impact'
        )
        AND (
            requires_manual_approval = false OR 
            (requires_manual_approval = true AND approval_granted = true)
        )
    );
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- FUNCTION 1: Initiate Relay Cycle
-- =============================================================================

CREATE OR REPLACE FUNCTION initiate_relay_cycle(
    p_source_node VARCHAR(10),
    p_target_node VARCHAR(10),
    p_enhancement_goals JSONB
)
RETURNS UUID AS $$
DECLARE
    v_cycle_id UUID;
    v_prev_cycle_hash VARCHAR(64);
BEGIN
    -- Validate: Only one active cycle at a time
    IF EXISTS (
        SELECT 1 FROM aya_relay_cycles 
        WHERE current_phase != 'COMPLETE' 
        AND completed_at IS NULL
    ) THEN
        RAISE EXCEPTION 'RELAY CYCLE FAILED: Existing cycle in progress';
    END IF;
    
    -- Get hash of previous cycle for chain
    SELECT encode(sha256(relay_cycle_id::text::bytea), 'hex')
    INTO v_prev_cycle_hash
    FROM aya_bulletproof_audit
    WHERE event_type = 'RELAY_CYCLE_INITIATED'
    ORDER BY event_id DESC
    LIMIT 1;
    
    -- Create new cycle
    INSERT INTO aya_relay_cycles (
        alpha_role,
        beta_role,
        current_phase,
        improvement_target,
        enhancement_goals
    ) VALUES (
        CASE WHEN p_source_node = 'ALPHA' THEN 'SOURCE'::node_role 
             ELSE 'TARGET'::node_role END,
        CASE WHEN p_source_node = 'BETA' THEN 'SOURCE'::node_role 
             ELSE 'TARGET'::node_role END,
        'INIT'::relay_phase,
        'AYA_SYSTEM',
        p_enhancement_goals
    ) RETURNING cycle_id INTO v_cycle_id;
    
    -- Log to immutable audit trail
    INSERT INTO aya_bulletproof_audit (
        node, event_type, relay_cycle_id, status, evidence, hash, previous_hash
    ) VALUES (
        'AYA',
        'RELAY_CYCLE_INITIATED',
        v_cycle_id,
        'STARTED',
        jsonb_build_object(
            'source', p_source_node,
            'target', p_target_node,
            'improvement_target', 'AYA_SYSTEM',
            'goals', p_enhancement_goals,
            'cycle_number', (SELECT cycle_number FROM aya_relay_cycles WHERE cycle_id = v_cycle_id)
        ),
        encode(sha256(v_cycle_id::text::bytea), 'hex'),
        v_prev_cycle_hash
    );
    
    RETURN v_cycle_id;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- FUNCTION 2: Transition Relay Phase (with Milestone Gates)
-- =============================================================================

CREATE OR REPLACE FUNCTION transition_relay_phase(
    p_cycle_id UUID,
    p_next_phase relay_phase,
    p_evidence JSONB,
    p_skip_milestone_check BOOLEAN DEFAULT false
)
RETURNS BOOLEAN AS $$
DECLARE
    v_current_phase relay_phase;
    v_valid_transition BOOLEAN;
    v_improvement_target VARCHAR(50);
    v_pending_approvals INTEGER;
BEGIN
    -- Get current phase and target
    SELECT current_phase, improvement_target 
    INTO v_current_phase, v_improvement_target
    FROM aya_relay_cycles
    WHERE cycle_id = p_cycle_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'CYCLE NOT FOUND: Invalid cycle_id';
    END IF;
    
    -- Validate phase sequence
    v_valid_transition := CASE
        WHEN v_current_phase = 'INIT' AND p_next_phase = 'ANALYZE' THEN true
        WHEN v_current_phase = 'ANALYZE' AND p_next_phase = 'ENHANCE' THEN true
        WHEN v_current_phase = 'ENHANCE' AND p_next_phase = 'TRANSFER' THEN true
        WHEN v_current_phase = 'TRANSFER' AND p_next_phase = 'VALIDATE' THEN true
        WHEN v_current_phase = 'VALIDATE' AND p_next_phase = 'COMPLETE' THEN true
        ELSE false
    END;
    
    IF NOT v_valid_transition THEN
        RAISE EXCEPTION 'INVALID PHASE TRANSITION: % -> %', v_current_phase, p_next_phase;
    END IF;
    
    -- Check for pending milestone approvals (unless skipped)
    IF NOT p_skip_milestone_check THEN
        SELECT COUNT(*) INTO v_pending_approvals
        FROM aya_milestone_approvals
        WHERE relay_cycle_id = p_cycle_id
        AND status = 'pending';
        
        IF v_pending_approvals > 0 THEN
            RAISE EXCEPTION 'MILESTONE APPROVAL REQUIRED: % pending approvals for phase transition', v_pending_approvals;
        END IF;
    END IF;
    
    -- Check bulletproof verification for COMPLETE phase
    IF p_next_phase = 'COMPLETE' AND NOT relay_cycle_fully_verified(p_cycle_id) THEN
        RAISE EXCEPTION 'BULLETPROOF VERIFICATION FAILED: Cannot complete cycle without full verification chain';
    END IF;
    
    -- Update relay state
    UPDATE aya_relay_cycles SET
        current_phase = p_next_phase,
        phase_started_at = NOW(),
        phase_transitions = phase_transitions || 
            jsonb_build_object(
                'from', v_current_phase,
                'to', p_next_phase,
                'timestamp', NOW(),
                'evidence', p_evidence
            ),
        bulletproof_verified = CASE 
            WHEN p_next_phase = 'COMPLETE' THEN relay_cycle_fully_verified(p_cycle_id)
            ELSE bulletproof_verified
        END,
        approved_at = CASE 
            WHEN p_next_phase = 'COMPLETE' THEN NOW()
            ELSE approved_at
        END,
        completed_at = CASE 
            WHEN p_next_phase = 'COMPLETE' THEN NOW()
            ELSE completed_at
        END
    WHERE cycle_id = p_cycle_id;
    
    -- Log transition
    INSERT INTO aya_bulletproof_audit (
        node, event_type, relay_cycle_id, status, evidence, hash
    ) VALUES (
        'AYA',
        'PHASE_TRANSITION',
        p_cycle_id,
        p_next_phase::text,
        jsonb_build_object(
            'from_phase', v_current_phase,
            'to_phase', p_next_phase,
            'improvement_target', v_improvement_target,
            'evidence', p_evidence,
            'pending_approvals_bypassed', p_skip_milestone_check
        ),
        encode(sha256((p_cycle_id || p_next_phase::text)::text::bytea), 'hex')
    );
    
    RETURN true;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- FUNCTION 3: Request Milestone Approval
-- =============================================================================

CREATE OR REPLACE FUNCTION request_milestone_approval(
    p_cycle_id UUID,
    p_milestone_type VARCHAR(50),
    p_description TEXT,
    p_impact_analysis JSONB,
    p_requested_by VARCHAR(50)
)
RETURNS UUID AS $$
DECLARE
    v_approval_id UUID;
BEGIN
    INSERT INTO aya_milestone_approvals (
        relay_cycle_id,
        milestone_type,
        milestone_description,
        requested_by,
        context,
        impact_analysis
    ) VALUES (
        p_cycle_id,
        p_milestone_type,
        p_description,
        p_requested_by,
        jsonb_build_object(
            'cycle_phase', (SELECT current_phase FROM aya_relay_cycles WHERE cycle_id = p_cycle_id),
            'timestamp', NOW()
        ),
        p_impact_analysis
    ) RETURNING approval_id INTO v_approval_id;
    
    -- Log to audit
    INSERT INTO aya_bulletproof_audit (
        node, event_type, relay_cycle_id, status, evidence, hash
    ) VALUES (
        'AYA',
        'MILESTONE_APPROVAL_REQUESTED',
        p_cycle_id,
        'PENDING',
        jsonb_build_object(
            'approval_id', v_approval_id,
            'milestone_type', p_milestone_type,
            'requested_by', p_requested_by
        ),
        encode(sha256((v_approval_id || 'MILESTONE')::text::bytea), 'hex')
    );
    
    RETURN v_approval_id;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- FUNCTION 4: Grant Milestone Approval
-- =============================================================================

CREATE OR REPLACE FUNCTION grant_milestone_approval(
    p_approval_id UUID,
    p_approved_by VARCHAR(50),
    p_notes TEXT DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    v_cycle_id UUID;
BEGIN
    -- Update approval status
    UPDATE aya_milestone_approvals
    SET status = 'approved',
        approved_at = NOW(),
        approved_by = p_approved_by,
        approval_notes = p_notes
    WHERE approval_id = p_approval_id
    AND status = 'pending'
    RETURNING relay_cycle_id INTO v_cycle_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'APPROVAL NOT FOUND or already processed';
    END IF;
    
    -- Log to audit
    INSERT INTO aya_bulletproof_audit (
        node, event_type, relay_cycle_id, status, evidence, hash
    ) VALUES (
        'AYA',
        'MILESTONE_APPROVAL_GRANTED',
        v_cycle_id,
        'APPROVED',
        jsonb_build_object(
            'approval_id', p_approval_id,
            'approved_by', p_approved_by,
            'notes', p_notes
        ),
        encode(sha256((p_approval_id || 'APPROVED')::text::bytea), 'hex')
    );
    
    RETURN true;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- FUNCTION 5: Role Swap (End of Cycle)
-- =============================================================================

CREATE OR REPLACE FUNCTION swap_relay_roles(
    p_cycle_id UUID
)
RETURNS UUID AS $$
DECLARE
    v_new_cycle_id UUID;
    v_current_state RECORD;
BEGIN
    -- Get current cycle state
    SELECT * INTO v_current_state
    FROM aya_relay_cycles
    WHERE cycle_id = p_cycle_id
    AND current_phase = 'COMPLETE'
    AND bulletproof_verified = true;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'CANNOT SWAP: Cycle must be in COMPLETE phase and bulletproof verified';
    END IF;
    
    -- Initiate new cycle with swapped roles
    SELECT initiate_relay_cycle(
        CASE WHEN v_current_state.alpha_role = 'SOURCE' THEN 'BETA' ELSE 'ALPHA' END,
        CASE WHEN v_current_state.alpha_role = 'SOURCE' THEN 'ALPHA' ELSE 'BETA' END,
        '{}'::jsonb
    ) INTO v_new_cycle_id;
    
    -- Log role swap
    INSERT INTO aya_bulletproof_audit (
        node, event_type, relay_cycle_id, status, evidence, hash
    ) VALUES (
        'AYA',
        'ROLE_SWAP',
        v_new_cycle_id,
        'SWAPPED',
        jsonb_build_object(
            'previous_cycle', p_cycle_id,
            'new_source', CASE WHEN v_current_state.alpha_role = 'SOURCE' THEN 'BETA' ELSE 'ALPHA' END,
            'new_target', CASE WHEN v_current_state.alpha_role = 'SOURCE' THEN 'ALPHA' ELSE 'BETA' END,
            'previous_cycle_metrics', v_current_state.improvement_metrics
        ),
        encode(sha256((v_new_cycle_id || 'ROLE_SWAP')::text::bytea), 'hex')
    );
    
    RETURN v_new_cycle_id;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- FUNCTION 6: Record Enhancement
-- =============================================================================

CREATE OR REPLACE FUNCTION record_relay_enhancement(
    p_cycle_id UUID,
    p_enhancement_type VARCHAR(50),
    p_component VARCHAR(100),
    p_before_state JSONB,
    p_after_state JSONB,
    p_metrics JSONB,
    p_applied_by VARCHAR(10)
)
RETURNS UUID AS $$
DECLARE
    v_enhancement_id UUID;
    v_improvement_delta JSONB;
BEGIN
    -- Calculate improvement delta
    v_improvement_delta := jsonb_build_object(
        'performance_delta', 
            COALESCE((p_metrics->>'performance_improvement_percent')::float, 0.0),
        'accuracy_delta', 
            COALESCE((p_metrics->>'accuracy_improvement_percent')::float, 0.0),
        'efficiency_delta', 
            COALESCE((p_metrics->>'efficiency_gain_percent')::float, 0.0)
    );
    
    INSERT INTO aya_relay_enhancements (
        relay_cycle_id,
        enhancement_type,
        component_affected,
        before_state,
        after_state,
        improvement_delta,
        performance_improvement_percent,
        accuracy_improvement_percent,
        efficiency_gain_percent,
        applied_by
    ) VALUES (
        p_cycle_id,
        p_enhancement_type,
        p_component,
        p_before_state,
        p_after_state,
        v_improvement_delta,
        (p_metrics->>'performance_improvement_percent')::float,
        (p_metrics->>'accuracy_improvement_percent')::float,
        (p_metrics->>'efficiency_gain_percent')::float,
        p_applied_by
    ) RETURNING enhancement_id INTO v_enhancement_id;
    
    -- Update cycle metrics
    UPDATE aya_relay_cycles
    SET improvement_metrics = COALESCE(improvement_metrics, '{}'::jsonb) || 
        jsonb_build_object(
            p_component, v_improvement_delta
        )
    WHERE cycle_id = p_cycle_id;
    
    -- Log to audit
    INSERT INTO aya_bulletproof_audit (
        node, event_type, relay_cycle_id, status, evidence, hash
    ) VALUES (
        'AYA',
        'ENHANCEMENT_APPLIED',
        p_cycle_id,
        'APPLIED',
        jsonb_build_object(
            'enhancement_id', v_enhancement_id,
            'type', p_enhancement_type,
            'component', p_component,
            'metrics', p_metrics
        ),
        encode(sha256((v_enhancement_id || p_component)::text::bytea), 'hex')
    );
    
    RETURN v_enhancement_id;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- FUNCTION 7: Check Stale Systems
-- =============================================================================

CREATE OR REPLACE FUNCTION check_stale_systems()
RETURNS TABLE(system_name VARCHAR, minutes_stale FLOAT, last_status VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        sh.system_name,
        EXTRACT(EPOCH FROM (NOW() - sh.last_heartbeat))/60 as minutes_stale,
        sh.status as last_status
    FROM aya_system_health sh
    WHERE sh.last_heartbeat < NOW() - INTERVAL '5 minutes'
    ORDER BY minutes_stale DESC;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- FUNCTION 8: Record Verification Checkpoint
-- =============================================================================

CREATE OR REPLACE FUNCTION record_verification_checkpoint(
    p_cycle_id UUID,
    p_node VARCHAR(10),
    p_phase INTEGER,
    p_phase_name VARCHAR(50),
    p_checkpoint VARCHAR(100),
    p_verified BOOLEAN,
    p_evidence JSONB,
    p_verifier VARCHAR(50),
    p_method VARCHAR(100),
    p_requires_approval BOOLEAN DEFAULT false
)
RETURNS UUID AS $$
DECLARE
    v_verification_id UUID;
BEGIN
    INSERT INTO aya_verification_chain (
        relay_cycle_id,
        node,
        phase,
        phase_name,
        checkpoint,
        verified,
        evidence,
        verifier,
        verification_method,
        requires_manual_approval
    ) VALUES (
        p_cycle_id,
        p_node,
        p_phase,
        p_phase_name,
        p_checkpoint,
        p_verified,
        p_evidence,
        p_verifier,
        p_method,
        p_requires_approval
    ) RETURNING verification_id INTO v_verification_id;
    
    -- Log to audit
    INSERT INTO aya_bulletproof_audit (
        node, event_type, relay_cycle_id, status, evidence, hash
    ) VALUES (
        p_node,
        'VERIFICATION_CHECKPOINT',
        p_cycle_id,
        CASE WHEN p_verified THEN 'VERIFIED' ELSE 'FAILED' END,
        jsonb_build_object(
            'verification_id', v_verification_id,
            'phase', p_phase,
            'checkpoint', p_checkpoint,
            'verified', p_verified,
            'requires_approval', p_requires_approval
        ),
        encode(sha256((v_verification_id || p_checkpoint)::text::bytea), 'hex')
    );
    
    RETURN v_verification_id;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- COMPLETION
-- =============================================================================

COMMENT ON FUNCTION initiate_relay_cycle IS 'Start a new ALPHA↔BETA relay cycle with specified enhancement goals';
COMMENT ON FUNCTION transition_relay_phase IS 'Transition to next phase with optional milestone gate bypass';
COMMENT ON FUNCTION request_milestone_approval IS 'Request manual approval for milestone-gated transitions';
COMMENT ON FUNCTION grant_milestone_approval IS 'Grant approval for pending milestone';
COMMENT ON FUNCTION swap_relay_roles IS 'Complete current cycle and start new one with swapped roles';
COMMENT ON FUNCTION record_relay_enhancement IS 'Record an enhancement applied during relay cycle';
COMMENT ON FUNCTION relay_cycle_fully_verified IS 'Check if all required verification checkpoints are complete';
COMMENT ON FUNCTION check_stale_systems IS 'Monitor system health and detect stale heartbeats';
COMMENT ON FUNCTION record_verification_checkpoint IS 'Record a verification checkpoint in the chain';
