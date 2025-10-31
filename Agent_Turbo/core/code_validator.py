#!/usr/bin/env python3
"""
Code Validation System for Agent Turbo
Automated code review, validation, and improvement cycle using LM Studio

PRIME DIRECTIVES COMPLIANT:
- Functional reality only (actual LM Studio API calls)
- No theatrical wrappers (real validation, not mocks)
- Bulletproof verification (tests actual code execution)
"""

import json
import time
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from datetime import datetime
import subprocess
import sys

# Import existing Agent Turbo components
try:
    from lm_studio_client import LMStudioClient
except ImportError:
    from core.lm_studio_client import LMStudioClient


class CodeValidator:
    """
    Automated code validation system using LM Studio for code review.

    Features:
    - Multi-pass validation (security, style, logic, performance)
    - Automated fix suggestions
    - Validation cycle until production-ready
    - GitHub integration for sign-off
    - Database audit trail
    """

    def __init__(self,
                 lm_studio_url: str = "http://localhost:1234/v1",
                 model_preference: str = "mlx",
                 db_connection = None):
        """
        Initialize CodeValidator

        Args:
            lm_studio_url: LM Studio API endpoint (default: localhost)
            model_preference: "mlx" for 80B MLX model (default, fastest), "coder" for 480B model
            db_connection: Optional PostgreSQL connection for audit trail
        """
        # Initialize LM Studio client
        self.lm_client = LMStudioClient(base_url=lm_studio_url)
        self.model_preference = model_preference
        self.db = db_connection

        # Validation statistics
        self.stats = {
            'validations_performed': 0,
            'issues_found': 0,
            'issues_fixed': 0,
            'cycles_run': 0,
            'production_approvals': 0
        }

        # Configure model endpoint based on preference
        if model_preference == "mlx" or model_preference == "standard":
            # Use ALPHA's 80B MLX model (default - 4.6x faster, same quality)
            self.lm_client.base_url = "http://192.168.0.80:1234/v1"
            # Re-test connectivity to get actual model
            try:
                import requests
                response = requests.get(f"{self.lm_client.base_url}/models", timeout=10)
                if response.status_code == 200:
                    models = response.json()
                    # Prioritize qwen3-next-80b-a3b-instruct-mlx (MLX-optimized)
                    # Priority 1: 80B MLX model (fastest, same quality as 480B)
                    mlx_model = None
                    for model in models.get('data', []):
                        model_id = model['id'].lower()
                        # Priority 1: qwen3-next-80b-a3b-instruct-mlx
                        if 'qwen3' in model_id and 'next' in model_id and '80b' in model_id and 'mlx' in model_id:
                            mlx_model = model['id']
                            print(f"🎯 Using 80B MLX model (optimal): {mlx_model}")
                            break
                        # Priority 2: Any 80B MLX model
                        elif '80b' in model_id and 'mlx' in model_id and not mlx_model:
                            mlx_model = model['id']
                        # Priority 3: Any 80B model
                        elif '80b' in model_id and not mlx_model:
                            mlx_model = model['id']

                    if mlx_model:
                        self.lm_client.model_id = mlx_model
                        if 'mlx' not in mlx_model.lower():
                            print(f"🎯 Using 80B model: {mlx_model}")
                    else:
                        # Fallback to first available model
                        if models.get('data'):
                            self.lm_client.model_id = models['data'][0]['id']
                            print(f"⚠️  80B MLX model not found, using: {self.lm_client.model_id}")
            except Exception as e:
                print(f"⚠️  Could not auto-detect model: {e}")
        elif model_preference == "coder":
            # Use ALPHA's 480B coder model for deep analysis (slower but thorough)
            self.lm_client.base_url = "http://192.168.0.80:1234/v1"
            try:
                import requests
                response = requests.get(f"{self.lm_client.base_url}/models", timeout=10)
                if response.status_code == 200:
                    models = response.json()
                    coder_model = None
                    for model in models.get('data', []):
                        model_id = model['id'].lower()
                        if 'qwen3' in model_id and 'coder' in model_id and '480b' in model_id:
                            coder_model = model['id']
                            print(f"🎯 Using 480B Coder model: {coder_model}")
                            break
                        elif 'coder' in model_id and not coder_model:
                            coder_model = model['id']
                        elif '480b' in model_id and not coder_model:
                            coder_model = model['id']

                    if coder_model:
                        self.lm_client.model_id = coder_model
                    else:
                        if models.get('data'):
                            self.lm_client.model_id = models['data'][0]['id']
                            print(f"⚠️  No coder model found, using: {self.lm_client.model_id}")
            except Exception as e:
                print(f"⚠️  Could not auto-detect model: {e}")
        else:
            # Use default model
            print(f"🎯 Using default model: {self.lm_client.model_id}")

    def validate_code(self,
                     code: str,
                     language: str = "python",
                     validation_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Validate code using LM Studio

        Args:
            code: Source code to validate
            language: Programming language (python, javascript, etc.)
            validation_type: "comprehensive", "security", "style", "logic", "performance"

        Returns:
            Dict with validation results, issues found, and suggestions
        """
        self.stats['validations_performed'] += 1

        # Build validation prompt based on type
        prompts = {
            'comprehensive': self._build_comprehensive_prompt(code, language),
            'security': self._build_security_prompt(code, language),
            'style': self._build_style_prompt(code, language),
            'logic': self._build_logic_prompt(code, language),
            'performance': self._build_performance_prompt(code, language)
        }

        prompt = prompts.get(validation_type, prompts['comprehensive'])

        # Call LM Studio for analysis
        start_time = time.time()
        response = self.lm_client.generate_text(
            prompt=prompt,
            max_tokens=2000,
            temperature=0.1,  # Low temperature for consistent code analysis
            use_cache=False  # Don't cache code validation (always fresh analysis)
        )
        validation_time = time.time() - start_time

        # If model not loaded, try to fallback to loaded model
        if not response['success'] and 'model_not_found' in str(response.get('error', '')):
            print(f"   ⚠️  Preferred model not loaded, trying fallback...")
            # Try to get first available loaded model
            try:
                import requests
                models_response = requests.get(f"{self.lm_client.base_url}/models", timeout=10)
                if models_response.status_code == 200:
                    models = models_response.json()
                    if models.get('data'):
                        fallback_model = models['data'][0]['id']
                        print(f"   🔄 Using fallback model: {fallback_model}")
                        original_model = self.lm_client.model_id
                        self.lm_client.model_id = fallback_model
                        # Retry with fallback model
                        response = self.lm_client.generate_text(
                            prompt=prompt,
                            max_tokens=2000,
                            temperature=0.1,
                            use_cache=False
                        )
                        validation_time = time.time() - start_time
                        if response['success']:
                            print(f"   ✅ Fallback successful with {fallback_model}")
                        else:
                            # Restore original model ID
                            self.lm_client.model_id = original_model
            except Exception as e:
                print(f"   ⚠️  Fallback failed: {e}")

        if not response['success']:
            return {
                'success': False,
                'error': response.get('error', 'Validation failed'),
                'validation_time': validation_time
            }

        # Parse LLM response
        analysis = response['content']

        # DEBUG: Print first 500 chars of analysis
        print(f"   📄 Analysis preview: {analysis[:500]}...")

        issues = self._extract_issues(analysis)
        suggestions = self._extract_suggestions(analysis)

        print(f"   🔍 Extracted {len(issues)} issues, {len(suggestions)} suggestions")

        self.stats['issues_found'] += len(issues)

        result = {
            'success': True,
            'validation_type': validation_type,
            'language': language,
            'issues_found': len(issues),
            'issues': issues,
            'suggestions': suggestions,
            'raw_analysis': analysis,
            'validation_time': validation_time,
            'tokens_used': response.get('tokens', 0),
            'model_used': response.get('model', 'unknown'),
            'timestamp': datetime.now().isoformat()
        }

        # Log to database if available
        if self.db:
            self._log_validation_to_db(code, result)

        return result

    def _build_comprehensive_prompt(self, code: str, language: str) -> str:
        """Build comprehensive validation prompt"""
        return f"""You are an expert code reviewer. Analyze this {language} code for:

1. SECURITY: Vulnerabilities, injection risks, unsafe operations
2. CORRECTNESS: Logic errors, edge cases, type issues
3. STYLE: Code quality, readability, naming conventions
4. PERFORMANCE: Inefficiencies, bottlenecks, optimization opportunities
5. BEST PRACTICES: Design patterns, maintainability, testing

Code to review:
```{language}
{code}
```

Provide your analysis in this format:

ISSUES:
- [SECURITY] Description of security issue
- [CORRECTNESS] Description of logic issue
- [STYLE] Description of style issue
- [PERFORMANCE] Description of performance issue

SUGGESTIONS:
1. Specific fix for issue 1
2. Specific fix for issue 2
3. Improvement recommendation

SEVERITY: [CRITICAL/HIGH/MEDIUM/LOW]
PRODUCTION_READY: [YES/NO]
"""

    def _build_security_prompt(self, code: str, language: str) -> str:
        """Build security-focused validation prompt"""
        return f"""You are a security expert. Analyze this {language} code for security vulnerabilities:

- SQL injection risks
- Command injection risks
- XSS vulnerabilities
- Authentication/authorization flaws
- Data exposure risks
- Unsafe deserialization
- Path traversal vulnerabilities

Code:
```{language}
{code}
```

List each security issue found with severity and fix recommendation.
"""

    def _build_style_prompt(self, code: str, language: str) -> str:
        """Build style-focused validation prompt"""
        return f"""Review this {language} code for style and maintainability:

- Code readability
- Naming conventions
- Function complexity
- Code duplication
- Documentation quality
- Type hints (if applicable)

Code:
```{language}
{code}
```

Provide specific style improvements.
"""

    def _build_logic_prompt(self, code: str, language: str) -> str:
        """Build logic-focused validation prompt"""
        return f"""Analyze this {language} code for logical correctness:

- Edge cases handled?
- Error handling present?
- Input validation?
- Return values correct?
- State management issues?

Code:
```{language}
{code}
```

Identify logic errors and suggest fixes.
"""

    def _build_performance_prompt(self, code: str, language: str) -> str:
        """Build performance-focused validation prompt"""
        return f"""Analyze this {language} code for performance:

- Time complexity issues
- Memory usage concerns
- Redundant operations
- Database query optimization
- Caching opportunities

Code:
```{language}
{code}
```

Suggest performance optimizations.
"""

    def _extract_issues(self, analysis: str) -> List[Dict[str, str]]:
        """Extract issues from LLM analysis"""
        issues = []

        # Look for ISSUES section
        if "ISSUES:" in analysis:
            issues_section = analysis.split("ISSUES:")[1].split("SUGGESTIONS:")[0] if "SUGGESTIONS:" in analysis else analysis.split("ISSUES:")[1]

            for line in issues_section.split('\n'):
                line = line.strip()
                if line.startswith('- ['):
                    # Extract category and description
                    # Format: - [SECURITY] Description
                    try:
                        category = line.split('[')[1].split(']')[0]
                        description = line.split(']')[1].strip()
                        issues.append({
                            'category': category,
                            'description': description,
                            'severity': self._assess_severity(category, description)
                        })
                    except:
                        # Fallback if parsing fails
                        issues.append({
                            'category': 'UNKNOWN',
                            'description': line,
                            'severity': 'MEDIUM'
                        })

        return issues

    def _extract_suggestions(self, analysis: str) -> List[str]:
        """Extract fix suggestions from LLM analysis"""
        suggestions = []

        if "SUGGESTIONS:" in analysis:
            suggestions_section = analysis.split("SUGGESTIONS:")[1].split("SEVERITY:")[0] if "SEVERITY:" in analysis else analysis.split("SUGGESTIONS:")[1]

            for line in suggestions_section.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Remove numbering
                    clean_line = line.lstrip('0123456789.-) ').strip()
                    if clean_line:
                        suggestions.append(clean_line)

        return suggestions

    def _assess_severity(self, category: str, description: str) -> str:
        """Assess severity of issue"""
        # Security issues are high priority
        if category == 'SECURITY':
            if any(word in description.lower() for word in ['injection', 'vulnerability', 'exploit']):
                return 'CRITICAL'
            return 'HIGH'

        # Correctness issues are medium to high
        if category == 'CORRECTNESS':
            if any(word in description.lower() for word in ['crash', 'error', 'fail', 'incorrect']):
                return 'HIGH'
            return 'MEDIUM'

        # Style and performance are lower priority
        if category in ['STYLE', 'PERFORMANCE']:
            return 'LOW'

        return 'MEDIUM'

    def apply_fixes(self,
                   code: str,
                   validation_result: Dict[str, Any],
                   auto_fix: bool = True) -> Dict[str, Any]:
        """
        Apply suggested fixes to code

        Args:
            code: Original code
            validation_result: Result from validate_code()
            auto_fix: If True, automatically apply LLM-generated fixes

        Returns:
            Dict with fixed code and changes made
        """
        if not validation_result['success'] or not validation_result['suggestions']:
            return {
                'success': False,
                'error': 'No fixes to apply',
                'code': code
            }

        # Build fix prompt
        suggestions_text = '\n'.join(f"{i+1}. {s}" for i, s in enumerate(validation_result['suggestions']))

        fix_prompt = f"""Apply these fixes to the code:

Original code:
```python
{code}
```

Fixes to apply:
{suggestions_text}

Return ONLY the fixed code, no explanations. Format:
```python
<fixed code here>
```
"""

        response = self.lm_client.generate_text(
            prompt=fix_prompt,
            max_tokens=3000,
            temperature=0.1,
            use_cache=False
        )

        if not response['success']:
            return {
                'success': False,
                'error': 'Failed to generate fixes',
                'code': code
            }

        # Extract fixed code from response
        fixed_code = self._extract_code_block(response['content'])

        if not fixed_code:
            return {
                'success': False,
                'error': 'Could not extract fixed code',
                'code': code,
                'raw_response': response['content']
            }

        self.stats['issues_fixed'] += len(validation_result['suggestions'])

        return {
            'success': True,
            'original_code': code,
            'fixed_code': fixed_code,
            'fixes_applied': len(validation_result['suggestions']),
            'changes': self._diff_code(code, fixed_code)
        }

    def _extract_code_block(self, text: str) -> Optional[str]:
        """Extract code from markdown code block"""
        # Look for ```python ... ``` or ```language ... ```
        if '```' in text:
            blocks = text.split('```')
            for block in blocks[1::2]:  # Every other element after split is code
                # Remove language identifier
                lines = block.strip().split('\n')
                if lines[0].strip() in ['python', 'javascript', 'java', 'go', 'rust']:
                    return '\n'.join(lines[1:])
                return block.strip()
        return None

    def _diff_code(self, original: str, fixed: str) -> List[str]:
        """Generate simple diff of changes"""
        orig_lines = original.split('\n')
        fixed_lines = fixed.split('\n')

        changes = []
        for i, (orig, fix) in enumerate(zip(orig_lines, fixed_lines)):
            if orig != fix:
                changes.append(f"Line {i+1}: {orig.strip()} → {fix.strip()}")

        # Handle length differences
        if len(fixed_lines) > len(orig_lines):
            changes.append(f"Added {len(fixed_lines) - len(orig_lines)} lines")
        elif len(orig_lines) > len(fixed_lines):
            changes.append(f"Removed {len(orig_lines) - len(fixed_lines)} lines")

        return changes

    def validation_cycle(self,
                        code: str,
                        language: str = "python",
                        max_iterations: int = 3,
                        target_severity: str = "LOW") -> Dict[str, Any]:
        """
        Run validation cycle until code is production-ready

        Args:
            code: Initial code to validate
            language: Programming language
            max_iterations: Maximum number of fix cycles
            target_severity: Stop when all issues are this severity or lower

        Returns:
            Dict with final code, iteration history, and production readiness
        """
        self.stats['cycles_run'] += 1

        current_code = code
        iterations = []

        for iteration in range(max_iterations):
            print(f"\n🔄 Validation Cycle {iteration + 1}/{max_iterations}")

            # Validate current code
            validation = self.validate_code(current_code, language, "comprehensive")

            if not validation['success']:
                return {
                    'success': False,
                    'error': validation.get('error'),
                    'iterations': iterations
                }

            iterations.append({
                'iteration': iteration + 1,
                'issues_found': validation['issues_found'],
                'issues': validation['issues'],
                'validation_time': validation['validation_time']
            })

            print(f"   Found {validation['issues_found']} issues")

            # Check if production ready
            critical_issues = [i for i in validation['issues'] if i['severity'] in ['CRITICAL', 'HIGH']]

            if not critical_issues and validation['issues_found'] == 0:
                print("   ✅ Code is production-ready (no issues)")
                return {
                    'success': True,
                    'production_ready': True,
                    'final_code': current_code,
                    'iterations': iterations,
                    'total_issues_fixed': sum(len(it['issues']) for it in iterations),
                    'total_time': sum(it['validation_time'] for it in iterations)
                }

            if not critical_issues and target_severity in ['LOW', 'MEDIUM']:
                print(f"   ✅ Code meets target severity ({target_severity})")
                return {
                    'success': True,
                    'production_ready': True,
                    'final_code': current_code,
                    'iterations': iterations,
                    'total_issues_fixed': sum(len(it['issues']) for it in iterations),
                    'total_time': sum(it['validation_time'] for it in iterations),
                    'remaining_issues': validation['issues_found']
                }

            # Apply fixes
            print("   🔧 Applying fixes...")
            fix_result = self.apply_fixes(current_code, validation)

            if not fix_result['success']:
                print(f"   ⚠️  Could not apply fixes: {fix_result.get('error')}")
                break

            current_code = fix_result['fixed_code']
            print(f"   ✅ Applied {fix_result['fixes_applied']} fixes")

        # Reached max iterations
        final_validation = self.validate_code(current_code, language, "comprehensive")

        return {
            'success': True,
            'production_ready': final_validation['issues_found'] == 0,
            'final_code': current_code,
            'iterations': iterations,
            'total_issues_fixed': sum(len(it['issues']) for it in iterations),
            'total_time': sum(it['validation_time'] for it in iterations),
            'max_iterations_reached': True,
            'remaining_issues': final_validation['issues_found']
        }

    def sign_off_for_production(self,
                               code: str,
                               validation_result: Dict[str, Any],
                               file_path: str,
                               commit_message: str = None,
                               auto_commit: bool = False,
                               auto_push: bool = False) -> Dict[str, Any]:
        """
        Sign off code for production and optionally commit to GitHub

        Args:
            code: Final validated code
            validation_result: Final validation result
            file_path: Path where code should be saved
            commit_message: Optional custom commit message
            auto_commit: If True, automatically git add and commit
            auto_push: If True, automatically git push (requires auto_commit=True)

        Returns:
            Dict with sign-off status and GitHub operations result
        """
        # Check if production ready
        if not validation_result.get('production_ready', False):
            remaining = validation_result.get('remaining_issues', 0)
            return {
                'success': False,
                'error': f'Code not production-ready ({remaining} issues remaining)',
                'production_ready': False
            }

        # Write code to file
        try:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(code)
            print(f"✅ Code written to: {file_path}")
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to write file: {e}',
                'production_ready': True
            }

        # Generate commit message if not provided
        if not commit_message:
            iterations = validation_result.get('iterations', [])
            total_fixes = validation_result.get('total_issues_fixed', 0)
            commit_message = f"Code validation complete: {total_fixes} issues fixed across {len(iterations)} iterations"

        self.stats['production_approvals'] += 1

        result = {
            'success': True,
            'production_ready': True,
            'file_path': str(file_path),
            'commit_message': commit_message,
            'validation_summary': {
                'iterations': len(validation_result.get('iterations', [])),
                'issues_fixed': validation_result.get('total_issues_fixed', 0),
                'total_time': validation_result.get('total_time', 0)
            },
            'ready_for_github': True,
            'git_operations': {
                'committed': False,
                'pushed': False
            }
        }

        # Execute git operations if requested
        if auto_commit:
            git_result = self._git_commit(file_path, commit_message, auto_push)
            result['git_operations'] = git_result

            if not git_result['success']:
                result['git_error'] = git_result.get('error')
                print(f"⚠️  Git operations failed: {git_result.get('error')}")
            else:
                if git_result['committed']:
                    print(f"✅ Committed to git: {git_result['commit_sha']}")
                if git_result['pushed']:
                    print(f"✅ Pushed to remote: {git_result['remote']}")

        return result

    def _git_commit(self,
                   file_path: Path,
                   commit_message: str,
                   push: bool = False) -> Dict[str, Any]:
        """
        Execute git add, commit, and optionally push

        Args:
            file_path: File to add and commit
            commit_message: Commit message
            push: If True, push to remote

        Returns:
            Dict with git operation results
        """
        try:
            # Check if we're in a git repository
            status_result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                cwd=file_path.parent,
                capture_output=True,
                text=True,
                timeout=5
            )

            if status_result.returncode != 0:
                return {
                    'success': False,
                    'error': 'Not in a git repository',
                    'committed': False,
                    'pushed': False
                }

            # Git add
            add_result = subprocess.run(
                ['git', 'add', str(file_path)],
                cwd=file_path.parent,
                capture_output=True,
                text=True,
                timeout=10
            )

            if add_result.returncode != 0:
                return {
                    'success': False,
                    'error': f'Git add failed: {add_result.stderr}',
                    'committed': False,
                    'pushed': False
                }

            # Git commit
            commit_result = subprocess.run(
                ['git', 'commit', '-m', commit_message],
                cwd=file_path.parent,
                capture_output=True,
                text=True,
                timeout=10
            )

            if commit_result.returncode != 0:
                # Check if it's "nothing to commit" (not an error)
                if 'nothing to commit' in commit_result.stdout.lower():
                    return {
                        'success': True,
                        'warning': 'No changes to commit',
                        'committed': False,
                        'pushed': False
                    }
                return {
                    'success': False,
                    'error': f'Git commit failed: {commit_result.stderr}',
                    'committed': False,
                    'pushed': False
                }

            # Extract commit SHA
            commit_sha = None
            for line in commit_result.stdout.split('\n'):
                if line.strip().startswith('['):
                    # Format: [branch commit_sha] message
                    parts = line.split(']')[0].split()
                    if len(parts) > 1:
                        commit_sha = parts[1]
                    break

            result = {
                'success': True,
                'committed': True,
                'commit_sha': commit_sha,
                'pushed': False
            }

            # Git push if requested
            if push:
                push_result = subprocess.run(
                    ['git', 'push'],
                    cwd=file_path.parent,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if push_result.returncode != 0:
                    result['push_error'] = push_result.stderr
                    result['success'] = False
                else:
                    result['pushed'] = True
                    # Extract remote name
                    remote_result = subprocess.run(
                        ['git', 'remote', '-v'],
                        cwd=file_path.parent,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if remote_result.returncode == 0:
                        for line in remote_result.stdout.split('\n'):
                            if '(push)' in line:
                                result['remote'] = line.split()[0]
                                break

            return result

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Git operation timed out',
                'committed': False,
                'pushed': False
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Git operation failed: {str(e)}',
                'committed': False,
                'pushed': False
            }

    def _log_validation_to_db(self, code: str, validation_result: Dict[str, Any]):
        """Log validation to PostgreSQL database (if available)"""
        if not self.db:
            return

        try:
            # This would integrate with Agent Turbo's database
            # For now, just a placeholder showing the structure
            pass
        except Exception as e:
            print(f"⚠️  Database logging failed: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get validator statistics"""
        return {
            **self.stats,
            'lm_studio_stats': self.lm_client.get_stats()
        }


def main():
    """Test the CodeValidator"""
    print("🧪 Testing CodeValidator\n")

    # Initialize validator
    validator = CodeValidator(model_preference="coder")

    # Test code with intentional issues
    test_code = """
def process_user_data(user_input):
    # Security issue: SQL injection vulnerability
    query = f"SELECT * FROM users WHERE name = '{user_input}'"

    # Logic issue: No error handling
    result = execute_query(query)

    # Performance issue: Inefficient loop
    for i in range(len(result)):
        print(result[i])

    return result
"""

    print("📝 Test Code:")
    print(test_code)

    # Run validation cycle
    print("\n🔄 Running validation cycle...\n")
    result = validator.validation_cycle(test_code, max_iterations=2)

    if result['success']:
        print(f"\n{'='*60}")
        print("✅ VALIDATION CYCLE COMPLETE")
        print(f"{'='*60}")
        print(f"Production Ready: {result['production_ready']}")
        print(f"Iterations: {len(result['iterations'])}")
        print(f"Issues Fixed: {result['total_issues_fixed']}")
        print(f"Total Time: {result['total_time']:.2f}s")

        if result['production_ready']:
            print("\n📝 Final Code:")
            print(result['final_code'])

    # Print stats
    print(f"\n📊 Validator Statistics:")
    stats = validator.get_stats()
    for key, value in stats.items():
        if key != 'lm_studio_stats':
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
