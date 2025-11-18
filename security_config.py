"""
Security Configuration for Code Interceptor + Agentic Sandbox
Centralized configuration for security policies and limits
"""

import os
from typing import Dict, List


class SecurityConfig:
    """Configuration class for security settings"""
    
    # Resource Limits
    MAX_EXECUTION_TIME = int(os.getenv("MAX_EXECUTION_TIME", "30"))
    MAX_MEMORY_MB = int(os.getenv("MAX_MEMORY_MB", "256"))
    MAX_OUTPUT_SIZE = int(os.getenv("MAX_OUTPUT_SIZE", "8192"))
    MAX_CODE_SIZE = int(os.getenv("MAX_CODE_SIZE", "10000"))  # bytes
    MAX_LINES = int(os.getenv("MAX_LINES", "1000"))
    
    # Sandbox Configuration
    SANDBOX_DIR = os.getenv("SANDBOX_DIR", "/tmp/code_sandbox")
    CLEANUP_TIMEOUT = int(os.getenv("CLEANUP_TIMEOUT", "5"))  # seconds
    
    # Security Patterns
    DANGEROUS_PATTERNS = [
        # File system operations
        r"/dev/[a-zA-Z]+",
        r"/proc",
        r"/sys",
        r"/etc/passwd",
        r"/etc/shadow",
        r"mkfs",
        r"mount",
        r"umount",
        r"rm\s+-rf",
        r"chmod\s+[467][0-7][0-7]",
        r"chown",
        
        # Network operations
        r"nc\s",
        r"netcat",
        r"telnet",
        r"ssh",
        r"curl",
        r"wget",
        r"fetch",
        r"requests",
        r"socket\.connect",
        r"http\.request",
        r"urllib",
        r"httplib",
        
        # System operations
        r"reboot",
        r"shutdown",
        r"halt",
        r"killall",
        r"pkill",
        r"kill\s+-",
        r"ps\s+aux",
        
        # Privilege escalation
        r"sudo",
        r"su\s",
        r"setuid",
        r"setgid",
        
        # Code injection
        r"eval\(",
        r"exec\(",
        r"os\.system",
        r"subprocess\.call",
        r"subprocess\.Popen",
        r"subprocess\.run",
        
        # Cryptographic operations (weak algorithms)
        r"hashlib\.md5",
        r"hashlib\.sha1",
        r"cryptography\.hazmat\.primitives\.hashes\.MD5",
        r"cryptography\.hazmat\.primitives\.hashes\.SHA1",
        
        # Database operations
        r"sqlite3?",
        r"psycopg2",
        r"mysql",
        r"pymongo",
        r"redis",
        
        # Process spawning
        r"fork",
        r"spawn",
        r"multiprocessing",
        r"threading",
        
        # File operations (dangerous paths)
        r"open\s*\(\s*['\"]\/",
        r"open\s*\(\s*['\"][a-zA-Z]+\/",
        
        # Dynamic imports
        r"__import__",
        r"importlib",
        
        # JavaScript specific
        r"eval\s*\(",
        r"Function\s*\(",
        r"setTimeout\s*\(",
        r"setInterval\s*\(",
        r"document\.write",
        r"innerHTML",
        
        # System information leakage
        r"os\.environ",
        r"process\.env",
        r"__file__",
        r"__dirname",
    ]
    
    # Language-specific security rules
    LANGUAGE_SECURITY_RULES = {
        "python": {
            "dangerous_imports": ["os", "sys", "subprocess", "multiprocessing", "threading"],
            "dangerous_functions": ["eval", "exec", "compile", "open", "__import__"],
            "max_imports": 10,
            "max_function_calls": 100
        },
        "javascript": {
            "dangerous_apis": ["eval", "Function", "setTimeout", "setInterval", "fetch", "XMLHttpRequest"],
            "dangerous_dom": ["document.write", "innerHTML", "outerHTML"],
            "max_functions": 50,
            "max_variables": 100
        },
        "bash": {
            "dangerous_commands": ["rm", "rmdir", "mv", "cp", "chmod", "chown", "sudo", "su"],
            "dangerous_paths": ["/etc/", "/proc/", "/sys/", "/dev/"],
            "max_commands": 50
        },
        "cpp": {
            "dangerous_includes": ["filesystem", "fstream", "ifstream", "ofstream"],
            "dangerous_functions": ["system", "popen", "execl", "execv"],
            "max_includes": 20,
            "max_functions": 100
        },
        "rust": {
            "dangerous_crates": ["std::process", "std::fs", "std::io"],
            "unsafe_blocks": False,  # Disallow unsafe blocks
            "max_crates": 10,
            "max_functions": 100
        }
    }
    
    # Complexity limits
    COMPLEXITY_LIMITS = {
        "python": {
            "max_functions": 20,
            "max_classes": 10,
            "max_nesting_depth": 5,
            "max_variables_per_scope": 20
        },
        "javascript": {
            "max_functions": 20,
            "max_classes": 10,
            "max_nesting_depth": 5,
            "max_variables": 50
        },
        "bash": {
            "max_functions": 10,
            "max_nesting_depth": 3,
            "max_variables": 30
        },
        "cpp": {
            "max_functions": 30,
            "max_classes": 15,
            "max_nesting_depth": 4,
            "max_includes": 20
        },
        "rust": {
            "max_functions": 25,
            "max_structs": 15,
            "max_traits": 10,
            "max_nesting_depth": 4
        }
    }
    
    # Allowed file extensions and their safety levels
    SAFE_EXTENSIONS = {
        ".py": {"language": "python", "compile": False, "timeout_multiplier": 1.0},
        ".js": {"language": "javascript", "compile": False, "timeout_multiplier": 1.0},
        ".sh": {"language": "bash", "compile": False, "timeout_multiplier": 1.0},
        ".cpp": {"language": "cpp", "compile": True, "timeout_multiplier": 2.0},
        ".c": {"language": "cpp", "compile": True, "timeout_multiplier": 2.0},
        ".rs": {"language": "rust", "compile": True, "timeout_multiplier": 2.0},
        ".go": {"language": "go", "compile": True, "timeout_multiplier": 2.0},
        ".java": {"language": "java", "compile": True, "timeout_multiplier": 3.0}
    }
    
    # Security scanning rules
    SCANNING_CONFIG = {
        "enable_ast_analysis": True,
        "enable_pattern_matching": True,
        "enable_complexity_analysis": True,
        "enable_import_analysis": True,
        "severity_levels": {
            "critical": ["eval", "exec", "system", "rm -rf"],
            "high": ["sudo", "chmod", "chown", "fork"],
            "medium": ["open", "import", "require"],
            "low": ["print", "console.log", "echo"]
        }
    }
    
    # Execution environment restrictions
    ENVIRONMENT_RESTRICTIONS = {
        "network_enabled": False,
        "filesystem_access": "sandbox_only",
        "environment_variables": {
            "PATH": "/usr/bin:/bin",
            "HOME": "/tmp",
            "USER": "nobody",
            "SHELL": "/bin/bash"
        },
        "disabled_syscalls": [
            # Add system calls to disable if using seccomp
            "personality", "ptrace", "process_vm_readv", "process_vm_writev"
        ]
    }
    
    # Rate limiting
    RATE_LIMITS = {
        "requests_per_minute": 60,
        "requests_per_hour": 1000,
        "concurrent_executions": 5,
        "code_execution_quota": 100  # per user per day
    }
    
    # Audit and logging
    AUDIT_CONFIG = {
        "log_executions": True,
        "log_security_violations": True,
        "log_performance_metrics": True,
        "retention_days": 30,
        "sanitize_logs": True,  # Remove sensitive data from logs
        "log_levels": ["INFO", "WARNING", "ERROR", "SECURITY"]
    }
    
    @classmethod
    def get_language_config(cls, language: str) -> Dict:
        """Get configuration for specific language"""
        return cls.LANGUAGE_SECURITY_RULES.get(language, {})
    
    @classmethod
    def get_complexity_limits(cls, language: str) -> Dict:
        """Get complexity limits for specific language"""
        return cls.COMPLEXITY_LIMITS.get(language, {})
    
    @classmethod
    def is_safe_extension(cls, extension: str) -> bool:
        """Check if file extension is allowed"""
        return extension in cls.SAFE_EXTENSIONS
    
    @classmethod
    def get_security_severity(cls, violation_pattern: str) -> str:
        """Determine severity level of security violation"""
        for severity, patterns in cls.SCANNING_CONFIG["severity_levels"].items():
            for pattern in patterns:
                if pattern in violation_pattern.lower():
                    return severity
        return "medium"  # Default severity
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """Validate configuration and return warnings"""
        warnings = []
        
        # Check resource limits
        if cls.MAX_EXECUTION_TIME > 60:
            warnings.append("High execution time limit may impact performance")
        
        if cls.MAX_MEMORY_MB > 512:
            warnings.append("High memory limit may impact system stability")
        
        if cls.MAX_OUTPUT_SIZE > 16384:
            warnings.append("Large output size may impact performance")
        
        # Check sandbox directory
        if not cls.SANDBOX_DIR.startswith("/tmp/"):
            warnings.append("Sandbox directory should be in /tmp/ for security")
        
        return warnings


# Export configuration for easy import
CONFIG = SecurityConfig()

# Validation on import
WARNINGS = CONFIG.validate_config()
if WARNINGS:
    print("Security Configuration Warnings:")
    for warning in WARNINGS:
        print(f"  ⚠️  {warning}")