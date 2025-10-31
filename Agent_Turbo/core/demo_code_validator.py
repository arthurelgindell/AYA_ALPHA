#!/usr/bin/env python3
"""
CodeValidator Demonstration
Shows full validation cycle and GitHub integration
"""

from pathlib import Path
from code_validator import CodeValidator

def demo_validation_cycle():
    """Demonstrate full validation cycle until production-ready"""

    print("🎯 CodeValidator Demonstration")
    print("="*70)

    # Initialize validator
    print("\n1️⃣ Initializing CodeValidator with Qwen3 Coder 480B preference...")
    validator = CodeValidator(model_preference="coder")
    print("   ✅ CodeValidator ready")

    # Test code with deliberate issues
    test_code = """def calculate_total(prices):
    total = 0
    for i in range(len(prices)):
        total += prices[i]
    return total
"""

    print("\n2️⃣ Test Code (has style/performance issues):")
    print(test_code)

    # Run validation cycle
    print("\n3️⃣ Running validation cycle (up to 3 iterations)...")
    print("   This will automatically fix issues until production-ready\n")

    result = validator.validation_cycle(
        code=test_code,
        language="python",
        max_iterations=3,
        target_severity="LOW"
    )

    # Show results
    print(f"\n{'='*70}")
    print("📊 Validation Cycle Results")
    print(f"{'='*70}")

    if result['success']:
        print(f"✅ Success: {result['success']}")
        print(f"🎯 Production Ready: {result['production_ready']}")
        print(f"🔄 Iterations: {len(result['iterations'])}")
        print(f"🔧 Total Issues Fixed: {result.get('total_issues_fixed', 0)}")
        print(f"⏱️  Total Time: {result.get('total_time', 0):.2f}s")

        if result.get('remaining_issues', 0) > 0:
            print(f"⚠️  Remaining Issues: {result['remaining_issues']} (low severity)")

        print(f"\n📝 Final Code:")
        print(result['final_code'])

        # Try to sign off for production
        if result['production_ready']:
            print(f"\n4️⃣ Signing off for production...")
            test_file = Path("/Users/arthurdell/AYA/Agent_Turbo/core/validated_calculate_total.py")

            sign_off = validator.sign_off_for_production(
                code=result['final_code'],
                validation_result=result,
                file_path=str(test_file),
                auto_commit=False  # Safe default
            )

            if sign_off['success']:
                print(f"   ✅ Code written to: {sign_off['file_path']}")
                print(f"   📝 Commit message: {sign_off['commit_message']}")
                print(f"\n   To commit manually:")
                print(f"   cd /Users/arthurdell/AYA/Agent_Turbo/core")
                print(f"   git add {test_file.name}")
                print(f"   git commit -m \"{sign_off['commit_message']}\"")
            else:
                print(f"   ⚠️  Sign-off blocked: {sign_off.get('error')}")
    else:
        print(f"❌ Validation failed: {result.get('error')}")

    # Show statistics
    print(f"\n{'='*70}")
    print("📈 Validator Statistics")
    print(f"{'='*70}")
    stats = validator.get_stats()
    for key, value in stats.items():
        if key != 'lm_studio_stats':
            print(f"   {key}: {value}")

    print(f"\n{'='*70}")


def demo_security_validation():
    """Demonstrate security-focused validation"""

    print("\n\n🔒 Security Validation Demonstration")
    print("="*70)

    validator = CodeValidator(model_preference="coder")

    # Code with security vulnerability
    vulnerable_code = """import os

def run_command(user_input):
    os.system(f"echo {user_input}")
"""

    print("\n1️⃣ Vulnerable Code:")
    print(vulnerable_code)

    print("\n2️⃣ Running security-focused validation...")
    validation = validator.validate_code(
        vulnerable_code,
        language="python",
        validation_type="security"
    )

    if validation['success']:
        print(f"\n📊 Security Analysis Results:")
        print(f"   Issues found: {validation['issues_found']}")
        print(f"   Validation time: {validation['validation_time']:.2f}s\n")

        for issue in validation['issues']:
            print(f"   [{issue['severity']}] {issue['category']}")
            print(f"   {issue['description'][:120]}...\n")

        if validation['suggestions']:
            print(f"   💡 Suggestions:")
            for i, suggestion in enumerate(validation['suggestions'], 1):
                print(f"   {i}. {suggestion}")

    print(f"\n{'='*70}")


if __name__ == "__main__":
    # Run main demonstration
    demo_validation_cycle()

    # Run security demonstration
    demo_security_validation()

    print("\n✅ Demonstration complete!")
    print("\nKey Features Demonstrated:")
    print("  ✓ Automatic model detection and fallback")
    print("  ✓ Qwen3 Coder 480B priority (when loaded)")
    print("  ✓ Multi-iteration validation cycle")
    print("  ✓ Automatic fix generation")
    print("  ✓ Production sign-off validation")
    print("  ✓ Security-focused analysis")
    print("  ✓ GitHub integration ready (auto_commit=True to use)")
