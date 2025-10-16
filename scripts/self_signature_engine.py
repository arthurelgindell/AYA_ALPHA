#!/usr/bin/env python3
"""
GLADIATOR Self-Signature Engine
Cryptographically sign all offensive traffic to prevent self-detection

Purpose: Combat/Defense delamination to prevent positive feedback loop
Standard: HMAC-SHA256 signing
"""

import hmac
import hashlib
import uuid
import time
import json

class SelfSignatureEngine:
    """
    Cryptographically sign all offensive traffic from Customer Node
    
    This ensures defensive subsystem can identify and filter out
    self-generated offensive traffic, preventing system from attacking itself.
    """
    
    def __init__(self, node_uuid: str = None, signing_key: str = None):
        """
        Initialize signature engine with node identity
        
        Args:
            node_uuid: Unique identifier for this Customer Node
            signing_key: 256-bit secret key for signing
        """
        self.node_uuid = node_uuid or str(uuid.uuid4())
        self.signing_key = signing_key or self._generate_key()
        
        # Statistics
        self.stats = {
            'packets_signed': 0,
            'signatures_generated': 0,
            'errors': 0
        }
        
        # Verify key integrity on init
        self._verify_key_integrity()
    
    def _generate_key(self) -> str:
        """Generate cryptographically secure signing key"""
        return hashlib.sha256(
            str(uuid.uuid4()).encode() + str(time.time()).encode()
        ).hexdigest()
    
    def _verify_key_integrity(self):
        """Verify signing key hasn't been tampered with"""
        if not self.signing_key or len(self.signing_key) < 32:
            raise ValueError("Invalid signing key (must be ≥32 chars)")
        
        # Calculate checksum
        checksum = hashlib.sha256(self.signing_key.encode()).hexdigest()
        
        # In production: Store checksum in secure enclave
        # For prototype: Just validate length and format
        return True
    
    def sign_packet(self, packet_payload: bytes) -> dict:
        """
        Sign an offensive packet with HMAC-SHA256
        
        Args:
            packet_payload: Raw packet payload (bytes)
        
        Returns:
            dict with signature headers to add to packet
        """
        try:
            # Calculate HMAC-SHA256 signature
            signature = hmac.new(
                key=self.signing_key.encode(),
                msg=packet_payload + self.node_uuid.encode(),
                digestmod=hashlib.sha256
            ).hexdigest()
            
            # Create signature headers
            headers = {
                'X-GLADIATOR-SIG': signature,
                'X-GLADIATOR-UUID': self.node_uuid,
                'X-GLADIATOR-TS': int(time.time())
            }
            
            # Update statistics
            self.stats['packets_signed'] += 1
            self.stats['signatures_generated'] += 1
            
            return headers
            
        except Exception as e:
            self.stats['errors'] += 1
            raise RuntimeError(f"Signature generation failed: {e}")
    
    def verify_signature(self, packet_payload: bytes, claimed_signature: str, claimed_uuid: str) -> bool:
        """
        Verify if a signature is valid for this node
        
        Args:
            packet_payload: Raw packet payload
            claimed_signature: Signature from packet header
            claimed_uuid: UUID from packet header
        
        Returns:
            True if signature valid, False otherwise
        """
        try:
            # Verify UUID matches this node
            if claimed_uuid != self.node_uuid:
                return False  # Different node
            
            # Calculate expected signature
            expected_sig = hmac.new(
                key=self.signing_key.encode(),
                msg=packet_payload + claimed_uuid.encode(),
                digestmod=hashlib.sha256
            ).hexdigest()
            
            # Constant-time comparison (prevents timing attacks)
            return hmac.compare_digest(claimed_signature, expected_sig)
            
        except Exception:
            return False
    
    def get_statistics(self) -> dict:
        """Return signature engine statistics"""
        return {
            'node_uuid': self.node_uuid,
            'packets_signed': self.stats['packets_signed'],
            'signatures_generated': self.stats['signatures_generated'],
            'errors': self.stats['errors'],
            'key_length': len(self.signing_key)
        }


# =============================================================================
# TESTING & VALIDATION
# =============================================================================

def test_signature_engine():
    """Test signature engine implementation"""
    
    print("="*80)
    print("SELF-SIGNATURE ENGINE TEST")
    print("="*80)
    
    # Test 1: Initialization
    print("\n[TEST 1] Engine initialization...")
    engine = SelfSignatureEngine(
        node_uuid="test-node-001",
        signing_key="test_secret_key_12345678901234567890"
    )
    print(f"✅ Node UUID: {engine.node_uuid}")
    print(f"✅ Key length: {len(engine.signing_key)} chars")
    
    # Test 2: Sign packet
    print("\n[TEST 2] Packet signing...")
    payload = b"offensive_traffic_to_attacker_192.168.1.100"
    headers = engine.sign_packet(payload)
    
    print(f"✅ Signature generated: {headers['X-GLADIATOR-SIG'][:32]}...")
    print(f"✅ UUID header: {headers['X-GLADIATOR-UUID']}")
    print(f"✅ Timestamp: {headers['X-GLADIATOR-TS']}")
    assert len(headers['X-GLADIATOR-SIG']) == 64  # SHA256 hex = 64 chars
    
    # Test 3: Verify signature
    print("\n[TEST 3] Signature verification...")
    is_valid = engine.verify_signature(
        payload,
        headers['X-GLADIATOR-SIG'],
        headers['X-GLADIATOR-UUID']
    )
    print(f"✅ Self-signature valid: {is_valid}")
    assert is_valid == True
    
    # Test 4: Reject invalid signature
    print("\n[TEST 4] Invalid signature rejection...")
    is_valid = engine.verify_signature(
        payload,
        "invalid_signature_12345",
        headers['X-GLADIATOR-UUID']
    )
    print(f"✅ Invalid signature rejected: {not is_valid}")
    assert is_valid == False
    
    # Test 5: Reject different node
    print("\n[TEST 5] Different node rejection...")
    is_valid = engine.verify_signature(
        payload,
        headers['X-GLADIATOR-SIG'],
        "different-node-uuid"
    )
    print(f"✅ Different node rejected: {not is_valid}")
    assert is_valid == False
    
    # Test 6: Statistics
    print("\n[TEST 6] Statistics tracking...")
    stats = engine.get_statistics()
    print(f"✅ Packets signed: {stats['packets_signed']}")
    print(f"✅ Errors: {stats['errors']}")
    
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED - SIGNATURE ENGINE VALIDATED")
    print("="*80)
    
    return engine

if __name__ == "__main__":
    test_signature_engine()

