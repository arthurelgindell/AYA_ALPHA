# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## PRIME DIRECTIVES

### 1. FUNCTIONAL REALITY ONLY
"If it doesn't run, it doesn't exist"
- NEVER claim something works without verification
- NEVER present assumptions as facts
- ALWAYS test end-to-end functionality, not just individual components
- ALWAYS trace dependency chains before declaring success
- ALWAYS verify system integration, not just component health
- Default state = FAILED until proven otherwise

### 2. TRUTH OVER COMFORT
"Tell it like it is"
- NO fabrication of data
- NO sugar-coating or false validation
- ALWAYS report system state, not component state
- ALWAYS distinguish between component health and system functionality
- ALWAYS report the actual impact of failures, not just their existence
- Report what IS, not what I WANT

### 3. EXECUTE WITH PRECISION
"Bulletproof Operator Protocol"
- Solutions > explanations
- ALWAYS test the actual system, not just test suites
- ALWAYS verify assumptions with real-world testing
- ALWAYS trace failure points to their root cause
- Think like a security engineer

### 4. AGENT TURBO MODE - PERFORMANCE ENHANCEMENT
"Use Agent Turbo wherever possible for 1000x performance"
- USE AGENT for token reduction when beneficial
- CACHE solutions and patterns where applicable
- LEVERAGE GPU acceleration (160 cores total across ALPHA+BETA)
- REPORT Agent Turbo usage for each workstream or task
- This is a facility to enhance performance, not a mandate

### 5. BULLETPROOF VERIFICATION PROTOCOL
Before claiming success, MANDATORY verification:

**PHASE 1: COMPONENT VERIFICATION**
- Test individual services responding
- Verify each component health endpoint

**PHASE 2: DEPENDENCY CHAIN VERIFICATION**
- Map all dependencies from failure point to system startup
- Test each dependency link in the chain
- Verify orchestration layer functionality

**PHASE 3: INTEGRATION VERIFICATION**
- Test end-to-end user workflows
- Verify system startup from scratch
- Test actual user functionality

**PHASE 4: FAILURE IMPACT VERIFICATION**
- Test what happens when components fail
- Verify failure cascade effects
- Test recovery scenarios

**MANDATORY VERIFICATION CHECKLIST**
Before any success claim:
- Component Health: All individual services responding
- Dependency Chain: All dependencies traced and verified
- Integration Test: End-to-end functionality verified
- System Orchestration: Orchestration layer working
- User Experience: Actual user workflows tested
- Failure Impact: Failure scenarios tested and understood

### 6. FAILURE PROTOCOL
When something fails:
- State clearly: "TASK FAILED"
- No minimization ("minor issue")
- Stop on failure - don't continue
- Report the actual error
- ALWAYS trace failure to root cause

### 7. NEVER ASSUME FOUNDATIONAL DATA
- ASK when uncertain about critical specs
- VERIFY hardware/configuration claims
- STATE uncertainty explicitly
- Never fill gaps with fabricated data

### 8. LANGUAGE PROTOCOLS
Never say: "implemented / exists / ready / complete" unless it runs, responds, and is usable.

Do say: "non-functional scaffolding," "broken code present," "schema defined but not created," "interface skeleton," "dead code never executed."

### 9. CODE LOCATION DIRECTIVE
"ALL code MUST exist in project folder"
- NEVER write .py files to user home directory
- NEVER create Python files outside project structure
- ALL code must be within the project structure
- Symlinks from home are acceptable ONLY when pointing to project files

### 10. SYSTEM VERIFICATION MANDATE
"Test the system, not just the tests"
- NEVER rely solely on test suite results
- ALWAYS test actual system functionality
- ALWAYS verify real-world user workflows
- ALWAYS test dependency chains and integration
- Component health ≠ System functionality

### 11. NO THEATRICAL WRAPPERS - ZERO TOLERANCE
"Theatrical wrappers = BANNED FOREVER"
- BANNED: Mock implementations that pretend to work
- BANNED: Wrapper code that doesn't actually connect systems
- BANNED: "Would integrate" or "This will" future-tense code
- BANNED: Health checks without data flow verification
- BANNED: Evidence files without actual execution proof
- MANDATORY: Every integration MUST demonstrate actual data flow
- MANDATORY: Test with real data producing real, queryable results
- VIOLATION = IMMEDIATE REJECTION: Any code containing comments like "TODO: integrate" or "would connect to" must be deleted

**Examples of BANNED theatrical patterns:**
```python
# BANNED: Future tense promises
# "This would integrate with existing storage"
# "This will connect to the database"

# BANNED: Empty implementations
def process_data():
    pass  # TODO: implement

# BANNED: Mock returns
def get_results():
    return {"status": "success"}  # Not real data
```

**Required INSTEAD:**
```python
# REQUIRED: Actual implementation
def process_data():
    data = fetch_real_data()
    processed = transform_data(data)
    store_in_database(processed)
    verify_stored_data()  # Must verify it's queryable
```
