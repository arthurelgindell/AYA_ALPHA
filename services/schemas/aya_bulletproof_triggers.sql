-- AYA Bulletproof LISTEN/NOTIFY Triggers
-- Database: aya_rag (PostgreSQL 18.0)
-- Purpose: Real-time event notifications for relay coordination
-- Created: 2025-10-31

-- =============================================================================
-- TRIGGER 1: Notify on Relay Phase Transitions
-- =============================================================================

-- Notify on relay phase transitions
CREATE OR REPLACE FUNCTION notify_relay_phase_transition()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.current_phase IS DISTINCT FROM NEW.current_phase THEN
        PERFORM pg_notify(
            'aya_relay_phase',
            json_build_object(
                'cycle_id', NEW.cycle_id,
                'from_phase', OLD.current_phase,
                'to_phase', NEW.current_phase,
                'alpha_role', NEW.alpha_role,
                'beta_role', NEW.beta_role,
                'improvement_target', NEW.improvement_target,
                'requires_approval', EXISTS(
                    SELECT 1 FROM aya_milestone_approvals 
                    WHERE relay_cycle_id = NEW.cycle_id 
                    AND status = 'pending'
                )
            )::text
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER relay_phase_notification
AFTER UPDATE ON aya_relay_cycles
FOR EACH ROW
EXECUTE FUNCTION notify_relay_phase_transition();

-- =============================================================================
-- TRIGGER 2: Notify on Verification Checkpoint
-- =============================================================================

-- Notify on verification checkpoint
CREATE OR REPLACE FUNCTION notify_verification_checkpoint()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify(
        'aya_verification',
        json_build_object(
            'verification_id', NEW.verification_id,
            'relay_cycle_id', NEW.relay_cycle_id,
            'phase', NEW.phase,
            'checkpoint', NEW.checkpoint,
            'verified', NEW.verified,
            'node', NEW.node,
            'requires_manual_approval', NEW.requires_manual_approval
        )::text
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER verification_notification
AFTER INSERT ON aya_verification_chain
FOR EACH ROW
EXECUTE FUNCTION notify_verification_checkpoint();

-- =============================================================================
-- TRIGGER 3: Notify on Milestone Approval Requests
-- =============================================================================

-- Notify on milestone approval requests
CREATE OR REPLACE FUNCTION notify_milestone_approval()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'pending' THEN
        PERFORM pg_notify(
            'aya_milestone_approval',
            json_build_object(
                'approval_id', NEW.approval_id,
                'relay_cycle_id', NEW.relay_cycle_id,
                'milestone_type', NEW.milestone_type,
                'description', NEW.milestone_description,
                'impact_analysis', NEW.impact_analysis
            )::text
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER milestone_approval_notification
AFTER INSERT OR UPDATE ON aya_milestone_approvals
FOR EACH ROW
EXECUTE FUNCTION notify_milestone_approval();

-- =============================================================================
-- TRIGGER 4: Notify on GAMMA Workload Authorization
-- =============================================================================

-- Notify on GAMMA authorization
CREATE OR REPLACE FUNCTION notify_gamma_authorized()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.bulletproof_authorized = false AND NEW.bulletproof_authorized = true THEN
        PERFORM pg_notify(
            'gamma_workload_authorized',
            json_build_object(
                'workload_id', NEW.workload_id,
                'workload_type', NEW.workload_type,
                'authorized_by', NEW.authorized_by
            )::text
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER gamma_auth_notification
AFTER UPDATE ON aya_gamma_workloads
FOR EACH ROW
EXECUTE FUNCTION notify_gamma_authorized();

-- =============================================================================
-- TRIGGER 5: Notify on System Health Changes
-- =============================================================================

-- Notify on system health status changes
CREATE OR REPLACE FUNCTION notify_system_health_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status OR 
       (NEW.last_heartbeat < NOW() - INTERVAL '5 minutes' AND OLD.last_heartbeat >= NOW() - INTERVAL '5 minutes') THEN
        PERFORM pg_notify(
            'aya_system_health',
            json_build_object(
                'system_name', NEW.system_name,
                'old_status', OLD.status,
                'new_status', NEW.status,
                'last_heartbeat', NEW.last_heartbeat,
                'is_stale', NEW.last_heartbeat < NOW() - INTERVAL '5 minutes'
            )::text
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER system_health_notification
AFTER UPDATE ON aya_system_health
FOR EACH ROW
EXECUTE FUNCTION notify_system_health_change();

-- =============================================================================
-- TRIGGER 6: Notify on Enhancement Applied
-- =============================================================================

-- Notify when enhancements are applied
CREATE OR REPLACE FUNCTION notify_enhancement_applied()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify(
        'aya_enhancement_applied',
        json_build_object(
            'enhancement_id', NEW.enhancement_id,
            'relay_cycle_id', NEW.relay_cycle_id,
            'enhancement_type', NEW.enhancement_type,
            'component_affected', NEW.component_affected,
            'performance_improvement', NEW.performance_improvement_percent,
            'accuracy_improvement', NEW.accuracy_improvement_percent,
            'efficiency_gain', NEW.efficiency_gain_percent,
            'applied_by', NEW.applied_by
        )::text
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER enhancement_applied_notification
AFTER INSERT ON aya_relay_enhancements
FOR EACH ROW
EXECUTE FUNCTION notify_enhancement_applied();

-- =============================================================================
-- TRIGGER 7: Notify on Bulletproof Audit Events
-- =============================================================================

-- Notify on critical audit events
CREATE OR REPLACE FUNCTION notify_audit_event()
RETURNS TRIGGER AS $$
BEGIN
    -- Only notify for certain critical event types
    IF NEW.event_type IN ('RELAY_CYCLE_INITIATED', 'PHASE_TRANSITION', 'MILESTONE_APPROVAL_GRANTED', 
                          'ENHANCEMENT_APPLIED', 'ROLE_SWAP') THEN
        PERFORM pg_notify(
            'aya_audit_event',
            json_build_object(
                'event_id', NEW.event_id,
                'timestamp', NEW.timestamp,
                'node', NEW.node,
                'event_type', NEW.event_type,
                'relay_cycle_id', NEW.relay_cycle_id,
                'status', NEW.status
            )::text
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_event_notification
AFTER INSERT ON aya_bulletproof_audit
FOR EACH ROW
EXECUTE FUNCTION notify_audit_event();

-- =============================================================================
-- TRIGGER 8: Notify on System Operation Status Changes
-- =============================================================================

-- Notify on system operation status changes
CREATE OR REPLACE FUNCTION notify_operation_status()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        PERFORM pg_notify(
            'aya_operation_status',
            json_build_object(
                'operation_id', NEW.operation_id,
                'relay_cycle_id', NEW.relay_cycle_id,
                'operation_type', NEW.operation_type,
                'target_system', NEW.target_system,
                'old_status', OLD.status,
                'new_status', NEW.status,
                'error', NEW.error
            )::text
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER operation_status_notification
AFTER UPDATE ON aya_system_operations
FOR EACH ROW
EXECUTE FUNCTION notify_operation_status();

-- =============================================================================
-- COMPLETION
-- =============================================================================

COMMENT ON FUNCTION notify_relay_phase_transition IS 'Broadcasts relay phase changes via pg_notify';
COMMENT ON FUNCTION notify_verification_checkpoint IS 'Broadcasts verification events via pg_notify';
COMMENT ON FUNCTION notify_milestone_approval IS 'Broadcasts milestone approval requests via pg_notify';
COMMENT ON FUNCTION notify_gamma_authorized IS 'Broadcasts GAMMA workload authorizations via pg_notify';
COMMENT ON FUNCTION notify_system_health_change IS 'Broadcasts system health status changes via pg_notify';
COMMENT ON FUNCTION notify_enhancement_applied IS 'Broadcasts when enhancements are applied via pg_notify';
COMMENT ON FUNCTION notify_audit_event IS 'Broadcasts critical audit trail events via pg_notify';
COMMENT ON FUNCTION notify_operation_status IS 'Broadcasts system operation status changes via pg_notify';
