-- =============================================================================
-- GLADIATOR DATABASE - INITIAL DATA POPULATION
-- =============================================================================
-- Purpose: Populate GLADIATOR tables with current project state
-- Run after: gladiator_schema.sql
-- Database: aya_rag
-- Date: 2025-10-10
-- =============================================================================

BEGIN;

-- =============================================================================
-- POPULATE: gladiator_models (Foundation + MLX models)
-- =============================================================================

-- Foundation Model (ALPHA - already validated)
INSERT INTO gladiator_models (
    model_name, model_type, model_role, source, huggingface_repo,
    model_size_gb, quantization, deployed_on, deployment_path, api_endpoint,
    ram_required_gb, inference_speed_tok_per_sec, context_window,
    training_phase, instances_count, status, validated_at, validation_notes,
    metadata
) VALUES (
    'foundation-sec-8b-instruct-int8',
    'foundation',
    'blue_team_base',
    'lm_studio',
    'Unknown - loaded in LM Studio',
    8.0,
    'int8',
    'ALPHA',
    'LM Studio Models',
    'http://localhost:1234/v1',
    12,
    67.0,  -- Average from validation tests
    NULL,
    'pre_flight',
    1,
    'validated',
    '2025-10-10 19:15:00',
    'Exhaustive validation complete. 7/7 tests passed. Suitable for fine-tuning.',
    '{"validation_report": "/Users/arthurdell/GLADIATOR/FOUNDATION_MODEL_VALIDATION_2025-10-10.md"}'
);

-- Red Team Models (BETA - to be downloaded)
INSERT INTO gladiator_models (
    model_name, model_type, model_role, source, huggingface_repo,
    model_size_gb, quantization, deployed_on, deployment_path,
    ram_required_gb, context_window, training_phase, instances_count,
    status, metadata
) VALUES 
(
    'Llama-3.3-70B-Instruct-4bit',
    'red_team',
    'strategic_attack_planning',
    'mlx_community',
    'mlx-community/Llama-3.3-70B-Instruct-4bit',
    40.0,
    '4bit',
    'BETA',
    '/Volumes/DATA/GLADIATOR/models/llama-70b-red-team',
    42,
    NULL,
    'pre_flight',
    1,
    'planned',
    '{"download_list": "/Users/arthurdell/GLADIATOR/MLX_MODELS_BETA.txt"}'
),
(
    'TinyLlama-1.1B-Chat-v1.0-4bit',
    'red_team',
    'attack_specialists',
    'mlx_community',
    'mlx-community/TinyLlama-1.1B-Chat-v1.0-4bit',
    0.7,
    '4bit',
    'BETA',
    '/Volumes/DATA/GLADIATOR/models/tinyllama-1.1b-specialist',
    1,
    NULL,
    'pre_flight',
    15,  -- 15 concurrent instances
    'planned',
    '{"specializations": ["network", "web", "system", "social", "persistence"]}'
),
(
    'CodeLlama-7b-Python-mlx',
    'red_team',
    'exploit_code_synthesis',
    'mlx_community',
    'mlx-community/CodeLlama-7b-Python-mlx',
    4.0,
    'default',
    'BETA',
    '/Volumes/DATA/GLADIATOR/models/codellama-7b-exploit-synthesis',
    4.5,
    NULL,
    'pre_flight',
    10,  -- 10 concurrent instances
    'planned',
    '{"languages": ["python", "shellcode", "powershell", "bash"]}'
);

-- =============================================================================
-- POPULATE: gladiator_validation_tests (Foundation model validation)
-- =============================================================================

INSERT INTO gladiator_validation_tests (
    test_name, test_type, validation_gate, phase, tested_on,
    model_id, test_dataset_size, test_parameters,
    test_result, accuracy_percentage, pass_threshold,
    inference_time_ms, throughput_samples_per_sec,
    self_attack_prevented, feedback_loop_detected,
    test_output, go_no_go_decision, decision_by, decision_notes,
    executed_at, completed_at
) VALUES 
(
    'Foundation Model - Threat Detection',
    'pre_flight',
    'gate_0',
    'pre_flight',
    'ALPHA',
    (SELECT id FROM gladiator_models WHERE model_name = 'foundation-sec-8b-instruct-int8'),
    1,
    '{"test": "Multiple failed SSH login attempts", "expected": "brute force detection"}',
    'PASS',
    100.0,
    90.0,
    3080,
    NULL,
    NULL,
    NULL,
    'Correctly identified as brute force attack. Inference: 64.7 tok/s, Duration: 3.08s',
    'GO',
    'cursor',
    'Test 1/7 passed. Accurate threat analysis.',
    '2025-10-10 19:05:00',
    '2025-10-10 19:05:03'
),
(
    'Foundation Model - Attack Classification',
    'pre_flight',
    'gate_0',
    'pre_flight',
    'ALPHA',
    (SELECT id FROM gladiator_models WHERE model_name = 'foundation-sec-8b-instruct-int8'),
    1,
    '{"test": "SQL injection payload", "expected": "SQL Injection classification"}',
    'PASS',
    100.0,
    90.0,
    2950,
    NULL,
    NULL,
    NULL,
    'Correctly classified as SQL Injection. Inference: 67.5 tok/s, Duration: 2.95s',
    'GO',
    'cursor',
    'Test 2/7 passed. Accurate classification.',
    '2025-10-10 19:05:03',
    '2025-10-10 19:05:06'
),
(
    'Foundation Model - 0-Day Behavioral Analysis',
    'pre_flight',
    'gate_0',
    'pre_flight',
    'ALPHA',
    (SELECT id FROM gladiator_models WHERE model_name = 'foundation-sec-8b-instruct-int8'),
    1,
    '{"test": "Novel attack pattern", "expected": "Malware identification without signatures"}',
    'PASS',
    100.0,
    90.0,
    2940,
    NULL,
    NULL,
    NULL,
    'Correctly identified as potential malware. Inference: 67.6 tok/s, Duration: 2.94s',
    'GO',
    'cursor',
    'Test 3/7 passed. No signature match required.',
    '2025-10-10 19:05:06',
    '2025-10-10 19:05:09'
),
(
    'Foundation Model - Long Context Handling',
    'pre_flight',
    'gate_0',
    'pre_flight',
    'ALPHA',
    (SELECT id FROM gladiator_models WHERE model_name = 'foundation-sec-8b-instruct-int8'),
    10,
    '{"test": "10 attack patterns + MITRE mapping", "tokens_generated": 499}',
    'PASS',
    NULL,
    NULL,
    7360,
    489,  -- samples per hour
    NULL,
    NULL,
    'Generated 499 tokens. Inference: 67.8 tok/s, Duration: 7.36s. Training throughput: ~489 samples/hour',
    'GO',
    'cursor',
    'Test 4/7 passed. Suitable for training batches.',
    '2025-10-10 19:05:09',
    '2025-10-10 19:05:17'
),
(
    'Foundation Model - Concurrent Request Handling',
    'pre_flight',
    'gate_0',
    'pre_flight',
    'ALPHA',
    (SELECT id FROM gladiator_models WHERE model_name = 'foundation-sec-8b-instruct-int8'),
    5,
    '{"concurrent_requests": 5, "expected": "Stable under load"}',
    'PASS',
    100.0,
    100.0,
    7630,
    0.7,
    NULL,
    NULL,
    '5/5 requests succeeded. Total time: 7.63s, Effective throughput: 0.7 req/s',
    'GO',
    'cursor',
    'Test 5/7 passed. Model stable under training-like load.',
    '2025-10-10 19:05:17',
    '2025-10-10 19:05:25'
),
(
    'Foundation Model - Fine-Tuning Compatibility',
    'pre_flight',
    'gate_0',
    'pre_flight',
    'ALPHA',
    (SELECT id FROM gladiator_models WHERE model_name = 'foundation-sec-8b-instruct-int8'),
    1,
    '{"test": "Few-shot learning", "expected": "Follow training pattern"}',
    'PASS',
    100.0,
    90.0,
    NULL,
    NULL,
    NULL,
    NULL,
    'Model correctly followed pattern: Threat Level: HIGH, Type: Malware Execution. Can learn from training data.',
    'GO',
    'cursor',
    'Test 6/7 passed. Suitable for fine-tuning on attack datasets.',
    '2025-10-10 19:05:25',
    '2025-10-10 19:05:30'
),
(
    'Foundation Model - Exhaustive Validation Summary',
    'pre_flight',
    'gate_0',
    'pre_flight',
    'ALPHA',
    (SELECT id FROM gladiator_models WHERE model_name = 'foundation-sec-8b-instruct-int8'),
    18,  -- Total test cases
    '{"total_tests": 7, "passed": 7, "failed": 0}',
    'PASS',
    100.0,
    90.0,
    NULL,
    NULL,
    NULL,
    NULL,
    'All 7 validation tests passed. 10/10 validation score. Ready for Phase 0.',
    'GO',
    'Arthur',
    'Foundation model exhaustively validated and approved for Phase 0 training.',
    '2025-10-10 19:15:00',
    '2025-10-10 19:15:00'
);

-- =============================================================================
-- POPULATE: gladiator_phase_milestones (Phase 0 timeline)
-- =============================================================================

INSERT INTO gladiator_phase_milestones (
    phase, week_number, milestone_name, milestone_type,
    planned_start_date, planned_end_date, estimated_duration_days,
    status, validation_required, notes, blocking
) VALUES 
-- Pre-Flight (THIS WEEK)
(
    'pre_flight',
    -15,
    'Pre-Flight Validation - Network & Model Testing',
    'gate',
    '2025-10-10',
    '2025-10-14',
    5,
    'in_progress',
    TRUE,
    'Foundation model validated. Pending: Network throughput, self-attack prevention, Go/No-Go decision',
    TRUE
),

-- Week -14
(
    'phase_0',
    -14,
    'Block 0: Environment Setup - Hardware & Network',
    'block_completion',
    '2025-10-20',
    '2025-10-26',
    7,
    'planned',
    FALSE,
    'Physical setup, network validation, storage validation',
    FALSE
),

-- Week -13
(
    'phase_0',
    -13,
    'Gate 1: Environment Ready',
    'gate',
    '2025-10-27',
    '2025-11-02',
    7,
    'planned',
    TRUE,
    'ALPHA, BETA, AIR configured. Network isolated (air-gapped). Foundation model validated. Monitoring operational.',
    TRUE
),

-- Weeks -12 to -7
(
    'phase_0',
    -12,
    'Block 1: Red Team Attack Generation - 10M Patterns',
    'block_completion',
    '2025-11-03',
    '2025-12-14',
    42,
    'planned',
    FALSE,
    'Generate 10M attack patterns + 100M variants. MITRE ATT&CK coverage.',
    FALSE
),
(
    'phase_0',
    -7,
    'Gate 2: Red Team Dataset Complete',
    'gate',
    '2025-12-15',
    '2025-12-21',
    7,
    'planned',
    TRUE,
    '10M+ attack patterns. 100M+ variants. Full MITRE coverage. 6TB on BETA.',
    TRUE
),

-- Week -6
(
    'phase_0',
    -6,
    'Gate 3: Foundation Model Reality Check (CRITICAL)',
    'gate',
    '2025-12-22',
    '2025-12-22',
    1,
    'planned',
    TRUE,
    'MANDATORY: Quick fine-tuning test (1K samples, 100 steps). Target: ≥90% accuracy. If fail, STOP Phase 0.',
    TRUE
),

-- Weeks -6 to -4
(
    'phase_0',
    -6,
    'Block 2: Blue Team Fine-Tuning - Full Training',
    'block_completion',
    '2025-12-22',
    '2026-01-11',
    21,
    'planned',
    FALSE,
    'Fine-tune Foundation-Sec-8B on 8M attack patterns. Target: >98% test accuracy.',
    FALSE
),
(
    'phase_0',
    -4,
    'Gate 4: GLADIATOR-SEC-8B-EXPERT Complete',
    'gate',
    '2026-01-12',
    '2026-01-18',
    7,
    'planned',
    TRUE,
    'Training converged. Validation accuracy >95%. Test accuracy >98% on 1M held-out samples.',
    TRUE
),

-- Weeks -3 to -1
(
    'phase_0',
    -3,
    'Block 3: Knowledge Distillation - 4× 1.5B Models',
    'block_completion',
    '2026-01-19',
    '2026-02-08',
    21,
    'planned',
    FALSE,
    'Distill 4× GLADIATOR-1.5B models from 8B teacher. Quantize to 4-bit.',
    FALSE
),
(
    'phase_0',
    -1,
    'Gate 5: Distillation Complete',
    'gate',
    '2026-02-09',
    '2026-02-15',
    7,
    'planned',
    TRUE,
    'All 4× GLADIATOR-1.5B models trained. Quantized to 4-bit. >94% accuracy each. Inference <10ms.',
    TRUE
),

-- Week 0
(
    'phase_0',
    0,
    'Gate 6: Production Readiness (FINAL)',
    'gate',
    '2026-02-16',
    '2026-02-20',
    5,
    'planned',
    TRUE,
    'Gauntlet test: >94% on 100K held-out attacks. Self-attack prevention validated. Models packaged. DEPLOY ONLY IF ALL PASS.',
    TRUE
);

-- =============================================================================
-- UPDATE: gladiator_project_state with current status
-- =============================================================================

UPDATE gladiator_project_state SET
    current_phase = 'pre_flight',
    current_week = -15,
    current_milestone_id = (SELECT id FROM gladiator_phase_milestones WHERE week_number = -15 LIMIT 1),
    phase_0_progress_percentage = 5,  -- Pre-flight in progress
    foundation_model_validated = TRUE,
    alpha_status = 'active',
    beta_status = 'active',
    air_status = 'not_deployed',
    air_gap_enforced = FALSE,
    last_go_no_go_decision = 'GO',
    last_go_no_go_gate = 'gate_0_foundation_model',
    last_go_no_go_date = '2025-10-10',
    critical_blockers = 0,
    major_risks = 2,  -- Network not upgraded, AIR not deployed
    minor_issues = 1,  -- Red Team models not downloaded yet
    metadata = jsonb_build_object(
        'foundation_validation_report', '/Users/arthurdell/GLADIATOR/FOUNDATION_MODEL_VALIDATION_2025-10-10.md',
        'mlx_models_list', '/Users/arthurdell/GLADIATOR/MLX_MODELS_BETA.txt',
        'next_actions', jsonb_build_array(
            'Arthur downloads MLX models on BETA',
            'Test network throughput (iperf3)',
            'Implement self-attack prevention prototype',
            'Go/No-Go decision for Phase 0 start'
        )
    )
WHERE is_current = TRUE;

-- =============================================================================
-- POPULATE: gladiator_documentation (import existing docs)
-- =============================================================================

-- Update documentation records with actual content (placeholder - will be updated via script)
UPDATE gladiator_documentation 
SET 
    content = 'See file: /Users/arthurdell/Documents/Dropbox/GLADIATOR/GLADIATOR_MASTER_ARCHITECTURE_v2.2.md',
    word_count = 2340,  -- Approximate from validation report
    updated_at = NOW()
WHERE doc_name = 'GLADIATOR_MASTER_ARCHITECTURE_v2.2.md';

UPDATE gladiator_documentation 
SET 
    content = 'See file: /Users/arthurdell/Documents/Dropbox/GLADIATOR/GLADIATOR_INFRASTRUCTURE_TEST_PLAN_v2.2.md',
    word_count = 2220,  -- Approximate
    updated_at = NOW()
WHERE doc_name = 'GLADIATOR_INFRASTRUCTURE_TEST_PLAN_v2.2.md';

-- Add newly created documentation
INSERT INTO gladiator_documentation (
    doc_type, doc_name, doc_version, url, title, description,
    content, word_count, status
) VALUES 
(
    'validation',
    'FOUNDATION_MODEL_VALIDATION_2025-10-10.md',
    'v1.0',
    '/Users/arthurdell/GLADIATOR/FOUNDATION_MODEL_VALIDATION_2025-10-10.md',
    'Foundation Model Exhaustive Validation Report',
    'Foundation-Sec-8B model validation - all 7 tests passed, approved for Phase 0',
    'See file for full content',
    1200,
    'approved'
),
(
    'reference',
    'MLX_MODELS_DOWNLOAD_LIST.md',
    'v1.0',
    '/Users/arthurdell/GLADIATOR/MLX_MODELS_DOWNLOAD_LIST.md',
    'GLADIATOR MLX Models Download List',
    'Complete list of MLX-optimized models for BETA Red Team',
    'See file for full content',
    800,
    'approved'
),
(
    'reference',
    'gladiator_schema.sql',
    'v1.0',
    '/Users/arthurdell/GLADIATOR/gladiator_schema.sql',
    'GLADIATOR Database Schema',
    'PostgreSQL 18 schema for GLADIATOR project tracking',
    'See file for full content',
    1500,
    'approved'
);

COMMIT;

-- =============================================================================
-- VERIFICATION QUERIES
-- =============================================================================

-- Check current status
SELECT 
    'Current Phase: ' || current_phase ||
    ', Week: ' || current_week ||
    ', Progress: ' || phase_0_progress_percentage || '%' ||
    ', Gates Passed: ' || gates_passed || '/' || gates_total ||
    ', Foundation Validated: ' || foundation_model_validated::text
    as project_status
FROM gladiator_project_state WHERE is_current = TRUE;

-- Check models
SELECT 
    model_name,
    model_type,
    deployed_on,
    status,
    instances_count
FROM gladiator_models
ORDER BY model_type, model_name;

-- Check validation tests
SELECT 
    test_name,
    test_result,
    accuracy_percentage,
    go_no_go_decision
FROM gladiator_validation_tests
ORDER BY executed_at;

-- Check milestones
SELECT 
    phase,
    week_number,
    milestone_name,
    status,
    validation_required
FROM gladiator_phase_milestones
ORDER BY week_number;

-- =============================================================================
-- END OF POPULATION SCRIPT
-- =============================================================================

