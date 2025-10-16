#!/usr/bin/env python3
"""
GLADIATOR Isolated PID Controller
Gate intensity control that IGNORES self-generated offensive traffic

Purpose: Calculate gate intensity based ONLY on external threats
Critical: Breaks positive feedback loop by filtering self-traffic
"""

import time
from typing import List, Dict
from whitelist_filter import WhitelistFilter

class IsolatedPIDController:
    """
    PID controller that calculates gate intensity based ONLY on
    EXTERNAL threats, not offensive subsystem activity.
    
    This breaks the positive feedback loop where offensive traffic
    would trigger defensive detection → increase gate → more offensive
    → more detection → runaway escalation.
    """
    
    def __init__(self, tier: str, node_uuid: str, signing_key: str):
        """
        Initialize isolated PID controller
        
        Args:
            tier: Customer tier (SHIELD, GUARDIAN, GLADIATOR, REAPER)
            node_uuid: This node's UUID
            signing_key: Signing key for whitelist filter
        """
        self.tier = tier
        self.params = self._get_tier_params(tier)
        
        # PID state
        self.integral = 0.0
        self.last_error = 0.0
        self.last_update = time.time()
        self.current_gate = 0.0
        
        # Whitelist filter (removes self-traffic BEFORE threat scoring)
        self.filter = WhitelistFilter(node_uuid, signing_key)
        
        # Statistics
        self.stats = {
            'updates': 0,
            'gate_increases': 0,
            'gate_decreases': 0,
            'max_gate_reached': 0.0
        }
    
    def _get_tier_params(self, tier: str) -> dict:
        """
        PID parameters tuned per customer tier
        
        Returns:
            dict with Kp, Ki, Kd, max_gate parameters
        """
        params = {
            'SHIELD': {
                'Kp': 0.04,  # Conservative
                'Ki': 0.005,
                'Kd': 0.03,  # Strong damping
                'max_gate': 2.9
            },
            'GUARDIAN': {
                'Kp': 0.06,  # Balanced
                'Ki': 0.01,
                'Kd': 0.02,
                'max_gate': 3.9
            },
            'GLADIATOR': {
                'Kp': 0.10,  # Aggressive
                'Ki': 0.015,
                'Kd': 0.01,
                'max_gate': 4.9
            },
            'REAPER': {
                'Kp': 0.15,  # Extremely aggressive
                'Ki': 0.02,
                'Kd': 0.005,
                'max_gate': 5.0
            }
        }
        return params.get(tier, params['SHIELD'])
    
    def calculate_threat_score(self, network_packets: List[dict]) -> float:
        """
        Calculate threat score ONLY from EXTERNAL threats
        
        CRITICAL: Self-generated traffic is filtered out BEFORE
        this calculation, preventing feedback loop.
        
        Args:
            network_packets: List of network packets
        
        Returns:
            Threat score (0.0-10.0) based on external threats only
        """
        # Filter out self-signed offensive traffic
        external_packets = []
        for packet in network_packets:
            filtered = self.filter.process_packet(packet)
            if filtered is not None:
                external_packets.append(filtered)
        
        # Calculate threat score on EXTERNAL traffic only
        # Simplified scoring: count external packets
        threat_score = len(external_packets) * 0.1
        
        return min(threat_score, 10.0)  # Cap at 10.0
    
    def update_gate(self, network_packets: List[dict], target_threshold: float = 0.5) -> float:
        """
        Update gate intensity based on EXTERNAL threat score
        
        CRITICAL: Offensive operations do NOT affect gate intensity.
        Gate is driven by INCOMING threats, not OUTGOING attacks.
        
        Args:
            network_packets: All network traffic (self + external)
            target_threshold: Target threat level
        
        Returns:
            New gate intensity (0.0 to max_gate)
        """
        now = time.time()
        dt = now - self.last_update
        
        # Calculate threat score (self-traffic filtered automatically)
        measured_threat = self.calculate_threat_score(network_packets)
        
        # Calculate error (external threats only)
        error = measured_threat - target_threshold
        
        # PID terms
        P = self.params['Kp'] * error
        
        self.integral += error * dt
        I = self.params['Ki'] * self.integral
        
        derivative = (error - self.last_error) / dt if dt > 0 else 0
        D = self.params['Kd'] * derivative
        
        # Calculate new gate intensity
        gate_adjustment = P + I + D
        new_gate = self.current_gate + gate_adjustment
        
        # Apply constraints
        new_gate = max(0.0, min(new_gate, self.params['max_gate']))
        
        # Track statistics
        if new_gate > self.current_gate:
            self.stats['gate_increases'] += 1
        elif new_gate < self.current_gate:
            self.stats['gate_decreases'] += 1
        
        self.stats['max_gate_reached'] = max(self.stats['max_gate_reached'], new_gate)
        self.stats['updates'] += 1
        
        # Update state
        self.current_gate = new_gate
        self.last_error = error
        self.last_update = now
        
        return new_gate
    
    def get_statistics(self) -> dict:
        """Return PID controller statistics"""
        return {
            'tier': self.tier,
            'current_gate': self.current_gate,
            'max_gate': self.params['max_gate'],
            'updates': self.stats['updates'],
            'gate_increases': self.stats['gate_increases'],
            'gate_decreases': self.stats['gate_decreases'],
            'max_gate_reached': self.stats['max_gate_reached'],
            'filter_stats': self.filter.get_statistics()
        }


# =============================================================================
# CRITICAL TEST: FEEDBACK LOOP PREVENTION
# =============================================================================

def test_feedback_loop_prevention():
    """
    CRITICAL TEST: Verify system does NOT escalate when generating offensive traffic
    
    This is the MOST IMPORTANT test for GLADIATOR.
    If this fails, system will attack itself in production.
    """
    
    print("="*80)
    print("CRITICAL TEST: FEEDBACK LOOP PREVENTION")
    print("="*80)
    
    node_uuid = "test-customer-node"
    signing_key = "production_signing_key_test"
    
    # Initialize PID controller for SHIELD tier
    print("\n[SETUP] Initialize PID controller (SHIELD tier)...")
    pid = IsolatedPIDController('SHIELD', node_uuid, signing_key)
    print(f"✅ Tier: {pid.tier}, Max gate: {pid.params['max_gate']}")
    
    # Test Scenario: System generates 100 offensive packets (self-signed)
    print("\n[SCENARIO] System generates 100 offensive packets...")
    print("Expected: Gate should NOT increase (self-traffic filtered)")
    
    offensive_packets = []
    for i in range(100):
        payload = f"counter_strike_{i}".encode()
        
        # Sign packet (as offensive subsystem would)
        import hmac, hashlib
        signature = hmac.new(
            key=signing_key.encode(),
            msg=payload + node_uuid.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        offensive_packets.append({
            'payload': payload,
            'X-GLADIATOR-SIG': signature,
            'X-GLADIATOR-UUID': node_uuid,
            'direction': 'outbound'
        })
    
    # Process offensive traffic through PID controller
    initial_gate = pid.current_gate
    print(f"\nInitial gate: {initial_gate:.4f}")
    
    # Update gate 10 times with offensive traffic
    for cycle in range(10):
        gate = pid.update_gate(offensive_packets, target_threshold=0.5)
        time.sleep(0.01)  # Small delay between updates
    
    final_gate = pid.current_gate
    gate_change = abs(final_gate - initial_gate)
    
    print(f"Final gate: {final_gate:.4f}")
    print(f"Gate change: {gate_change:.4f}")
    
    # CRITICAL ASSERTION
    print(f"\n[VALIDATION] Gate change threshold: 0.1")
    if gate_change < 0.1:
        print(f"✅ NO FEEDBACK LOOP: Gate change = {gate_change:.4f} (threshold: 0.1)")
        print("✅ SYSTEM WILL NOT ATTACK ITSELF")
    else:
        print(f"❌ FEEDBACK LOOP DETECTED: Gate changed by {gate_change:.4f}")
        print("❌ CRITICAL FAILURE - SYSTEM WILL ATTACK ITSELF IN PRODUCTION")
        raise AssertionError("Feedback loop detected - DO NOT DEPLOY")
    
    # Check filter statistics
    filter_stats = pid.filter.get_statistics()
    print(f"\n[FILTER STATS]")
    print(f"  Total packets processed: {filter_stats['total_packets']}")
    print(f"  Self-filtered: {filter_stats['self_filtered']}")
    print(f"  Filter rate: {filter_stats['filter_rate']:.1%}")
    
    assert filter_stats['self_filtered'] == 1000, "Should filter 100 packets × 10 cycles"
    
    print("\n" + "="*80)
    print("✅ FEEDBACK LOOP PREVENTION: VALIDATED")
    print("="*80)


def test_mixed_traffic_scenario():
    """
    Test: System under attack AND conducting counter-strikes simultaneously
    Verify: Gate responds to external threats, ignores self-traffic
    """
    
    print("\n" + "="*80)
    print("MIXED TRAFFIC SCENARIO TEST")
    print("="*80)
    
    node_uuid = "test-node-mixed"
    signing_key = "test_key_mixed"
    
    pid = IsolatedPIDController('SHIELD', node_uuid, signing_key)
    
    # Create mixed traffic: 10 external attacks + 50 self-generated counter-strikes
    print("\n[SCENARIO] 10 external attacks + 50 self counter-strikes...")
    
    mixed_traffic = []
    
    # Add external attacks (should affect gate)
    for i in range(10):
        mixed_traffic.append({
            'payload': f"external_attack_{i}".encode(),
            'direction': 'inbound'
            # No GLADIATOR signature
        })
    
    # Add self-generated counter-strikes (should NOT affect gate)
    import hmac, hashlib
    for i in range(50):
        payload = f"counter_strike_{i}".encode()
        sig = hmac.new(
            key=signing_key.encode(),
            msg=payload + node_uuid.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        mixed_traffic.append({
            'payload': payload,
            'X-GLADIATOR-SIG': sig,
            'X-GLADIATOR-UUID': node_uuid,
            'direction': 'outbound'
        })
    
    # Calculate threat score
    threat_score = pid.calculate_threat_score(mixed_traffic)
    
    print(f"\nMixed traffic scenario:")
    print(f"  Total packets: {len(mixed_traffic)}")
    print(f"  External attacks: 10")
    print(f"  Self counter-strikes: 50")
    print(f"  Threat score: {threat_score:.2f}")
    
    # CRITICAL: Threat score should ONLY reflect external attacks (10 packets)
    expected_threat = 10 * 0.1  # 10 external × 0.1 weight
    
    print(f"\n[VALIDATION]")
    print(f"  Expected threat (10 external): {expected_threat:.2f}")
    print(f"  Measured threat: {threat_score:.2f}")
    
    if abs(threat_score - expected_threat) < 0.01:
        print(f"✅ CORRECT: Self-traffic ignored, only external counted")
    else:
        print(f"❌ INCORRECT: Self-traffic affected threat score")
        raise AssertionError("Mixed traffic test failed")
    
    # Update gate
    new_gate = pid.update_gate(mixed_traffic, target_threshold=0.5)
    print(f"\n  Gate intensity: {new_gate:.4f}")
    print(f"  Gate should increase (responding to 10 external attacks)")
    
    # Gate should increase because of external threats
    assert new_gate > 0, "Gate should respond to external threats"
    
    print("\n" + "="*80)
    print("✅ MIXED TRAFFIC SCENARIO: VALIDATED")
    print("="*80)


if __name__ == "__main__":
    test_feedback_loop_prevention()
    test_mixed_traffic_scenario()
    
    print("\n" + "="*80)
    print("✅ SELF-ATTACK PREVENTION COMPLETE")
    print("✅ SYSTEM WILL NOT ATTACK ITSELF")
    print("="*80)

