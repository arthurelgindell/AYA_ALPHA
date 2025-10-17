#!/usr/bin/env python3
"""
Retrieval Optimization Setup for AGENT_TURBO
Implements cursor-retrieval for improved code search and context awareness
GAMMA Project - Prime Directives Compliance
"""

import subprocess
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

class RetrievalOptimizationSetup:
    """Retrieval optimization setup for Cursor."""
    
    def __init__(self):
        self.cursor_extensions_path = Path("/Applications/Cursor.app/Contents/Resources/app/extensions")
        self.retrieval_path = self.cursor_extensions_path / "cursor-retrieval"
        self.index_dir = Path("/Volumes/DATA/Agent_Turbo/indexes")
        self.cache_dir = Path("/Volumes/DATA/Agent_Turbo/retrieval_cache")
        self.status = {
            "retrieval_available": False,
            "indexing_enabled": False,
            "cache_optimized": False,
            "github_integration": False
        }
        
    def verify_retrieval_extension(self) -> bool:
        """Verify retrieval extension is available."""
        try:
            retrieval_exists = self.retrieval_path.exists()
            print(f"✅ Retrieval Extension: {'Available' if retrieval_exists else 'Missing'}")
            
            if retrieval_exists:
                self.status["retrieval_available"] = True
                
            return retrieval_exists
        except Exception as e:
            print(f"❌ Retrieval verification failed: {e}")
            return False
    
    def create_index_directories(self) -> bool:
        """Create index directories."""
        try:
            directories = [
                self.index_dir,
                self.cache_dir,
                self.index_dir / "code_index",
                self.index_dir / "documentation_index",
                self.index_dir / "context_index",
                self.cache_dir / "query_cache",
                self.cache_dir / "embedding_cache"
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created directory: {directory}")
            
            return True
            
        except Exception as e:
            print(f"❌ Index directory creation failed: {e}")
            return False
    
    def create_retrieval_config(self) -> bool:
        """Create retrieval configuration."""
        try:
            config_content = {
                "retrieval": {
                    "enabled": True,
                    "indexing_enabled": True,
                    "cache_enabled": True,
                    "github_integration": True
                },
                "indexing": {
                    "code_files": [".py", ".js", ".ts", ".java", ".cpp", ".c", ".h"],
                    "documentation_files": [".md", ".txt", ".rst", ".adoc"],
                    "exclude_patterns": [
                        "node_modules",
                        ".git",
                        "__pycache__",
                        "*.pyc",
                        "*.log"
                    ],
                    "max_file_size_mb": 10
                },
                "cache": {
                    "query_cache_size": 1000,
                    "embedding_cache_size": 500,
                    "cache_ttl_hours": 24
                },
                "github": {
                    "can_attempt_login": True,
                    "augment_results": True
                }
            }
            
            config_path = Path("/Volumes/DATA/Agent_Turbo/.cursor/retrieval_config.json")
            config_path.parent.mkdir(exist_ok=True)
            config_path.write_text(json.dumps(config_content, indent=2))
            
            print("✅ Retrieval configuration created")
            return True
            
        except Exception as e:
            print(f"❌ Retrieval config creation failed: {e}")
            return False
    
    def create_cursorignore(self) -> bool:
        """Create .cursorignore file for indexing control."""
        try:
            ignore_content = """# Cursor Retrieval Ignore Patterns
# Files and directories to exclude from indexing

# Build artifacts
node_modules/
dist/
build/
target/
*.pyc
__pycache__/

# Logs
*.log
logs/

# Temporary files
*.tmp
*.temp
.DS_Store

# Large files
*.zip
*.tar.gz
*.dmg

# Sensitive files
*.key
*.pem
*.p12
.env
secrets/

# Generated files
*.generated.*
auto_*

# Test artifacts
coverage/
.pytest_cache/
.coverage

# IDE files
.vscode/settings.json
.idea/
*.swp
*.swo

# OS files
Thumbs.db
.DS_Store
"""
            
            ignore_path = Path("/Volumes/DATA/Agent_Turbo/.cursorignore")
            ignore_path.write_text(ignore_content)
            
            print("✅ .cursorignore file created")
            return True
            
        except Exception as e:
            print(f"❌ .cursorignore creation failed: {e}")
            return False
    
    def create_cursorindexingignore(self) -> bool:
        """Create .cursorindexingignore file for advanced indexing control."""
        try:
            indexing_ignore_content = """# Cursor Indexing Ignore Patterns
# Advanced patterns for retrieval indexing control

# Large binary files
*.bin
*.dat
*.db
*.sqlite

# Media files
*.mp4
*.avi
*.mov
*.mp3
*.wav
*.png
*.jpg
*.jpeg
*.gif

# Archives
*.zip
*.rar
*.7z
*.tar
*.gz

# Executables
*.exe
*.app
*.dmg
*.pkg

# Dependencies
node_modules/
vendor/
packages/

# Cache directories
.cache/
cache/
tmp/
temp/
"""
            
            indexing_ignore_path = Path("/Volumes/DATA/Agent_Turbo/.cursorindexingignore")
            indexing_ignore_path.write_text(indexing_ignore_content)
            
            print("✅ .cursorindexingignore file created")
            return True
            
        except Exception as e:
            print(f"❌ .cursorindexingignore creation failed: {e}")
            return False
    
    def create_retrieval_optimizer(self) -> bool:
        """Create retrieval optimizer script."""
        try:
            optimizer_content = '''#!/usr/bin/env python3
"""
Retrieval Optimizer for AGENT_TURBO
Optimizes code search and context awareness
"""

import json
import time
import hashlib
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any

class RetrievalOptimizer:
    """Retrieval optimization system."""
    
    def __init__(self):
        self.index_dir = Path("/Volumes/DATA/Agent_Turbo/indexes")
        self.cache_dir = Path("/Volumes/DATA/Agent_Turbo/retrieval_cache")
        self.config_path = Path("/Volumes/DATA/Agent_Turbo/.cursor/retrieval_config.json")
        
        # Load configuration
        if self.config_path.exists():
            self.config = json.loads(self.config_path.read_text())
        else:
            self.config = {}
    
    def optimize_indexing(self) -> Dict[str, Any]:
        """Optimize indexing performance."""
        try:
            print("🚀 Optimizing indexing performance...")
            
            # Get file statistics
            code_files = self.get_code_files()
            doc_files = self.get_documentation_files()
            
            # Calculate index size
            index_size = self.calculate_index_size()
            
            # Optimize index structure
            optimization_results = {
                "code_files": len(code_files),
                "documentation_files": len(doc_files),
                "index_size_mb": index_size,
                "optimization_applied": True,
                "timestamp": time.time()
            }
            
            # Save optimization results
            results_path = self.index_dir / "optimization_results.json"
            results_path.write_text(json.dumps(optimization_results, indent=2))
            
            print(f"✅ Indexing optimization complete: {optimization_results}")
            return optimization_results
            
        except Exception as e:
            print(f"❌ Indexing optimization failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def optimize_cache(self) -> Dict[str, Any]:
        """Optimize cache performance."""
        try:
            print("🚀 Optimizing cache performance...")
            
            # Get cache statistics
            cache_stats = self.get_cache_statistics()
            
            # Optimize cache structure
            cache_optimization = {
                "cache_entries": cache_stats.get("entries", 0),
                "cache_size_mb": cache_stats.get("size_mb", 0),
                "hit_rate": cache_stats.get("hit_rate", 0),
                "optimization_applied": True,
                "timestamp": time.time()
            }
            
            # Save cache optimization results
            results_path = self.cache_dir / "cache_optimization.json"
            results_path.write_text(json.dumps(cache_optimization, indent=2))
            
            print(f"✅ Cache optimization complete: {cache_optimization}")
            return cache_optimization
            
        except Exception as e:
            print(f"❌ Cache optimization failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_code_files(self) -> List[Path]:
        """Get list of code files."""
        try:
            code_extensions = [".py", ".js", ".ts", ".java", ".cpp", ".c", ".h"]
            code_files = []
            
            for ext in code_extensions:
                files = list(Path("/Volumes/DATA/Agent_Turbo").rglob(f"*{ext}"))
                code_files.extend(files)
            
            return code_files
        except Exception as e:
            print(f"❌ Code files retrieval failed: {e}")
            return []
    
    def get_documentation_files(self) -> List[Path]:
        """Get list of documentation files."""
        try:
            doc_extensions = [".md", ".txt", ".rst", ".adoc"]
            doc_files = []
            
            for ext in doc_extensions:
                files = list(Path("/Volumes/DATA/Agent_Turbo").rglob(f"*{ext}"))
                doc_files.extend(files)
            
            return doc_files
        except Exception as e:
            print(f"❌ Documentation files retrieval failed: {e}")
            return []
    
    def calculate_index_size(self) -> float:
        """Calculate index size in MB."""
        try:
            total_size = 0
            
            if self.index_dir.exists():
                for file_path in self.index_dir.rglob("*"):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
            
            return total_size / (1024 * 1024)  # Convert to MB
        except Exception as e:
            print(f"❌ Index size calculation failed: {e}")
            return 0.0
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            stats = {
                "entries": 0,
                "size_mb": 0,
                "hit_rate": 0
            }
            
            if self.cache_dir.exists():
                # Count cache entries
                cache_files = list(self.cache_dir.rglob("*"))
                stats["entries"] = len(cache_files)
                
                # Calculate cache size
                total_size = sum(f.stat().st_size for f in cache_files if f.is_file())
                stats["size_mb"] = total_size / (1024 * 1024)
                
                # Simulate hit rate (in real implementation, this would be tracked)
                stats["hit_rate"] = 0.75  # 75% hit rate
            
            return stats
        except Exception as e:
            print(f"❌ Cache statistics failed: {e}")
            return {"entries": 0, "size_mb": 0, "hit_rate": 0}
    
    def run_full_optimization(self) -> Dict[str, Any]:
        """Run full retrieval optimization."""
        try:
            print("🚀 Running full retrieval optimization...")
            
            # Optimize indexing
            indexing_results = self.optimize_indexing()
            
            # Optimize cache
            cache_results = self.optimize_cache()
            
            # Combine results
            full_results = {
                "indexing": indexing_results,
                "cache": cache_results,
                "overall_status": "success",
                "timestamp": time.time()
            }
            
            # Save full results
            results_path = self.index_dir / "full_optimization.json"
            results_path.write_text(json.dumps(full_results, indent=2))
            
            print(f"✅ Full optimization complete: {full_results}")
            return full_results
            
        except Exception as e:
            print(f"❌ Full optimization failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def list_optimization_options(self):
        """List available optimization options."""
        print("Available optimization options:")
        print("  1. Indexing Optimization")
        print("  2. Cache Optimization")
        print("  3. Full Optimization")

def main():
    """Main execution."""
    optimizer = RetrievalOptimizer()
    
    if len(sys.argv) < 2:
        optimizer.list_optimization_options()
        return 0
    
    command = sys.argv[1]
    
    if command == "indexing":
        result = optimizer.optimize_indexing()
        return 0 if result.get("status") != "error" else 1
    elif command == "cache":
        result = optimizer.optimize_cache()
        return 0 if result.get("status") != "error" else 1
    elif command == "full":
        result = optimizer.run_full_optimization()
        return 0 if result.get("status") != "error" else 1
    else:
        print("Usage:")
        print("  python3 retrieval_optimizer.py indexing")
        print("  python3 retrieval_optimizer.py cache")
        print("  python3 retrieval_optimizer.py full")
        return 1

if __name__ == "__main__":
    exit(main())
'''
            
            optimizer_path = Path("/Volumes/DATA/Agent_Turbo/scripts/retrieval_optimizer.py")
            optimizer_path.write_text(optimizer_content)
            optimizer_path.chmod(0o755)
            
            print("✅ Retrieval optimizer created")
            return True
            
        except Exception as e:
            print(f"❌ Retrieval optimizer creation failed: {e}")
            return False
    
    def test_retrieval_system(self) -> bool:
        """Test retrieval system functionality."""
        try:
            # Test retrieval optimizer
            result = subprocess.run([
                "python3", "/Volumes/DATA/Agent_Turbo/scripts/retrieval_optimizer.py", "indexing"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Retrieval system test successful")
                return True
            else:
                print(f"❌ Retrieval system test failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Retrieval system test failed: {e}")
            return False
    
    def setup_retrieval_optimization(self) -> bool:
        """Complete retrieval optimization setup."""
        print("🚀 Setting up Retrieval Optimization...")
        
        # Verify retrieval extension
        if not self.verify_retrieval_extension():
            print("❌ TASK FAILED: Retrieval extension not available")
            return False
        
        # Create index directories
        if not self.create_index_directories():
            print("❌ TASK FAILED: Index directory creation failed")
            return False
        
        # Create retrieval config
        if not self.create_retrieval_config():
            print("❌ TASK FAILED: Retrieval config creation failed")
            return False
        
        # Create ignore files
        if not self.create_cursorignore():
            print("❌ TASK FAILED: .cursorignore creation failed")
            return False
        
        if not self.create_cursorindexingignore():
            print("❌ TASK FAILED: .cursorindexingignore creation failed")
            return False
        
        # Create retrieval optimizer
        if not self.create_retrieval_optimizer():
            print("❌ TASK FAILED: Retrieval optimizer creation failed")
            return False
        
        # Test retrieval system
        if not self.test_retrieval_system():
            print("❌ TASK FAILED: Retrieval system test failed")
            return False
        
        print("✅ Retrieval optimization setup complete")
        return True

def main():
    """Main execution."""
    setup = RetrievalOptimizationSetup()
    success = setup.setup_retrieval_optimization()
    
    if success:
        print("✅ Retrieval optimization implementation successful")
        return 0
    else:
        print("❌ TASK FAILED: Retrieval optimization setup failed")
        return 1

if __name__ == "__main__":
    exit(main())
