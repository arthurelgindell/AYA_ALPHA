#!/usr/bin/env python3
"""
AYA Code Validator Service
Automated code review using ALPHA's qwen3-next-80b-a3b-instruct-mlx model
Accessible via Tailscale from all nodes (ALPHA, BETA, Gamma)

Author: Claude for Arthur
Date: October 29, 2025
"""

import sys
import json
import requests
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Configuration
DEFAULT_MODEL = "qwen3-next-80b-a3b-instruct-mlx"
ALPHA_LM_STUDIO_URL = "https://alpha.tail5f2bae.ts.net/v1"  # Tailscale access
ALPHA_LM_STUDIO_LOCAL = "http://localhost:1234/v1"  # Local if on ALPHA
TIMEOUT = 120  # 2 minutes for large files

class CodeValidator:
    """
    Automated code validation service using LM Studio on ALPHA.
    
    Features:
    - Security vulnerability detection
    - Bug identification
    - Best practices review
    - Performance suggestions
    - Accessible via Tailscale from any node
    """
    
    def __init__(self, use_tailscale: bool = True, model: str = DEFAULT_MODEL):
        """
        Initialize code validator.
        
        Args:
            use_tailscale: Use Tailscale URL (True) or localhost (False)
            model: Model to use for validation
        """
        self.model = model
        self.base_url = ALPHA_LM_STUDIO_URL if use_tailscale else ALPHA_LM_STUDIO_LOCAL
        self.session = requests.Session()
        if use_tailscale:
            self.session.verify = False  # Skip Tailscale cert verification
        
        self.stats = {
            'files_validated': 0,
            'issues_found': 0,
            'total_time': 0.0,
            'errors': 0
        }
        
        # Test connectivity
        self._test_connectivity()
    
    def _test_connectivity(self):
        """Test connection to LM Studio."""
        try:
            response = self.session.get(f"{self.base_url}/models", timeout=10)
            if response.status_code == 200:
                models = response.json()
                model_ids = [m['id'] for m in models.get('data', [])]
                if self.model in model_ids:
                    print(f"✅ Code Validator connected to {self.model}")
                else:
                    print(f"⚠️  Model {self.model} not found, available: {model_ids}")
            else:
                print(f"❌ LM Studio connection failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ LM Studio connection error: {e}")
    
    def validate_code(self, code: str, filename: str = "code.py", 
                     language: str = "python") -> Dict[str, Any]:
        """
        Validate code for security, bugs, and best practices.
        
        Args:
            code: Source code to validate
            filename: Name of file (for context)
            language: Programming language
            
        Returns:
            Dictionary with validation results
        """
        import time
        start_time = time.time()
        
        # Detect language if not specified
        if filename.endswith('.py'):
            language = 'Python'
        elif filename.endswith('.js') or filename.endswith('.ts'):
            language = 'JavaScript/TypeScript'
        elif filename.endswith('.sh'):
            language = 'Bash/Shell'
        elif filename.endswith('.go'):
            language = 'Go'
        elif filename.endswith('.rs'):
            language = 'Rust'
        
        prompt = f"""Review this {language} code from {filename} and identify:
1. Security vulnerabilities (SQL injection, XSS, etc.)
2. Bugs and logic errors
3. Performance issues
4. Best practices violations
5. Suggested improvements

Code:
```{language.lower()}
{code}
```

Provide a structured response with specific line references where possible."""
        
        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json={
                    'model': self.model,
                    'messages': [
                        {
                            'role': 'system',
                            'content': 'You are an expert code security auditor and software engineer. Provide concise, actionable feedback.'
                        },
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ],
                    'max_tokens': 1000,
                    'temperature': 0.3
                },
                timeout=TIMEOUT
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                review = data['choices'][0]['message']['content']
                usage = data.get('usage', {})
                
                # Count issues (rough heuristic)
                issues_count = review.lower().count('vulnerability') + \
                              review.lower().count('bug') + \
                              review.lower().count('error') + \
                              review.lower().count('issue')
                
                # Update stats
                self.stats['files_validated'] += 1
                self.stats['issues_found'] += issues_count
                self.stats['total_time'] += response_time
                
                return {
                    'success': True,
                    'filename': filename,
                    'language': language,
                    'review': review,
                    'issues_detected': issues_count,
                    'response_time': response_time,
                    'tokens_used': usage.get('total_tokens', 0),
                    'model': self.model,
                    'code_hash': hashlib.sha256(code.encode()).hexdigest()[:16],
                    'timestamp': datetime.now().isoformat()
                }
            else:
                self.stats['errors'] += 1
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'filename': filename,
                    'response_time': response_time
                }
                
        except Exception as e:
            self.stats['errors'] += 1
            return {
                'success': False,
                'error': str(e),
                'filename': filename,
                'response_time': time.time() - start_time
            }
    
    def validate_file(self, filepath: str) -> Dict[str, Any]:
        """
        Validate a code file.
        
        Args:
            filepath: Path to file
            
        Returns:
            Validation results
        """
        try:
            with open(filepath, 'r') as f:
                code = f.read()
            
            filename = Path(filepath).name
            return self.validate_code(code, filename)
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to read file: {e}",
                'filename': filepath
            }
    
    def validate_directory(self, directory: str, 
                          extensions: List[str] = ['.py', '.js', '.sh']) -> List[Dict[str, Any]]:
        """
        Validate all code files in a directory.
        
        Args:
            directory: Directory path
            extensions: File extensions to validate
            
        Returns:
            List of validation results
        """
        results = []
        dir_path = Path(directory)
        
        for ext in extensions:
            for filepath in dir_path.rglob(f'*{ext}'):
                if filepath.is_file():
                    print(f"Validating: {filepath}")
                    result = self.validate_file(str(filepath))
                    results.append(result)
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get validation statistics."""
        avg_time = (self.stats['total_time'] / self.stats['files_validated'] 
                   if self.stats['files_validated'] > 0 else 0)
        
        return {
            'files_validated': self.stats['files_validated'],
            'issues_found': self.stats['issues_found'],
            'errors': self.stats['errors'],
            'total_time': round(self.stats['total_time'], 2),
            'average_time_per_file': round(avg_time, 2),
            'model_used': self.model,
            'access_method': 'Tailscale' if ALPHA_LM_STUDIO_URL in self.base_url else 'Local'
        }
    
    def batch_validate(self, files: List[str]) -> Dict[str, Any]:
        """
        Validate multiple files and return summary.
        
        Args:
            files: List of file paths
            
        Returns:
            Summary with all results
        """
        results = []
        for filepath in files:
            result = self.validate_file(filepath)
            results.append(result)
        
        # Summary statistics
        successful = sum(1 for r in results if r.get('success'))
        failed = len(results) - successful
        total_issues = sum(r.get('issues_detected', 0) for r in results if r.get('success'))
        
        return {
            'summary': {
                'total_files': len(files),
                'validated': successful,
                'failed': failed,
                'total_issues_found': total_issues,
                'model': self.model
            },
            'results': results,
            'stats': self.get_stats()
        }


def main():
    """CLI interface for code validator."""
    import argparse
    
    parser = argparse.ArgumentParser(description='AYA Code Validator Service')
    parser.add_argument('action', choices=['validate', 'batch', 'test', 'stats'],
                       help='Action to perform')
    parser.add_argument('--file', help='File to validate')
    parser.add_argument('--files', nargs='+', help='Multiple files to validate')
    parser.add_argument('--code', help='Code string to validate')
    parser.add_argument('--model', default=DEFAULT_MODEL, help='Model to use')
    parser.add_argument('--local', action='store_true', help='Use localhost instead of Tailscale')
    parser.add_argument('--output', help='Output file for results (JSON)')
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = CodeValidator(use_tailscale=not args.local, model=args.model)
    
    if args.action == 'validate':
        if args.file:
            result = validator.validate_file(args.file)
        elif args.code:
            result = validator.validate_code(args.code, filename="inline_code")
        else:
            print("❌ Error: Provide --file or --code")
            return
        
        print(json.dumps(result, indent=2))
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
    
    elif args.action == 'batch':
        if not args.files:
            print("❌ Error: Provide --files")
            return
        
        result = validator.batch_validate(args.files)
        print(json.dumps(result, indent=2))
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
    
    elif args.action == 'test':
        # Run test with sample code
        test_code = '''def process_data(user_input):
    query = "SELECT * FROM users WHERE id = " + str(user_input)
    result = db.execute(query)
    return result'''
        
        print("Testing code validator with intentionally vulnerable code...")
        result = validator.validate_code(test_code, filename="test.py")
        print(json.dumps(result, indent=2))
    
    elif args.action == 'stats':
        stats = validator.get_stats()
        print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()

