#!/usr/bin/env python3
"""
Claude CLI Executor - Headless Claude Code Execution
Spawns Claude CLI processes in non-interactive mode with JSON output

Prime Directives Compliance:
- Directive #1: FUNCTIONAL REALITY - Real Claude CLI execution, real results
- Directive #11: NO THEATRICAL WRAPPERS - Actual subprocess spawning
"""

import asyncio
import json
import os
import time
from typing import Tuple, Dict, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClaudeExecutor:
    """
    Execute Claude Code CLI in headless mode.
    
    Features:
    - Spawn Claude CLI with --print mode (non-interactive)
    - JSON output parsing
    - Timeout handling
    - Error capture and reporting
    - Resource tracking (execution time)
    """
    
    def __init__(self, claude_path: str = None):
        """
        Initialize Claude executor.
        
        Args:
            claude_path: Path to Claude CLI binary
                        Defaults to standard installation
        """
        self.claude_path = claude_path or os.getenv('CLAUDE_CLI_PATH') or '/Users/arthurdell/.nvm/versions/node/v24.9.0/bin/claude'
        
        # Verify Claude CLI exists
        if not os.path.exists(self.claude_path):
            raise FileNotFoundError(f"Claude CLI not found at {self.claude_path}")
        
        logger.info(f"Claude executor initialized: {self.claude_path}")
    
    async def execute_task(
        self, 
        task_description: str,
        timeout_seconds: int = 300,
        working_directory: Optional[str] = None
    ) -> Tuple[bool, Dict]:
        """
        Execute a task using Claude CLI in headless mode.
        
        Args:
            task_description: Task prompt/description for Claude
            timeout_seconds: Execution timeout (default 300s = 5min)
            working_directory: Optional working directory for execution
        
        Returns:
            Tuple of (success: bool, result: dict)
            
            Success result format:
            {
                'status': 'completed',
                'output': <claude output>,
                'execution_time_ms': <time in milliseconds>,
                'started_at': <ISO timestamp>,
                'completed_at': <ISO timestamp>
            }
            
            Failure result format:
            {
                'status': 'failed',
                'error': <error message>,
                'error_type': <timeout|process_error|parse_error>,
                'execution_time_ms': <time in milliseconds>,
                'stderr': <stderr output if available>
            }
        """
        start_time = time.time()
        started_at = datetime.now().isoformat()
        
        try:
            logger.info(f"Spawning Claude CLI: timeout={timeout_seconds}s")
            logger.debug(f"Task: {task_description[:100]}...")
            
            # Set working directory if specified
            cwd = working_directory or os.getcwd()
            
            # Spawn Claude CLI process
            process = await asyncio.create_subprocess_exec(
                self.claude_path,
                '-p',  # Print mode (non-interactive)
                '--output-format', 'text',  # Text output for MVP
                task_description,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            
            try:
                # Wait for process with timeout
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout_seconds
                )
                
                execution_time_ms = int((time.time() - start_time) * 1000)
                completed_at = datetime.now().isoformat()
                
                # Check return code
                if process.returncode == 0:
                    output_text = stdout.decode('utf-8')
                    
                    logger.info(f"Task completed successfully in {execution_time_ms}ms")
                    
                    return True, {
                        'status': 'completed',
                        'output': output_text,
                        'execution_time_ms': execution_time_ms,
                        'started_at': started_at,
                        'completed_at': completed_at,
                        'return_code': 0
                    }
                else:
                    # Non-zero return code
                    error_output = stderr.decode('utf-8') if stderr else "Unknown error"
                    
                    logger.error(f"Claude CLI failed with return code {process.returncode}")
                    logger.error(f"Error: {error_output[:500]}")
                    
                    return False, {
                        'status': 'failed',
                        'error': f"Claude CLI returned non-zero exit code: {process.returncode}",
                        'error_type': 'process_error',
                        'stderr': error_output,
                        'execution_time_ms': execution_time_ms,
                        'return_code': process.returncode
                    }
            
            except asyncio.TimeoutError:
                # Task exceeded timeout
                execution_time_ms = int((time.time() - start_time) * 1000)
                
                logger.warning(f"Task timeout after {execution_time_ms}ms")
                
                # Kill the process
                try:
                    process.kill()
                    await process.wait()
                except Exception as e:
                    logger.error(f"Error killing process: {e}")
                
                return False, {
                    'status': 'failed',
                    'error': f"Task exceeded timeout of {timeout_seconds}s",
                    'error_type': 'timeout',
                    'execution_time_ms': execution_time_ms,
                    'timeout_seconds': timeout_seconds
                }
        
        except FileNotFoundError as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            logger.error(f"Claude CLI not found: {e}")
            
            return False, {
                'status': 'failed',
                'error': f"Claude CLI not found: {str(e)}",
                'error_type': 'not_found',
                'execution_time_ms': execution_time_ms
            }
        
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            logger.error(f"Unexpected error executing task: {e}")
            
            return False, {
                'status': 'failed',
                'error': str(e),
                'error_type': 'unexpected_error',
                'execution_time_ms': execution_time_ms
            }
    
    def verify_installation(self) -> bool:
        """
        Verify Claude CLI is properly installed and executable.
        
        Returns:
            bool: True if Claude CLI is accessible
        """
        try:
            if not os.path.exists(self.claude_path):
                logger.error(f"Claude CLI not found at {self.claude_path}")
                return False
            
            if not os.access(self.claude_path, os.X_OK):
                logger.error(f"Claude CLI not executable: {self.claude_path}")
                return False
            
            logger.info(f"Claude CLI verified: {self.claude_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error verifying Claude CLI: {e}")
            return False


# Test function for standalone execution
async def test_executor():
    """Test the Claude executor with a simple task"""
    executor = ClaudeExecutor()
    
    # Verify installation
    if not executor.verify_installation():
        print("❌ Claude CLI verification failed")
        return
    
    print("✅ Claude CLI verified")
    
    # Test task
    test_task = "Echo back: 'Hello from parallel execution test'"
    
    print(f"\n🔄 Executing test task...")
    print(f"Task: {test_task}")
    
    success, result = await executor.execute_task(test_task, timeout_seconds=30)
    
    if success:
        print(f"\n✅ Task completed successfully")
        print(f"Execution time: {result['execution_time_ms']}ms")
        print(f"Output:\n{result['output'][:500]}")
    else:
        print(f"\n❌ Task failed")
        print(f"Error: {result['error']}")
        if 'stderr' in result:
            print(f"stderr: {result['stderr'][:500]}")


if __name__ == "__main__":
    print("Claude Executor Test")
    print("=" * 50)
    asyncio.run(test_executor())

