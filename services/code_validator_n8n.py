#!/usr/bin/env python3
"""
AYA Code Validator n8n Integration Module
Webhook receiver for n8n workflows with batch processing and enforcement logic

Author: Claude for Arthur
Date: October 29, 2025
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.code_validator_service import CodeValidator, DEFAULT_MODEL

# Database logging (optional)
try:
    import psycopg2
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

# Load coding standards
STANDARDS_FILE = Path(__file__).parent.parent / "config" / "aya_coding_standards.json"

# Default standards if file doesn't exist
DEFAULT_STANDARDS = {
    "enforcement_levels": {
        "CRITICAL": "block",
        "HIGH": "warn",
        "MEDIUM": "log",
        "LOW": "info"
    },
    "thresholds": {
        "max_critical": 0,
        "max_high": 3,
        "max_medium": 10,
        "max_complexity": 15
    }
}


def load_standards() -> Dict[str, Any]:
    """Load coding standards configuration."""
    if STANDARDS_FILE.exists():
        try:
            with open(STANDARDS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Failed to load standards config: {e}, using defaults")
    return DEFAULT_STANDARDS


class CodeValidatorN8N:
    """
    n8n integration wrapper for code validator.
    
    Features:
    - Webhook endpoint for n8n workflows
    - Batch processing support
    - Enforcement decision logic
    - Result formatting for n8n
    """
    
    def __init__(self, use_tailscale: bool = True, model: str = DEFAULT_MODEL):
        """Initialize validator with n8n integration."""
        self.validator = CodeValidator(use_tailscale=use_tailscale, model=model)
        self.standards = load_standards()
        self.enforcement_levels = self.standards.get("enforcement_levels", DEFAULT_STANDARDS["enforcement_levels"])
        self.thresholds = self.standards.get("thresholds", DEFAULT_STANDARDS["thresholds"])
    
    def _classify_issue_severity(self, review_text: str) -> Dict[str, int]:
        """
        Classify issues by severity from review text.
        
        Returns:
            Dict with counts: {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        """
        text_lower = review_text.lower()
        
        # Critical keywords (security vulnerabilities)
        critical_keywords = [
            'sql injection', 'xss', 'csrf', 'auth bypass', 'privilege escalation',
            'command injection', 'path traversal', 'code injection', 'rce',
            'remote code execution', 'deserialization', 'buffer overflow'
        ]
        
        # High keywords (serious bugs)
        high_keywords = [
            'hardcoded secret', 'hardcoded password', 'hardcoded key',
            'missing validation', 'no input validation', 'insecure',
            'race condition', 'deadlock', 'memory leak', 'null pointer'
        ]
        
        # Medium keywords (code quality)
        medium_keywords = [
            'complexity', 'duplicate code', 'code smell', 'anti-pattern',
            'poor error handling', 'missing error handling', 'magic number'
        ]
        
        critical_count = sum(1 for kw in critical_keywords if kw in text_lower)
        high_count = sum(1 for kw in high_keywords if kw in text_lower)
        medium_count = sum(1 for kw in medium_keywords if kw in text_lower)
        
        # Total issues detected
        total_issues = critical_count + high_count + medium_count
        low_count = max(0, total_issues - critical_count - high_count - medium_count)
        
        return {
            "CRITICAL": critical_count,
            "HIGH": high_count,
            "MEDIUM": medium_count,
            "LOW": low_count
        }
    
    def _determine_enforcement_action(self, severity_counts: Dict[str, int]) -> str:
        """
        Determine enforcement action based on thresholds.
        
        Returns:
            "block", "warn", "log", or "pass"
        """
        critical = severity_counts.get("CRITICAL", 0)
        high = severity_counts.get("HIGH", 0)
        medium = severity_counts.get("MEDIUM", 0)
        
        # Check thresholds
        if critical > self.thresholds.get("max_critical", 0):
            return "block"
        if high > self.thresholds.get("max_high", 3):
            return "warn"
        if medium > self.thresholds.get("max_medium", 10):
            return "log"
        
        return "pass"
    
    def validate_for_n8n(self, 
                         code: Optional[str] = None,
                         file_path: Optional[str] = None,
                         agent_name: Optional[str] = None,
                         n8n_execution_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate code for n8n workflow.
        
        Args:
            code: Source code string (if provided)
            file_path: Path to file (if provided)
            agent_name: Name of agent requesting validation
            n8n_execution_id: n8n execution ID for tracking
            
        Returns:
            Formatted result for n8n with enforcement decision
        """
        validation_id = str(uuid.uuid4())[:8]
        
        # Validate code
        if file_path:
            result = self.validator.validate_file(file_path)
            filename = Path(file_path).name
        elif code:
            result = self.validator.validate_code(code, filename="inline_code")
            filename = "inline_code"
        else:
            return {
                "success": False,
                "error": "Either code or file_path must be provided",
                "validation_id": validation_id
            }
        
        if not result.get("success"):
            return {
                "success": False,
                "error": result.get("error", "Validation failed"),
                "validation_id": validation_id,
                "n8n_execution_id": n8n_execution_id
            }
        
        # Classify issues by severity
        review_text = result.get("review", "")
        severity_counts = self._classify_issue_severity(review_text)
        
        # Determine enforcement action
        enforcement_action = self._determine_enforcement_action(severity_counts)
        
        # Format result for n8n
        n8n_result = {
            "success": True,
            "validation_id": validation_id,
            "filename": filename,
            "file_path": file_path if file_path else None,
            "agent_name": agent_name,
            "n8n_execution_id": n8n_execution_id,
            "timestamp": datetime.now().isoformat(),
            "model_used": result.get("model", DEFAULT_MODEL),
            "response_time": result.get("response_time", 0),
            "issues_detected": result.get("issues_detected", 0),
            "severity_counts": severity_counts,
            "enforcement_action": enforcement_action,
            "review": review_text,
            "code_hash": result.get("code_hash"),
            "thresholds": self.thresholds,
            "enforcement_levels": self.enforcement_levels
        }
        
        # Optionally log to database if available
        self._log_to_database(n8n_result)
        
        return n8n_result
    
    def _log_to_database(self, validation_result: Dict[str, Any]) -> bool:
        """Log validation result to PostgreSQL database."""
        if not DB_AVAILABLE:
            return False
        
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="aya_rag",
                user="postgres",
                password="Power$$336633$$"
            )
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO code_validations (
                    validation_id, file_path, filename, agent_name,
                    validation_time, model_used, response_time,
                    issues_detected, severity_counts, enforcement_action,
                    review_text, code_hash, n8n_execution_id, success
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                validation_result["validation_id"],
                validation_result.get("file_path"),
                validation_result["filename"],
                validation_result.get("agent_name"),
                datetime.fromisoformat(validation_result["timestamp"]),
                validation_result["model_used"],
                validation_result["response_time"],
                validation_result["issues_detected"],
                json.dumps(validation_result["severity_counts"]),
                validation_result["enforcement_action"],
                validation_result.get("review", "")[:10000],  # Limit review text
                validation_result.get("code_hash"),
                validation_result.get("n8n_execution_id"),
                validation_result["success"]
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            # Silently fail - don't break validation if DB logging fails
            return False
    
    def batch_validate_for_n8n(self,
                                files: List[str],
                                agent_name: Optional[str] = None,
                                n8n_execution_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Batch validate multiple files for n8n.
        
        Args:
            files: List of file paths
            agent_name: Name of agent requesting validation
            n8n_execution_id: n8n execution ID for tracking
            
        Returns:
            Summary with all results
        """
        results = []
        total_critical = 0
        total_high = 0
        total_medium = 0
        
        for file_path in files:
            result = self.validate_for_n8n(
                file_path=file_path,
                agent_name=agent_name,
                n8n_execution_id=n8n_execution_id
            )
            results.append(result)
            
            if result.get("success"):
                severity = result.get("severity_counts", {})
                total_critical += severity.get("CRITICAL", 0)
                total_high += severity.get("HIGH", 0)
                total_medium += severity.get("MEDIUM", 0)
        
        # Determine overall enforcement
        overall_severity = {
            "CRITICAL": total_critical,
            "HIGH": total_high,
            "MEDIUM": total_medium,
            "LOW": 0
        }
        overall_enforcement = self._determine_enforcement_action(overall_severity)
        
        successful = sum(1 for r in results if r.get("success"))
        
        return {
            "success": True,
            "summary": {
                "total_files": len(files),
                "validated": successful,
                "failed": len(files) - successful,
                "total_critical_issues": total_critical,
                "total_high_issues": total_high,
                "total_medium_issues": total_medium,
                "overall_enforcement": overall_enforcement
            },
            "results": results,
            "n8n_execution_id": n8n_execution_id,
            "timestamp": datetime.now().isoformat()
        }


def webhook_handler(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Webhook handler for n8n HTTP requests.
    
    Expected request format:
    {
        "code": "...",  // Optional
        "file_path": "...",  // Optional
        "files": ["..."],  // Optional (for batch)
        "agent_name": "...",  // Optional
        "n8n_execution_id": "..."  // Optional
    }
    
    Returns:
        Validation result formatted for n8n
    """
    validator_n8n = CodeValidatorN8N()
    
    # Check for batch validation
    if "files" in request_data and request_data["files"]:
        return validator_n8n.batch_validate_for_n8n(
            files=request_data["files"],
            agent_name=request_data.get("agent_name"),
            n8n_execution_id=request_data.get("n8n_execution_id")
        )
    
    # Single validation
    return validator_n8n.validate_for_n8n(
        code=request_data.get("code"),
        file_path=request_data.get("file_path"),
        agent_name=request_data.get("agent_name"),
        n8n_execution_id=request_data.get("n8n_execution_id")
    )


if __name__ == "__main__":
    # CLI interface for testing
    import argparse
    
    parser = argparse.ArgumentParser(description='Code Validator n8n Integration')
    parser.add_argument('--file', help='File to validate')
    parser.add_argument('--files', nargs='+', help='Multiple files to validate')
    parser.add_argument('--code', help='Code string to validate')
    parser.add_argument('--agent', default='cli', help='Agent name')
    parser.add_argument('--execution-id', help='n8n execution ID')
    
    args = parser.parse_args()
    
    validator_n8n = CodeValidatorN8N()
    
    if args.files:
        result = validator_n8n.batch_validate_for_n8n(
            files=args.files,
            agent_name=args.agent,
            n8n_execution_id=args.execution_id
        )
    else:
        result = validator_n8n.validate_for_n8n(
            code=args.code,
            file_path=args.file,
            agent_name=args.agent,
            n8n_execution_id=args.execution_id
        )
    
    print(json.dumps(result, indent=2))

