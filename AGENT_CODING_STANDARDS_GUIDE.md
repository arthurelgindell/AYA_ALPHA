# AYA Agent Coding Standards Guide

**For**: All AYA Agents  
**Version**: 1.0  
**Date**: October 30, 2025  
**Status**: ✅ MANDATORY FOR ALL AGENTS

---

## 🔴 AYA BULLET PROOF PRIME DIRECTIVES

**MANDATORY COMPLIANCE**: All code validation enforced under AYA BULLET PROOF PRIME DIRECTIVES

**Master Document**: `/Users/arthurdell/AYA/AYA_PRIME_DIRECTIVES.md`

**Key Principles**:
- **Functional Reality Only** (Default = FAILED until proven)
- **Truth Over Comfort** (Report actual state)
- **Bulletproof Verification Protocol** (4-phase verification mandatory)
- **Zero Tolerance for Theatrical Wrappers** (No mocks, no stubs, no fake data)

**Database Entry Point**: Query `agent_landing` table (version 5.0) in `aya_rag` database for complete Prime Directives context.

**Full Reference**: See `/Users/arthurdell/AYA/AYA_PRIME_DIRECTIVES.md` for complete governance framework

---

## Quick Reference

### Enforcement Levels

| Severity | Action | Threshold | Override Required |
|----------|--------|-----------|-------------------|
| **CRITICAL** | 🔴 BLOCK | 0 issues | Yes |
| **HIGH** | ⚠️ WARN | >3 issues | No |
| **MEDIUM** | 📝 LOG | >10 issues | No |
| **LOW** | ℹ️ INFO | Unlimited | No |

### Model Configuration

- **Default Model**: `qwen3-next-80b-a3b-instruct-mlx` (80B MLX)
- **Performance**: 3.74s per review
- **Concurrency**: 8 simultaneous reviews
- **Quality**: Identical to 480B model

---

## What Gets Validated

### Automatic Validation Triggers

1. **Git Commits** (Pre-commit hook)
   - All staged `.py`, `.js`, `.ts`, `.sh` files
   - Runs automatically before commit
   - Blocks commits with CRITICAL issues

2. **Git Pushes** (Pre-push hook)
   - All changed files in commits being pushed
   - Runs automatically before push
   - Blocks pushes with CRITICAL issues

3. **File Watcher** (n8n workflow)
   - Monitors `/Users/arthurdell/AYA` every 5 minutes
   - Validates recently modified files
   - Logs all validations to database

4. **Agent Code Generation** (Agent Turbo)
   - Automatic validation before writing code
   - Blocks file writes with CRITICAL issues
   - Logs all validations

### File Types Validated

- ✅ Python (`.py`)
- ✅ JavaScript (`.js`)
- ✅ TypeScript (`.ts`)
- ✅ Shell scripts (`.sh`)
- ✅ Go (`.go`) - planned
- ✅ Rust (`.rs`) - planned

---

## CRITICAL Issues (BLOCK)

These issues **BLOCK** operations immediately:

### Security Vulnerabilities

1. **SQL Injection**
   ```python
   # ❌ BAD
   query = "SELECT * FROM users WHERE id = " + user_input
   
   # ✅ GOOD
   query = "SELECT * FROM users WHERE id = %s"
   cursor.execute(query, (user_input,))
   ```

2. **XSS (Cross-Site Scripting)**
   ```python
   # ❌ BAD
   return f"<div>{user_input}</div>"
   
   # ✅ GOOD
   from html import escape
   return f"<div>{escape(user_input)}</div>"
   ```

3. **Command Injection**
   ```python
   # ❌ BAD
   os.system(f"ls {user_input}")
   
   # ✅ GOOD
   import subprocess
   subprocess.run(["ls", user_input], check=True)
   ```

4. **Path Traversal**
   ```python
   # ❌ BAD
   file_path = base_dir + user_input
   
   # ✅ GOOD
   from pathlib import Path
   file_path = Path(base_dir) / Path(user_input).name
   ```

5. **Authentication Bypass**
   ```python
   # ❌ BAD
   if user_id == "admin":
       return True
   
   # ✅ GOOD
   if user.has_permission("admin"):
       return True
   ```

### Critical Bugs

- Hardcoded secrets or passwords
- Missing authentication checks
- Insecure configuration
- Race conditions in critical sections
- Memory leaks in long-running processes

---

## HIGH Issues (WARN)

These issues trigger warnings but don't block:

1. **Missing Input Validation**
   ```python
   # ⚠️ WARN
   def process(data):
       return data.upper()
   
   # ✅ GOOD
   def process(data):
       if not isinstance(data, str):
           raise TypeError("data must be a string")
       return data.upper()
   ```

2. **Hardcoded Secrets** (if not critical)
   ```python
   # ⚠️ WARN
   API_KEY = "sk-1234567890"
   
   # ✅ GOOD
   API_KEY = os.getenv("API_KEY")
   ```

3. **Poor Error Handling**
   ```python
   # ⚠️ WARN
   def divide(a, b):
       return a / b
   
   # ✅ GOOD
   def divide(a, b):
       if b == 0:
           raise ValueError("Cannot divide by zero")
       return a / b
   ```

---

## MEDIUM Issues (LOG)

These are logged but don't affect operations:

1. **Code Complexity**
   - Functions with cyclomatic complexity > 15
   - Deeply nested conditionals (>4 levels)

2. **Code Duplication**
   - Duplicate code blocks
   - Similar functions that could be refactored

3. **Anti-patterns**
   - Magic numbers without constants
   - Global variables
   - God objects (classes doing too much)

---

## LOW Issues (INFO)

Suggestions and optimizations:

1. **Style Improvements**
   - Line length > 100 characters
   - Inconsistent naming conventions
   - Missing docstrings

2. **Performance Optimizations**
   - Inefficient algorithms
   - Unnecessary database queries
   - Missing caching opportunities

3. **Documentation**
   - Missing type hints
   - Unclear variable names
   - Incomplete docstrings

---

## Best Practices

### 1. Security First

```python
# ✅ Always validate inputs
def process_user_input(data):
    if not isinstance(data, str):
        raise TypeError("data must be a string")
    if len(data) > 1000:
        raise ValueError("data too long")
    return sanitize(data)

# ✅ Use parameterized queries
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# ✅ Sanitize outputs
from html import escape
return escape(user_content)
```

### 2. Error Handling

```python
# ✅ Use specific exceptions
try:
    result = process_data(data)
except ValueError as e:
    logger.error(f"Invalid data: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise

# ✅ Provide actionable error messages
if not user_id:
    raise ValueError("user_id is required (cannot be empty)")
```

### 3. Clear Comments

```python
# ✅ Explain WHY, not WHAT
# Using LRU cache to avoid recomputing expensive operations
# that are frequently accessed in sequence
@lru_cache(maxsize=128)
def expensive_computation(n):
    ...

# ❌ DON'T comment obvious code
# Increment counter by 1
counter += 1
```

### 4. Type Hints

```python
# ✅ Use type hints
from typing import List, Optional, Dict

def process_users(users: List[Dict[str, str]]) -> Optional[int]:
    """Process list of user dictionaries."""
    ...
```

### 5. Documentation

```python
# ✅ Comprehensive docstrings
def calculate_total(prices: List[float]) -> float:
    """
    Calculate the sum of all prices.
    
    Args:
        prices: List of numeric prices (must be finite)
    
    Returns:
        Sum of all prices as a float
    
    Raises:
        ValueError: If any price is negative or infinite
        TypeError: If prices contains non-numeric values
    
    Example:
        >>> calculate_total([10.0, 20.0, 30.0])
        60.0
    """
    ...
```

---

## How to Use Code Validation

### From Agent Turbo

```python
from core.code_validation_helper import validate_and_write, CodeQualityError

try:
    result = validate_and_write(
        file_path="/path/to/code.py",
        code=generated_code,
        agent_name="agent_turbo"
    )
    print(f"✅ Code written: {result['written']}")
except CodeQualityError as e:
    print(f"❌ Validation failed: {e}")
    print(f"Review: {e.validation_result.get('review', '')}")
    # Fix issues and retry
```

### From Command Line

```bash
# Validate single file
python3 services/code_validator_n8n.py --file script.py --agent "cli"

# Validate inline code
python3 services/code_validator_n8n.py --code 'print("test")' --agent "cli"

# Batch validate
python3 services/code_validator_n8n.py --files script1.py script2.py --agent "cli"
```

### From Git

```bash
# Pre-commit hook runs automatically
git add script.py
git commit -m "Add feature"
# ✅ Validation runs automatically

# If validation fails, fix issues:
# 1. Review the validation output
# 2. Fix CRITICAL issues
# 3. Commit again
```

---

## Handling Validation Failures

### CRITICAL Issues (Blocked)

1. **Review the validation report**
   ```bash
   # Check the validation details
   python3 services/code_validator_n8n.py --file script.py --agent "review"
   ```

2. **Fix the issues**
   - Address CRITICAL security vulnerabilities first
   - Refer to examples in this guide
   - Test fixes locally

3. **Re-validate**
   ```bash
   python3 services/code_validator_n8n.py --file script.py --agent "retry"
   ```

4. **Commit after passing**
   ```bash
   git add script.py
   git commit -m "Fix security issues"
   ```

### HIGH Issues (Warnings)

- Review warnings but proceed if acceptable
- Consider fixing in follow-up commit
- Document why warnings are acceptable if intentional

### Override (Not Recommended)

```bash
# Only if absolutely necessary
git commit --no-verify
git push --no-verify
```

**Warning**: Overriding validation defeats the purpose of code quality enforcement. Use only in emergencies.

---

## Validation Results Format

```json
{
  "success": true,
  "validation_id": "abc123",
  "filename": "script.py",
  "agent_name": "agent_turbo",
  "model_used": "qwen3-next-80b-a3b-instruct-mlx",
  "response_time": 3.74,
  "issues_detected": 5,
  "severity_counts": {
    "CRITICAL": 1,
    "HIGH": 2,
    "MEDIUM": 2,
    "LOW": 0
  },
  "enforcement_action": "block",
  "review": "Detailed review text with specific issues..."
}
```

---

## Compliance Metrics

### View Your Compliance

```sql
SELECT 
    agent_name,
    COUNT(*) as total_validations,
    SUM(CASE WHEN enforcement_action = 'block' THEN 1 ELSE 0 END) as blocked,
    AVG(issues_detected) as avg_issues
FROM code_validations
WHERE agent_name = 'your_agent_name'
GROUP BY agent_name;
```

### View Team Compliance

```sql
SELECT 
    date,
    files_validated,
    critical_issues,
    high_issues,
    compliance_score
FROM compliance_metrics
ORDER BY date DESC
LIMIT 7;
```

---

## Resources

- **Coding Standards**: `/Users/arthurdell/AYA/config/aya_coding_standards.json`
- **Deployment Guide**: `CODE_VALIDATION_N8N_DEPLOYMENT.md`
- **Implementation Details**: `CODE_VALIDATION_IMPLEMENTATION_SUMMARY.md`

---

## Summary

✅ **All code is automatically validated**  
✅ **CRITICAL issues block operations**  
✅ **Complete audit trail in database**  
✅ **Consistent standards across all agents**  
✅ **Real-time feedback on code quality**  

**Follow these standards to ensure code quality and security across the AYA platform!**

