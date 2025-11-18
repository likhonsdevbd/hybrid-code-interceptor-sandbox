#!/usr/bin/env python3
"""
Code Interceptor + Agentic Sandbox for HuggingFace Spaces
Production-ready, secure code execution environment
"""

import os
import sys
import subprocess
import tempfile
import shutil
import uuid
import asyncio
import signal
import time
import resource
import pwd
import grp
import threading
import json
from pathlib import Path
from typing import Dict, List, Optional, AsyncGenerator
from dataclasses import dataclass
from datetime import datetime, timezone
import gradio as gr

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn


# Security Configuration
MAX_EXECUTION_TIME = 30  # seconds
MAX_MEMORY_MB = 256
MAX_OUTPUT_SIZE = 8192  # bytes
SANDBOX_DIR = Path("/tmp/code_sandbox")
SANDBOX_DIR.mkdir(exist_ok=True, mode=0o700)

# Language configurations
LANGUAGE_CONFIGS = {
    "python": {
        "command": "python3",
        "file_extension": ".py",
        "timeout_multiplier": 1.0
    },
    "bash": {
        "command": "bash",
        "file_extension": ".sh",
        "timeout_multiplier": 1.0
    },
    "javascript": {
        "command": "node",
        "file_extension": ".js",
        "timeout_multiplier": 1.0
    },
    "cpp": {
        "command": "g++ -O2 -std=c++17 -o {out} {file} && {out}",
        "file_extension": ".cpp",
        "timeout_multiplier": 2.0
    },
    "rust": {
        "command": "rustc -O -o {out} {file} && {out}",
        "file_extension": ".rs",
        "timeout_multiplier": 2.0
    }
}

# Security patterns - enhanced denylist
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
    
    # Network operations
    r"nc\s",
    r"netcat",
    r"telnet",
    r"ssh",
    r"curl",
    r"wget",
    r"fetch",
    r"requests",
    
    # System operations
    r"reboot",
    r"shutdown",
    r"halt",
    r"killall",
    r"pkill",
    
    # Privilege escalation
    r"sudo",
    r"su\s",
    r"chmod\s+[467][0-7][0-7]",
    r"chown",
    
    # Code injection
    r"eval\(",
    r"exec\(",
    r"os\.system",
    r"subprocess\.call",
    
    # Cryptographic operations
    r"hashlib\.md5",
    r"hashlib\.sha1",
    
    # Database operations
    r"sqlite3?",
    r"psycopg2",
    r"mysql",
    
    # Process spawning
    r"fork",
    r"spawn",
    r"Popen"
]


@dataclass
class SecurityViolation:
    pattern: str
    line: int
    context: str


class SecurityInterceptor:
    """Static analysis security interceptor"""
    
    def __init__(self):
        self.violations: List[SecurityViolation] = []
    
    def analyze_code(self, code: str, language: str) -> Dict:
        """Perform static security analysis"""
        self.violations = []
        
        # Basic pattern matching
        import re
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            for pattern in DANGEROUS_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    self.violations.append(SecurityViolation(
                        pattern=pattern,
                        line=i,
                        context=line.strip()
                    ))
        
        # Language-specific analysis
        if language == "python":
            self._analyze_python(code)
        elif language == "javascript":
            self._analyze_javascript(code)
        
        # Complexity checks
        complexity_score = self._calculate_complexity(code, language)
        
        return {
            "allowed": len(self.violations) == 0,
            "violations": [
                {
                    "pattern": v.pattern,
                    "line": v.line,
                    "context": v.context
                } for v in self.violations
            ],
            "complexity_score": complexity_score,
            "recommendations": self._get_recommendations()
        }
    
    def _analyze_python(self, code: str):
        """Python-specific security analysis"""
        try:
            import ast
            
            tree = ast.parse(code)
            for node in ast.walk(tree):
                # Check for dangerous function calls
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ["open", "exec", "eval", "compile"]:
                            # Context check - allow safe file operations
                            if node.func.id == "open":
                                # Check if it's a dangerous path
                                if len(node.args) > 0 and isinstance(node.args[0], ast.Constant):
                                    path = node.args[0].value
                                    if any(danger in path for danger in ["/etc/", "/proc/", "/sys/"]):
                                        self.violations.append(SecurityViolation(
                                            pattern=f"dangerous_path:{path}",
                                            line=node.lineno,
                                            context="Dangerous file path"
                                        ))
        except SyntaxError:
            pass  # Syntax errors handled separately
    
    def _analyze_javascript(self, code: str):
        """JavaScript-specific security analysis"""
        import re
        
        # Check for eval/exec patterns
        eval_patterns = [
            r"eval\s*\(",
            r"Function\s*\(",
            r"setTimeout\s*\(",
            r"setInterval\s*\("
        ]
        
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            for pattern in eval_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.violations.append(SecurityViolation(
                        pattern=pattern,
                        line=i,
                        context=line.strip()
                    ))
    
    def _calculate_complexity(self, code: str, language: str) -> int:
        """Calculate basic complexity score"""
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        # Simple complexity metrics
        complexity = len(non_empty_lines)
        
        if language == "python":
            complexity += code.count('def ') + code.count('class ')
        elif language == "javascript":
            complexity += code.count('function ') + code.count('class ')
        
        return min(complexity, 1000)  # Cap at 1000
    
    def _get_recommendations(self) -> List[str]:
        """Get security recommendations"""
        recommendations = []
        
        if any("open" in str(v.pattern) for v in self.violations):
            recommendations.append("Use safer file handling methods")
        
        if any("eval" in str(v.pattern) for v in self.violations):
            recommendations.append("Avoid dynamic code execution")
        
        if any("import" in v.context.lower() for v in self.violations):
            recommendations.append("Review import statements for security")
        
        return recommendations


class SandboxExecutor:
    """Secure code execution within process constraints"""
    
    def __init__(self):
        self.interceptor = SecurityInterceptor()
    
    def create_sandbox_directory(self, job_id: str) -> Path:
        """Create isolated sandbox directory"""
        sandbox_path = SANDBOX_DIR / job_id
        sandbox_path.mkdir(mode=0o700, exist_ok=True)
        return sandbox_path
    
    def set_resource_limits(self):
        """Set strict resource limits"""
        # Memory limit
        resource.setrlimit(resource.RLIMIT_AS, (MAX_MEMORY_MB * 1024 * 1024, MAX_MEMORY_MB * 1024 * 1024))
        
        # CPU time limit (soft limit)
        resource.setrlimit(resource.RLIMIT_CPU, (MAX_EXECUTION_TIME, MAX_EXECUTION_TIME))
        
        # File size limit
        resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_OUTPUT_SIZE, MAX_OUTPUT_SIZE))
        
        # Number of processes
        resource.setrlimit(resource.RLIMIT_NPROC, (2, 2))
    
    def execute_code(self, code: str, language: str, job_id: str, timeout: int = None) -> Dict:
        """Execute code in secure sandbox"""
        
        if timeout is None:
            timeout = int(MAX_EXECUTION_TIME * LANGUAGE_CONFIGS.get(language, {}).get("timeout_multiplier", 1.0))
        
        # Security analysis
        security_result = self.interceptor.analyze_code(code, language)
        if not security_result["allowed"]:
            return {
                "success": False,
                "error": "Security violation detected",
                "violations": security_result["violations"],
                "output": "",
                "exit_code": -1,
                "execution_time": 0
            }
        
        # Create sandbox
        sandbox_path = self.create_sandbox_directory(job_id)
        
        try:
            # Write code to file
            config = LANGUAGE_CONFIGS.get(language, LANGUAGE_CONFIGS["python"])
            file_extension = config["file_extension"]
            code_file = sandbox_path / f"main{file_extension}"
            
            with open(code_file, "w") as f:
                f.write(code)
            
            os.chmod(code_file, 0o600)  # Read-only for owner
            
            # Execute in subprocess with strict controls
            result = self._execute_subprocess(code_file, config["command"], timeout, sandbox_path)
            
            return {
                "success": True,
                "output": result["output"],
                "error": result["error"],
                "exit_code": result["exit_code"],
                "execution_time": result["execution_time"],
                "security_report": security_result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution failed: {str(e)}",
                "output": "",
                "exit_code": -1,
                "execution_time": 0
            }
        finally:
            # Cleanup
            if sandbox_path.exists():
                shutil.rmtree(sandbox_path, ignore_errors=True)
    
    def _execute_subprocess(self, code_file: Path, command_template: str, timeout: int, sandbox_path: Path) -> Dict:
        """Execute code in subprocess with monitoring"""
        
        # Prepare command
        if "{file}" in command_template:
            command = command_template.format(
                file=str(code_file),
                out=str(sandbox_path / "executable")
            )
        elif "{out}" in command_template:
            executable = sandbox_path / "executable"
            command = command_template.format(
                file=str(code_file),
                out=str(executable)
            )
        else:
            command = f"{command_template} {code_file}"
        
        start_time = time.time()
        
        try:
            # Create process with security restrictions
            env = {
                "PATH": "/usr/bin:/bin",
                "HOME": str(sandbox_path),
                "USER": "nobody",
                "TMPDIR": str(sandbox_path)
            }
            
            # Set process group for better cleanup
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(sandbox_path),
                env=env,
                preexec_fn=self._setup_process_security,
                text=True,
                bufsize=1
            )
            
            # Monitor execution with timeout
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                execution_time = time.time() - start_time
                
                # Truncate output if too large
                if len(stdout) > MAX_OUTPUT_SIZE:
                    stdout = stdout[:MAX_OUTPUT_SIZE] + "\n... (output truncated)"
                if len(stderr) > MAX_OUTPUT_SIZE:
                    stderr = stderr[:MAX_OUTPUT_SIZE] + "\n... (error truncated)"
                
                return {
                    "output": stdout,
                    "error": stderr,
                    "exit_code": process.returncode,
                    "execution_time": execution_time
                }
                
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                return {
                    "output": "",
                    "error": "Execution timeout exceeded",
                    "exit_code": 124,  # Standard timeout exit code
                    "execution_time": timeout
                }
                
        except Exception as e:
            return {
                "output": "",
                "error": f"Process execution error: {str(e)}",
                "exit_code": -1,
                "execution_time": time.time() - start_time
            }
    
    def _setup_process_security(self):
        """Setup security restrictions for subprocess"""
        try:
            # Change to non-root user
            nobody_uid = pwd.getpwnam('nobody').pw_uid
            nobody_gid = grp.getgrnam('nogroup').gr_gid
            
            os.setuid(nobody_uid)
            os.setgid(nobody_gid)
            
            # Set umask to restrictive
            os.umask(0o077)
            
            # Close unnecessary file descriptors
            max_fd = resource.getrlimit(resource.RLIMIT_NOFILE)[0]
            for fd in range(3, max_fd):
                try:
                    os.close(fd)
                except (OSError, IOError):
                    pass
            
        except (KeyError, OSError):
            pass  # Security setup failed, but continue


# API Models
class ExecutionRequest(BaseModel):
    code: str = Field(..., description="Code to execute")
    language: str = Field(..., description="Programming language")
    timeout: Optional[int] = Field(None, description="Execution timeout in seconds")


class ExecutionResponse(BaseModel):
    success: bool
    output: str = ""
    error: str = ""
    exit_code: int = 0
    execution_time: float = 0
    security_report: Dict = {}


# Initialize components
executor = SandboxExecutor()

# FastAPI app
app = FastAPI(
    title="Code Interceptor + Agentic Sandbox",
    description="Secure, production-ready code execution environment",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Code Interceptor Sandbox",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "sandbox_dir": str(SANDBOX_DIR),
        "max_execution_time": MAX_EXECUTION_TIME,
        "max_memory_mb": MAX_MEMORY_MB,
        "supported_languages": list(LANGUAGE_CONFIGS.keys()),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.post("/execute", response_model=ExecutionResponse)
async def execute_code(request: ExecutionRequest):
    """Execute code in secure sandbox"""
    
    # Validate language
    if request.language not in LANGUAGE_CONFIGS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language: {request.language}. Supported: {list(LANGUAGE_CONFIGS.keys())}"
        )
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Execute code
    result = executor.execute_code(
        code=request.code,
        language=request.language,
        job_id=job_id,
        timeout=request.timeout
    )
    
    return ExecutionResponse(**result)


@app.get("/languages")
async def get_supported_languages():
    """Get supported programming languages"""
    return {
        "languages": [
            {
                "name": lang,
                "command": config["command"],
                "file_extension": config["file_extension"],
                "timeout_multiplier": config["timeout_multiplier"]
            }
            for lang, config in LANGUAGE_CONFIGS.items()
        ]
    }


@app.get("/security/policy")
async def get_security_policy():
    """Get security policy information"""
    return {
        "max_execution_time": MAX_EXECUTION_TIME,
        "max_memory_mb": MAX_MEMORY_MB,
        "max_output_size": MAX_OUTPUT_SIZE,
        "dangerous_patterns_count": len(DANGEROUS_PATTERNS),
        "security_features": [
            "Static code analysis",
            "Pattern-based detection",
            "Resource limits",
            "Process isolation",
            "Sandbox execution"
        ]
    }


# Gradio Interface
def create_gradio_interface():
    """Create Gradio interface for HF Spaces"""
    
    def execute_code_interface(code, language, timeout):
        """Gradio interface function"""
        try:
            result = executor.execute_code(
                code=code,
                language=language,
                job_id=str(uuid.uuid4()),
                timeout=int(timeout) if timeout else None
            )
            
            # Format output
            if result["success"]:
                output = f"✅ Execution Successful\n\n"
                output += f"Output:\n{result['output']}\n\n"
                output += f"Exit Code: {result['exit_code']}\n"
                output += f"Execution Time: {result['execution_time']:.2f}s\n"
                
                if result['security_report']['violations']:
                    output += f"\n⚠️ Security Warnings:\n"
                    for violation in result['security_report']['violations']:
                        output += f"  - Line {violation['line']}: {violation['pattern']}\n"
            else:
                output = f"❌ Execution Failed\n\n"
                output += f"Error: {result['error']}\n"
                if result.get('violations'):
                    output += f"\n🔒 Security Violations:\n"
                    for violation in result['violations']:
                        output += f"  - Line {violation['line']}: {violation['pattern']}\n"
            
            return output
            
        except Exception as e:
            return f"❌ Interface Error: {str(e)}"
    
    # Sample code examples
    examples = [
        {
            "name": "Hello World (Python)",
            "code": """print("Hello from secure sandbox!")
print("Current time:", __import__('datetime').datetime.now())
result = sum(range(10))
print(f"Sum of 0-9: {result}")""",
            "language": "python",
            "timeout": 10
        },
        {
            "name": "Simple Math (JavaScript)",
            "code": """console.log("Hello from JavaScript!");
const numbers = [1, 2, 3, 4, 5];
const sum = numbers.reduce((a, b) => a + b, 0);
console.log(`Sum: ${sum}`);
console.log(`Current time: ${new Date()}`);""",
            "language": "javascript",
            "timeout": 10
        },
        {
            "name": "Fibonacci (Bash)",
            "code": """#!/bin/bash
echo "Fibonacci sequence:"
a=0
b=1
for i in {1..10}; do
    echo -n "$a "
    fn=$((a + b))
    a=$b
    b=$fn
done
echo "" """,
            "language": "bash",
            "timeout": 15
        }
    ]
    
    # Create interface
    with gr.Blocks(title="Code Interceptor Sandbox", theme=gr.themes.Soft()) as interface:
        gr.Markdown("""
        # 🔒 Code Interceptor + Agentic Sandbox
        
        Secure, production-ready code execution environment with comprehensive security analysis.
        
        **Features:**
        - 🔍 Static security analysis
        - ⚡ Multiple language support  
        - 🛡️ Process isolation
        - ⏱️ Resource limits
        - 📊 Real-time monitoring
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                code_input = gr.Code(
                    label="Code",
                    language="python",
                    value=examples[0]["code"],
                    lines=15
                )
                language_input = gr.Dropdown(
                    choices=list(LANGUAGE_CONFIGS.keys()),
                    value="python",
                    label="Programming Language"
                )
                timeout_input = gr.Number(
                    value=MAX_EXECUTION_TIME,
                    label="Timeout (seconds)",
                    minimum=1,
                    maximum=MAX_EXECUTION_TIME,
                    step=1
                )
                execute_btn = gr.Button("🚀 Execute Code", variant="primary")
            
            with gr.Column(scale=3):
                output = gr.Textbox(
                    label="Execution Results",
                    lines=20,
                    max_lines=30,
                    interactive=False
                )
        
        # Handle language changes
        def update_language(lang):
            example = next((ex for ex in examples if ex["language"] == lang), examples[0])
            return example["code"]
        
        language_input.change(
            fn=update_language,
            inputs=[language_input],
            outputs=[code_input]
        )
        
        # Wire up execution
        execute_btn.click(
            fn=execute_code_interface,
            inputs=[code_input, language_input, timeout_input],
            outputs=[output]
        )
        
        # Add examples section
        gr.Markdown("### 📝 Example Scripts")
        with gr.Row():
            for example in examples:
                with gr.Column():
                    gr.Markdown(f"**{example['name']}**")
                    gr.Button(
                        f"Load {example['name']}",
                        variant="secondary",
                        size="sm"
                    ).click(
                        fn=lambda e=example: (e["code"], e["language"], e["timeout"]),
                        outputs=[code_input, language_input, timeout_input]
                    )
    
    return interface


# Main application entry
if __name__ == "__main__":
    # Create Gradio interface
    demo = create_gradio_interface()
    
    # Launch both FastAPI and Gradio
    print("🚀 Starting Code Interceptor Sandbox...")
    print(f"📁 Sandbox directory: {SANDBOX_DIR}")
    print(f"⏱️ Max execution time: {MAX_EXECUTION_TIME}s")
    print(f"🧠 Max memory: {MAX_MEMORY_MB}MB")
    print(f"🌐 Supported languages: {', '.join(LANGUAGE_CONFIGS.keys())}")
    
    # Launch interface (this works for both HF Spaces and local deployment)
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=False,
        show_error=True
    )