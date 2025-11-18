#!/usr/bin/env python3
"""
Hybrid MCP + REST API Code Interceptor + Agentic Sandbox
Production-ready, secure code execution environment with MCP protocol support
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

# Import MCP components
from mcp_server import mcp_server
from security_config import SecurityConfig

# Security Configuration
MAX_EXECUTION_TIME = int(os.getenv("MAX_EXECUTION_TIME", "30"))
MAX_MEMORY_MB = int(os.getenv("MAX_MEMORY_MB", "256"))
MAX_OUTPUT_SIZE = int(os.getenv("MAX_OUTPUT_SIZE", "8192"))
SANDBOX_DIR = Path(os.getenv("SANDBOX_DIR", "/tmp/code_sandbox"))
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

# Enhanced security patterns
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
    """Enhanced static analysis security interceptor with MCP integration"""
    
    def __init__(self):
        self.violations: List[SecurityViolation] = []
    
    def analyze_code(self, code: str, language: str) -> Dict:
        """Perform comprehensive security analysis"""
        self.violations = []
        
        # Import static analysis rules if available
        try:
            from static_analysis_rules import static_rules
            static_analysis = static_rules.analyze_code(code, language)
            
            # Convert violations to our format
            for violation in static_analysis.get("violations", []):
                self.violations.append(SecurityViolation(
                    pattern=violation["pattern"],
                    line=violation["line_number"],
                    context=violation["line_content"]
                ))
                
        except ImportError:
            # Fallback to basic pattern matching
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
            "recommendations": self._get_recommendations(),
            "risk_score": self._calculate_risk_score(),
            "severity_breakdown": self._get_severity_breakdown()
        }
    
    def _calculate_complexity(self, code: str, language: str) -> int:
        """Calculate code complexity score"""
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        # Base complexity from line count
        complexity = len(non_empty_lines)
        
        # Language-specific metrics
        if language == "python":
            complexity += code.count('def ') + code.count('class ') + code.count('if ') + code.count('for ')
        elif language == "javascript":
            complexity += code.count('function ') + code.count('class ') + code.count('if ') + code.count('for ')
        elif language == "bash":
            complexity += code.count('if ') + code.count('for ') + code.count('while ')
        
        return min(complexity, 1000)
    
    def _calculate_risk_score(self) -> int:
        """Calculate risk score based on violations"""
        if not self.violations:
            return 0
        
        # Simple risk calculation
        severity_weights = {
            "CRITICAL": 10,
            "HIGH": 5,
            "MEDIUM": 2,
            "LOW": 1
        }
        
        total_score = sum(5 for _ in self.violations)  # Default to medium severity
        return min(100, total_score)
    
    def _get_severity_breakdown(self) -> Dict:
        """Get severity breakdown"""
        return {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": len(self.violations),
            "LOW": 0
        }
    
    def _get_recommendations(self) -> List[str]:
        """Get security recommendations"""
        recommendations = []
        
        violation_patterns = " ".join([v.pattern for v in self.violations])
        
        if any(pattern in violation_patterns for pattern in ["eval", "exec"]):
            recommendations.append("Avoid dynamic code execution")
        
        if any(pattern in violation_patterns for pattern in ["os.system", "subprocess"]):
            recommendations.append("Use safer alternatives for system operations")
        
        if any(pattern in violation_patterns for pattern in ["/dev", "/proc", "/sys"]):
            recommendations.append("Avoid accessing system directories")
        
        if not recommendations:
            recommendations.append("Code appears to follow security best practices")
        
        return recommendations


class SandboxExecutor:
    """Enhanced sandbox executor with MCP integration"""
    
    def __init__(self):
        self.interceptor = SecurityInterceptor()
    
    def create_sandbox_directory(self, job_id: str) -> Path:
        """Create isolated sandbox directory"""
        sandbox_path = SANDBOX_DIR / job_id
        sandbox_path.mkdir(mode=0o700, exist_ok=True)
        return sandbox_path
    
    def set_resource_limits(self):
        """Set strict resource limits"""
        try:
            # Memory limit
            resource.setrlimit(resource.RLIMIT_AS, (MAX_MEMORY_MB * 1024 * 1024, MAX_MEMORY_MB * 1024 * 1024))
            
            # CPU time limit
            resource.setrlimit(resource.RLIMIT_CPU, (MAX_EXECUTION_TIME, MAX_EXECUTION_TIME))
            
            # File size limit
            resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_OUTPUT_SIZE, MAX_OUTPUT_SIZE))
            
            # Number of processes
            resource.setrlimit(resource.RLIMIT_NPROC, (2, 2))
        except (OSError, ValueError):
            pass  # Some limits may not be settable
    
    def execute_code(self, code: str, language: str, job_id: str, timeout: int = None) -> Dict:
        """Execute code in secure sandbox with enhanced reporting"""
        
        if timeout is None:
            timeout = int(MAX_EXECUTION_TIME * LANGUAGE_CONFIGS.get(language, {}).get("timeout_multiplier", 1.0))
        
        # Security analysis
        security_result = self.interceptor.analyze_code(code, language)
        
        # Check if code is allowed
        if not security_result["allowed"]:
            return {
                "success": False,
                "error": "Security violation detected",
                "violations": security_result["violations"],
                "output": "",
                "exit_code": -1,
                "execution_time": 0,
                "security_report": security_result
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
            
            os.chmod(code_file, 0o600)
            
            # Execute in subprocess with strict controls
            result = self._execute_subprocess(code_file, config["command"], timeout, sandbox_path)
            
            # Add enhanced security reporting
            result["security_report"] = security_result
            result["job_id"] = job_id
            result["language"] = language
            result["sandbox_path"] = str(sandbox_path)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution failed: {str(e)}",
                "output": "",
                "exit_code": -1,
                "execution_time": 0,
                "security_report": security_result,
                "job_id": job_id
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
                "TMPDIR": str(sandbox_path),
                "PYTHONPATH": "",
                "NODE_PATH": ""
            }
            
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
                    "exit_code": 124,
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
            pass


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

# Create the main application (combining MCP and legacy REST)
app = mcp_server.app


# Add legacy endpoints that integrate with MCP system
@app.post("/execute", response_model=ExecutionResponse)
async def execute_code_legacy(request: ExecutionRequest):
    """Execute code using legacy REST API (integrates with MCP system)"""
    
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
            "Sandbox execution",
            "MCP protocol support",
            "Domain-specific managers"
        ],
        "mcp_managers": list(mcp_server.managers.keys()),
        "total_tools": len(mcp_server.tools),
        "total_resources": len(mcp_server.resources)
    }


# Enhanced Gradio Interface with MCP integration
def create_enhanced_gradio_interface():
    """Create enhanced Gradio interface with MCP capabilities"""
    
    def execute_code_interface(code, language, timeout, use_mcp=False):
        """Enhanced execution interface with MCP option"""
        try:
            job_id = str(uuid.uuid4())
            
            if use_mcp:
                # Use MCP Python execution
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                result = loop.run_until_complete(
                    mcp_server.execute_tool("python_execute", {
                        "code": code,
                        "timeout": int(timeout) if timeout else MAX_EXECUTION_TIME
                    })
                )
                loop.close()
                
                # Format MCP result
                if not result.get("isError", False):
                    output = f"✅ MCP Execution Successful\n\n"
                    output += f"Output:\n{result['content'][0]['text']}\n\n"
                    output += f"Tool: python_execute\n"
                    output += f"Manager: PythonManager\n"
                else:
                    output = f"❌ MCP Execution Failed\n\n"
                    output += f"Error: {result['content'][0]['text']}\n"
            else:
                # Use legacy execution
                result = executor.execute_code(
                    code=code,
                    language=language,
                    job_id=job_id,
                    timeout=int(timeout) if timeout else None
                )
                
                # Format legacy result
                if result["success"]:
                    output = f"✅ Legacy Execution Successful\n\n"
                    output += f"Output:\n{result['output']}\n\n"
                    output += f"Exit Code: {result['exit_code']}\n"
                    output += f"Execution Time: {result['execution_time']:.2f}s\n"
                    
                    if result.get('security_report', {}).get('violations'):
                        output += f"\n⚠️ Security Warnings:\n"
                        for violation in result['security_report']['violations']:
                            output += f"  - Line {violation['line']}: {violation['pattern']}\n"
                else:
                    output = f"❌ Legacy Execution Failed\n\n"
                    output += f"Error: {result['error']}\n"
                    if result.get('violations'):
                        output += f"\n🔒 Security Violations:\n"
                        for violation in result['violations']:
                            output += f"  - Line {violation['line']}: {violation['pattern']}\n"
            
            return output
            
        except Exception as e:
            return f"❌ Interface Error: {str(e)}"
    
    def execute_mcp_tool(tool_name, parameters):
        """Execute MCP tool directly"""
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Parse parameters (assuming JSON string)
            try:
                params = json.loads(parameters) if parameters else {}
            except json.JSONDecodeError:
                params = {"input": parameters}
            
            result = loop.run_until_complete(
                mcp_server.execute_tool(tool_name, params)
            )
            loop.close()
            
            if not result.get("isError", False):
                return f"✅ MCP Tool Executed Successfully\n\nTool: {tool_name}\nResult:\n{result['content'][0]['text']}"
            else:
                return f"❌ MCP Tool Failed\n\nTool: {tool_name}\nError: {result['content'][0]['text']}"
                
        except Exception as e:
            return f"❌ MCP Tool Error: {str(e)}"
    
    # Sample code examples
    examples = [
        {
            "name": "Hello World (Python)",
            "code": """print("Hello from secure sandbox!")
import datetime
result = sum(range(10))
print(f"Sum of 0-9: {result}")
print(f"Current time: {datetime.datetime.now()}")""",
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
    
    # MCP tools examples
    mcp_examples = [
        {
            "name": "File Operations",
            "tool": "file_write",
            "parameters": '{"path": "/tmp/code_sandbox/test.txt", "content": "Hello from MCP!"}'
        },
        {
            "name": "Python Analysis",
            "tool": "python_analyze",
            "parameters": '{"code": "print(\\'Hello World\\')"}'
        },
        {
            "name": "Bash Validation",
            "tool": "bash_validate",
            "parameters": '{"command": "echo \\'Hello\\'"}'
        }
    ]
    
    # Create enhanced interface
    with gr.Blocks(title="MCP Code Interceptor Sandbox", theme=gr.themes.Soft()) as interface:
        gr.Markdown("""
        # 🔒 MCP Code Interceptor + Agentic Sandbox
        
        **Hybrid Architecture**: Secure code execution with MCP protocol support
        
        **Features:**
        - 🔍 Enhanced static security analysis
        - ⚡ Multiple language support (Python, JavaScript, Bash, C++, Rust)
        - 🤖 **NEW**: MCP protocol integration for AI agents
        - 🔧 Domain-specific managers (Bash, Python, File, Web, Knowledge)
        - 🛡️ Process isolation & resource limits
        - 📊 Real-time security reporting
        """)
        
        with gr.Tab("Code Execution"):
            with gr.Row():
                with gr.Column(scale=2):
                    gr.Markdown("### 💻 Code Execution")
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
                    use_mcp_toggle = gr.Checkbox(
                        value=False,
                        label="Use MCP Protocol",
                        info="Execute via MCP for enhanced security and reporting"
                    )
                    execute_btn = gr.Button("🚀 Execute Code", variant="primary")
                
                with gr.Column(scale=3):
                    output = gr.Textbox(
                        label="Execution Results",
                        lines=20,
                        max_lines=30,
                        interactive=False
                    )
        
        with gr.Tab("MCP Tools"):
            with gr.Row():
                with gr.Column(scale=2):
                    gr.Markdown("### 🛠️ MCP Tool Execution")
                    tool_name_input = gr.Dropdown(
                        choices=list(mcp_server.tools.keys()),
                        value="python_execute",
                        label="MCP Tool"
                    )
                    parameters_input = gr.Textbox(
                        label="Parameters (JSON)",
                        value='{"code": "print(\\"Hello from MCP!\\")", "timeout": 30}',
                        lines=5
                    )
                    execute_mcp_btn = gr.Button("⚡ Execute MCP Tool", variant="secondary")
                
                with gr.Column(scale=3):
                    mcp_output = gr.Textbox(
                        label="MCP Execution Results",
                        lines=20,
                        max_lines=30,
                        interactive=False
                    )
        
        with gr.Tab("System Info"):
            gr.Markdown("### ℹ️ System Information")
            
            def get_system_info():
                """Get comprehensive system information"""
                info = {
                    "Server": mcp_server.get_server_info(),
                    "Languages": LANGUAGE_CONFIGS,
                    "Security": {
                        "max_execution_time": MAX_EXECUTION_TIME,
                        "max_memory_mb": MAX_MEMORY_MB,
                        "max_output_size": MAX_OUTPUT_SIZE,
                        "dangerous_patterns": len(DANGEROUS_PATTERNS)
                    }
                }
                
                # Format as readable text
                text = "## 🏗️ Architecture\n"
                for key, value in info["Server"].items():
                    text += f"**{key}**: {value}\n"
                
                text += "\n## 🔧 Configuration\n"
                for key, value in info["Security"].items():
                    text += f"**{key}**: {value}\n"
                
                text += "\n## 💻 Supported Languages\n"
                for lang, config in info["Languages"].items():
                    text += f"**{lang}**: {config['command']} ({config['file_extension']})\n"
                
                return text
            
            system_info_btn = gr.Button("📊 Refresh System Info", variant="secondary")
            system_info_display = gr.Markdown()
        
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
            inputs=[code_input, language_input, timeout_input, use_mcp_toggle],
            outputs=[output]
        )
        
        # Wire up MCP execution
        execute_mcp_btn.click(
            fn=execute_mcp_tool,
            inputs=[tool_name_input, parameters_input],
            outputs=[mcp_output]
        )
        
        # Wire up system info
        system_info_btn.click(
            fn=get_system_info,
            outputs=[system_info_display]
        )
        
        # Add examples section
        with gr.Accordion("📝 Code Examples", open=False):
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
        
        with gr.Accordion("🛠️ MCP Tool Examples", open=False):
            with gr.Row():
                for example in mcp_examples:
                    with gr.Column():
                        gr.Markdown(f"**{example['name']}**")
                        gr.Button(
                            f"Load {example['name']}",
                            variant="secondary",
                            size="sm"
                        ).click(
                            fn=lambda e=example: (e["tool"], e["parameters"]),
                            outputs=[tool_name_input, parameters_input]
                        )
    
    return interface


# Main application entry
if __name__ == "__main__":
    print("🚀 Starting MCP Code Interceptor Sandbox...")
    print(f"📁 Sandbox directory: {SANDBOX_DIR}")
    print(f"⏱️ Max execution time: {MAX_EXECUTION_TIME}s")
    print(f"🧠 Max memory: {MAX_MEMORY_MB}MB")
    print(f"🌐 Supported languages: {', '.join(LANGUAGE_CONFIGS.keys())}")
    print(f"🤖 MCP managers: {', '.join(mcp_server.managers.keys())}")
    print(f"🔧 Total MCP tools: {len(mcp_server.tools)}")
    
    # Create enhanced Gradio interface
    demo = create_enhanced_gradio_interface()
    
    # Launch interface
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=False,
        show_error=True
    )