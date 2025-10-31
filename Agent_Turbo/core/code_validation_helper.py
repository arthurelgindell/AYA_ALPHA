#!/usr/bin/env python3
"""
Code Validation Helper for Agent Turbo
Integrates automated code validation with Agent Turbo workflows

Author: Claude for Arthur
Date: October 29, 2025
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Optional, Any
import requests

# Try to import n8n validator
try:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from services.code_validator_n8n import CodeValidatorN8N, webhook_handler
    N8N_VALIDATOR_AVAILABLE = True
except ImportError:
    N8N_VALIDATOR_AVAILABLE = False

# Try to import local validator
try:
    from code_validator import CodeValidator
    LOCAL_VALIDATOR_AVAILABLE = True
except ImportError:
    LOCAL_VALIDATOR_AVAILABLE = False


class CodeValidationHelper:
    """
    Helper class for Agent Turbo to validate code before writing.
    
    Automatically uses n8n endpoint if available, falls back to local validator.
    """
    
    def __init__(self, agent_name: str = "agent_turbo"):
        """Initialize validation helper."""
        self.agent_name = agent_name
        self.n8n_endpoint = os.getenv(
            "CODE_VALIDATION_ENDPOINT",
            "http://alpha.tail5f2bae.ts.net:5678/webhook/code-validate"
        )
        self.use_n8n = os.getenv("CODE_VALIDATION_REQUIRED", "true").lower() == "true"
        self.enforce = os.getenv("CODE_VALIDATION_ENFORCE", "true").lower() == "true"
        
        # Initialize validators
        self.n8n_validator = None
        self.local_validator = None
        
        if N8N_VALIDATOR_AVAILABLE:
            try:
                self.n8n_validator = CodeValidatorN8N()
            except Exception as e:
                print(f"⚠️  N8N validator unavailable: {e}")
        
        if LOCAL_VALIDATOR_AVAILABLE:
            try:
                self.local_validator = CodeValidator(model_preference="mlx")
            except Exception as e:
                print(f"⚠️  Local validator unavailable: {e}")
    
    def validate_code(self, code: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate code using available validator.
        
        Args:
            code: Source code to validate
            file_path: Optional file path for context
            
        Returns:
            Validation result with enforcement decision
        """
        if not self.use_n8n:
            return {
                "success": True,
                "enforcement_action": "pass",
                "message": "Code validation disabled"
            }
        
        # Try n8n endpoint first
        if self.n8n_endpoint and self.n8n_endpoint.startswith("http"):
            try:
                response = requests.post(
                    self.n8n_endpoint,
                    json={
                        "code": code,
                        "file_path": file_path,
                        "agent_name": self.agent_name
                    },
                    timeout=30,
                    verify=False  # Tailscale self-signed cert
                )
                
                if response.status_code == 200:
                    return response.json()
            except Exception as e:
                print(f"⚠️  N8N endpoint failed: {e}, trying local validator")
        
        # Fallback to local validator
        if self.n8n_validator:
            return self.n8n_validator.validate_for_n8n(
                code=code,
                file_path=file_path,
                agent_name=self.agent_name
            )
        
        if self.local_validator:
            result = self.local_validator.validate_code(code, filename=Path(file_path).name if file_path else "code.py")
            # Convert to n8n format
            return {
                "success": result.get("success", False),
                "enforcement_action": "pass" if result.get("success") else "warn",
                "review": result.get("review", ""),
                "issues_detected": result.get("issues_detected", 0),
                "message": "Validated with local validator"
            }
        
        # No validator available
        return {
            "success": False,
            "enforcement_action": "warn",
            "error": "No validator available",
            "message": "Validation skipped - no validator configured"
        }
    
    def validate_and_write(self, file_path: str, code: str, force: bool = False) -> Dict[str, Any]:
        """
        Validate code and write if validation passes.
        
        Args:
            file_path: Path to write file
            code: Source code to validate and write
            force: Skip validation if True
            
        Returns:
            Dict with success status and validation results
        
        Raises:
            CodeQualityError: If validation fails and enforcement is enabled
        """
        if force or not self.use_n8n:
            # Write without validation
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(code)
            return {
                "success": True,
                "written": True,
                "validation": {"enforcement_action": "skipped"}
            }
        
        # Validate first
        validation = self.validate_code(code, file_path)
        
        if not validation.get("success"):
            if self.enforce:
                raise CodeQualityError(
                    f"Code validation failed: {validation.get('error', 'Unknown error')}",
                    validation
                )
            print(f"⚠️  Validation failed but writing anyway: {validation.get('error')}")
        
        enforcement = validation.get("enforcement_action", "pass")
        
        if enforcement == "block" and self.enforce:
            raise CodeQualityError(
                f"Code validation blocked write to {file_path}. Critical issues found.",
                validation
            )
        
        # Write file
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(code)
        
        return {
            "success": True,
            "written": True,
            "validation": validation
        }


class CodeQualityError(Exception):
    """Exception raised when code validation fails."""
    
    def __init__(self, message: str, validation_result: Optional[Dict] = None):
        super().__init__(message)
        self.validation_result = validation_result


# Convenience function for Agent Turbo
def validate_code(code: str, file_path: Optional[str] = None, agent_name: str = "agent_turbo") -> Dict[str, Any]:
    """Quick validation function for Agent Turbo."""
    helper = CodeValidationHelper(agent_name=agent_name)
    return helper.validate_code(code, file_path)


def validate_and_write(file_path: str, code: str, agent_name: str = "agent_turbo", force: bool = False) -> Dict[str, Any]:
    """Quick validate-and-write function for Agent Turbo."""
    helper = CodeValidationHelper(agent_name=agent_name)
    return helper.validate_and_write(file_path, code, force=force)

