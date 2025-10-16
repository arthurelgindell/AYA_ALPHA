#!/usr/bin/env python3
"""
GLADIATOR Whitelist Filter
Filter self-generated offensive traffic BEFORE threat detection

Purpose: Prevent defensive subsystem from analyzing offensive subsystem's traffic
Critical: Prevents positive feedback loop (system attacking itself)
"""

import hmac
import hashlib
import json
from typing import Optional, Dict

class WhitelistFilter:
    """
    Filter out self-signed traffic before threat analysis
    
    This prevents the defensive subsystem from detecting the offensive
    subsystem's traffic as threats, which would cause PID controller
    to escalate and create positive feedback loop.
    """
    
    def __init__(self, node_uuid: str, signing_key: str):
        """
        Initialize whitelist filter with node identity
        
        Args:
            node_uuid: This Customer Node's UUID
            signing_key: Signing key (must match offensive subsystem)
        """
        self.node_uuid = node_uuid
        self.signing_key = signing_key
        
        # Statistics
        self.stats = {
            'total_packets': 0,
            'self_filtered': 0,
            'external_analyzed': 0,
            'invalid_signatures': 0
        }
    
    def is_self_generated(self, packet: dict) -> bool:
        """
        Check if packet originated from this node's offensive subsystem
        
        Args:
            packet: dict with 'payload' and optional GLADIATOR headers
        
        Returns:
            True if self-generated (FILTER OUT)
            False if external (ANALYZE)
        """
        # Check for GLADIATOR signature header
        if 'X-GLADIATOR-SIG' not in packet:
            return False  # External traffic (no signature)
        
        # Extract claimed signature and UUID
        claimed_sig = packet['X-GLADIATOR-SIG']
        claimed_uuid = packet['X-GLADIATOR-UUID']
        
        # Verify UUID matches this node
        if claimed_uuid != self.node_uuid:
            # Another GLADIATOR node's traffic (still external)
            return False
        
        # Verify signature authenticity
        expected_sig = hmac.new(
            key=self.signing_key.encode(),
            msg=packet['payload'] + claimed_uuid.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        if claimed_sig == expected_sig:
            # Valid self-signature, FILTER OUT
            self.stats['self_filtered'] += 1
            return True
        else:
            # Signature mismatch (possible attack spoofing our headers)
            self.stats['invalid_signatures'] += 1
            return False  # ANALYZE (treat as external threat)
    
    def process_packet(self, packet: dict) -> Optional[dict]:
        """
        Filter self-generated traffic, pass external traffic to threat detector
        
        Args:
            packet: Network packet dict
        
        Returns:
            None if self-generated (filtered)
            packet dict if external (analyze)
        """
        self.stats['total_packets'] += 1
        
        if self.is_self_generated(packet):
            # LOG but do NOT analyze
            return None  # Filtered - skip threat analysis
        
        # External traffic, proceed with threat analysis
        self.stats['external_analyzed'] += 1
        return packet
    
    def get_statistics(self) -> dict:
        """Return filter statistics for monitoring"""
        total = self.stats['total_packets']
        
        return {
            'total_packets': total,
            'self_filtered': self.stats['self_filtered'],
            'external_analyzed': self.stats['external_analyzed'],
            'invalid_signatures': self.stats['invalid_signatures'],
            'filter_rate': self.stats['self_filtered'] / total if total > 0 else 0.0,
            'external_rate': self.stats['external_analyzed'] / total if total > 0 else 0.0
        }


# =============================================================================
# TESTING & VALIDATION
# =============================================================================

def test_whitelist_filter():
    """Test whitelist filter implementation"""
    
    print("="*80)
    print("WHITELIST FILTER TEST")
    print("="*80)
    
    node_uuid = "test-node-123"
    signing_key = "test_secret_key_for_filtering"
    
    # Initialize filter
    print("\n[TEST 1] Filter initialization...")
    filter_engine = WhitelistFilter(node_uuid, signing_key)
    print(f"✅ Node UUID: {filter_engine.node_uuid}")
    
    # Test 2: Self-generated traffic (should be filtered)
    print("\n[TEST 2] Self-generated traffic (should FILTER)...")
    payload = b"offensive_counter_strike_to_attacker"
    
    # Create valid self-signature
    signature = hmac.new(
        key=signing_key.encode(),
        msg=payload + node_uuid.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    self_packet = {
        'payload': payload,
        'X-GLADIATOR-SIG': signature,
        'X-GLADIATOR-UUID': node_uuid,
        'direction': 'outbound'
    }
    
    result = filter_engine.process_packet(self_packet)
    print(f"✅ Self-traffic filtered: {result is None}")
    assert result is None, "FAILED: Self-traffic should be filtered"
    
    # Test 3: External traffic (should be analyzed)
    print("\n[TEST 3] External traffic (should ANALYZE)...")
    external_packet = {
        'payload': b'malicious_external_attack',
        'direction': 'inbound'
        # No GLADIATOR signature
    }
    
    result = filter_engine.process_packet(external_packet)
    print(f"✅ External traffic passed: {result is not None}")
    assert result is not None, "FAILED: External traffic should pass through"
    
    # Test 4: Invalid signature (should be analyzed as threat)
    print("\n[TEST 4] Invalid signature (should ANALYZE as threat)...")
    invalid_packet = {
        'payload': b'suspicious_traffic_with_fake_signature',
        'X-GLADIATOR-SIG': 'fake_signature_attempt',
        'X-GLADIATOR-UUID': node_uuid,
        'direction': 'inbound'
    }
    
    result = filter_engine.process_packet(invalid_packet)
    print(f"✅ Invalid signature detected and passed for analysis: {result is not None}")
    assert result is not None, "FAILED: Invalid signature should be analyzed"
    
    # Test 5: Different node's traffic (should be analyzed)
    print("\n[TEST 5] Different GLADIATOR node (should ANALYZE)...")
    other_node_uuid = "different-node-456"
    other_signature = hmac.new(
        key=signing_key.encode(),
        msg=payload + other_node_uuid.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    other_packet = {
        'payload': payload,
        'X-GLADIATOR-SIG': other_signature,
        'X-GLADIATOR-UUID': other_node_uuid
    }
    
    result = filter_engine.process_packet(other_packet)
    print(f"✅ Other node traffic passed for analysis: {result is not None}")
    assert result is not None, "FAILED: Other node traffic should be analyzed"
    
    # Test 6: Statistics
    print("\n[TEST 6] Filter statistics...")
    stats = filter_engine.get_statistics()
    print(f"✅ Total packets: {stats['total_packets']}")
    print(f"✅ Self-filtered: {stats['self_filtered']} ({stats['filter_rate']:.1%})")
    print(f"✅ External analyzed: {stats['external_analyzed']} ({stats['external_rate']:.1%})")
    print(f"✅ Invalid signatures: {stats['invalid_signatures']}")
    
    assert stats['total_packets'] == 4
    assert stats['self_filtered'] == 1
    assert stats['external_analyzed'] == 3
    assert stats['invalid_signatures'] == 1
    
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED - WHITELIST FILTER VALIDATED")
    print("="*80)
    
    return filter_engine

if __name__ == "__main__":
    test_whitelist_filter()

