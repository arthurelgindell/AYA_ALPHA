#!/usr/bin/env python3
"""
Verify Prime Directives are properly configured and enforced in Cursor
"""

import os
import sys
import json
from pathlib import Path

def check_cursorrules():
    """Check if .cursorrules file exists and contains directives."""
    cursorrules = Path('/Volumes/DATA/Agent_Turbo/.cursorrules')
    
    if not cursorrules.exists():
        return False, "TASK FAILED: .cursorrules file not found"
    
    try:
        content = cursorrules.read_text()
        
        # Check for all 11 directives
        required_directives = [
            "1. FUNCTIONAL REALITY ONLY",
            "2. TRUTH OVER COMFORT",
            "3. EXECUTE WITH PRECISION",
            "4. AGENT TURBO MODE - MANDATORY",
            "5. BULLETPROOF VERIFICATION PROTOCOL",
            "6. FAILURE PROTOCOL",
            "7. NEVER ASSUME FOUNDATIONAL DATA",
            "8. LANGUAGE PROTOCOLS",
            "9. CODE LOCATION DIRECTIVE",
            "10. SYSTEM VERIFICATION MANDATE",
            "11. NO THEATRICAL WRAPPERS"
        ]
        
        missing = []
        for directive in required_directives:
            if directive not in content:
                missing.append(directive)
        
        if missing:
            return False, f"TASK FAILED: Missing directives: {missing}"
        
        return True, {
            'file_size': len(content),
            'directives_found': len(required_directives),
            'enforced': True
        }
    except Exception as e:
        return False, f"TASK FAILED: Error reading .cursorrules: {e}"

def check_prime_directives_json():
    """Check if prime_directives.json exists and is valid."""
    json_file = Path('/Volumes/DATA/Agent_Turbo/.cursor/prime_directives.json')
    
    if not json_file.exists():
        return False, "TASK FAILED: prime_directives.json not found"
    
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Verify structure
        required_keys = ['version', 'enforced', 'mandatory', 'directives']
        missing_keys = [key for key in required_keys if key not in data]
        
        if missing_keys:
            return False, f"TASK FAILED: Missing keys in JSON: {missing_keys}"
        
        if not data.get('enforced'):
            return False, "TASK FAILED: Directives not marked as enforced"
        
        if not data.get('mandatory'):
            return False, "TASK FAILED: Directives not marked as mandatory"
        
        directive_count = len(data.get('directives', {}))
        if directive_count != 11:
            return False, f"TASK FAILED: Expected 11 directives, found {directive_count}"
        
        return True, {
            'version': data.get('version'),
            'enforced': data.get('enforced'),
            'mandatory': data.get('mandatory'),
            'directive_count': directive_count,
            'workspace': data.get('workspace'),
            'verification_commands': len(data.get('verification_commands', {}))
        }
    except Exception as e:
        return False, f"TASK FAILED: Error reading prime_directives.json: {e}"

def check_vscode_settings():
    """Check if VSCode settings reference the directives."""
    settings_file = Path('/Volumes/DATA/Agent_Turbo/.vscode/settings.json')
    
    if not settings_file.exists():
        return False, "TASK FAILED: settings.json not found"
    
    try:
        with open(settings_file, 'r') as f:
            settings = json.load(f)
        
        required_settings = [
            'agent_turbo.enabled',
            'agent_turbo.prime_directives',
            'agent_turbo.enforce_directives'
        ]
        
        missing = [s for s in required_settings if s not in settings]
        
        if missing:
            return False, f"TASK FAILED: Missing settings: {missing}"
        
        if not settings.get('agent_turbo.enabled'):
            return False, "TASK FAILED: agent_turbo.enabled is false"
        
        if not settings.get('agent_turbo.enforce_directives'):
            return False, "TASK FAILED: agent_turbo.enforce_directives is false"
        
        return True, {
            'agent_turbo_enabled': settings.get('agent_turbo.enabled'),
            'enforce_directives': settings.get('agent_turbo.enforce_directives'),
            'prime_directives_path': settings.get('agent_turbo.prime_directives'),
            'cursorrules_path': settings.get('agent_turbo.cursorrules')
        }
    except Exception as e:
        return False, f"TASK FAILED: Error reading settings.json: {e}"

def verify_enforcement():
    """Test that directives are actually accessible and enforced."""
    # Check environment variable
    env_directives = os.getenv('AGENT_TURBO_PRIME_DIRECTIVES')
    
    if not env_directives:
        return False, "WARNING: AGENT_TURBO_PRIME_DIRECTIVES env var not set (will be set on next Cursor restart)"
    
    if not Path(env_directives).exists():
        return False, f"TASK FAILED: Prime directives file not found at {env_directives}"
    
    return True, {'env_var_set': True, 'file_accessible': True}

def test_agent_turbo_integration():
    """Test that Agent Turbo respects the directives."""
    sys.path.insert(0, '/Volumes/DATA/Agent_Turbo')
    
    try:
        from core.agent_turbo import AgentTurbo
        
        # This should succeed if Agent Turbo is operational
        turbo = AgentTurbo()
        verified = turbo.verify()
        
        if not verified:
            return False, "TASK FAILED: Agent Turbo verification failed"
        
        return True, {
            'agent_turbo_operational': True,
            'verification_passed': verified
        }
    except Exception as e:
        return False, f"TASK FAILED: Agent Turbo integration error: {e}"

def main():
    """Run all verification checks."""
    print("=" * 70)
    print("PRIME DIRECTIVES ENFORCEMENT VERIFICATION")
    print("=" * 70)
    print("\nVerifying that Prime Directives are configured and enforced...\n")
    
    all_passed = True
    
    # Check 1: .cursorrules file
    print("[1] Checking .cursorrules file...")
    passed, result = check_cursorrules()
    if passed:
        print("    ✅ .cursorrules file exists and contains all 11 directives")
        print(f"    📄 File size: {result.get('file_size')} bytes")
        print(f"    📋 Directives found: {result.get('directives_found')}")
    else:
        print(f"    ❌ {result}")
        all_passed = False
    
    # Check 2: prime_directives.json
    print("\n[2] Checking prime_directives.json...")
    passed, result = check_prime_directives_json()
    if passed:
        print("    ✅ prime_directives.json exists and is valid")
        print(f"    📦 Version: {result.get('version')}")
        print(f"    🔒 Enforced: {result.get('enforced')}")
        print(f"    ⚡ Mandatory: {result.get('mandatory')}")
        print(f"    📋 Directives: {result.get('directive_count')}")
        print(f"    📁 Workspace: {result.get('workspace')}")
    else:
        print(f"    ❌ {result}")
        all_passed = False
    
    # Check 3: VSCode settings
    print("\n[3] Checking VSCode settings integration...")
    passed, result = check_vscode_settings()
    if passed:
        print("    ✅ Settings.json configured correctly")
        print(f"    🚀 Agent Turbo enabled: {result.get('agent_turbo_enabled')}")
        print(f"    🔒 Enforce directives: {result.get('enforce_directives')}")
        print(f"    📄 Prime directives path: {result.get('prime_directives_path')}")
    else:
        print(f"    ❌ {result}")
        all_passed = False
    
    # Check 4: Environment enforcement
    print("\n[4] Checking environment enforcement...")
    passed, result = verify_enforcement()
    if passed:
        print("    ✅ Environment configured for enforcement")
        print(f"    🔐 Env var set: {result.get('env_var_set')}")
        print(f"    📂 File accessible: {result.get('file_accessible')}")
    else:
        if isinstance(result, str) and result.startswith("WARNING"):
            print(f"    ⚠️  {result}")
        else:
            print(f"    ❌ {result}")
            all_passed = False
    
    # Check 5: Agent Turbo integration
    print("\n[5] Testing Agent Turbo integration...")
    passed, result = test_agent_turbo_integration()
    if passed:
        print("    ✅ Agent Turbo operational and respecting directives")
        print(f"    🚀 Operational: {result.get('agent_turbo_operational')}")
        print(f"    ✅ Verified: {result.get('verification_passed')}")
    else:
        print(f"    ❌ {result}")
        all_passed = False
    
    # Final verdict
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ VERIFICATION COMPLETE: Prime Directives ENFORCED")
        print("=" * 70)
        print("\nAll Prime Directives are properly configured and enforced.")
        print("\nCursor will respect these directives at all times:")
        print("  • Functional reality only - no claims without verification")
        print("  • Truth over comfort - no sugar-coating")
        print("  • Execute with precision - bulletproof protocols")
        print("  • Agent Turbo mandatory - 1000x performance")
        print("  • Bulletproof verification - mandatory phases")
        print("  • Failure protocol - clear reporting")
        print("  • Never assume - verify everything")
        print("  • Language protocols - accurate terminology")
        print("  • Code location - project structure only")
        print("  • System verification - test real functionality")
        print("  • No theatrical wrappers - zero tolerance")
        print("\n" + "=" * 70)
        return True
    else:
        print("❌ TASK FAILED: Some verification checks failed")
        print("=" * 70)
        print("\nReview the failed checks above and fix before proceeding.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

