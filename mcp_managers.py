"""
MCP Protocol Implementation for Code Interceptor + Agentic Sandbox
Hybrid architecture supporting both direct API access and MCP protocol
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """MCP Tool definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    category: str
    manager: str
    security_level: str
    async_execution: bool = True
    resource_limits: Optional[Dict[str, Any]] = None


@dataclass
class MCPResource:
    """MCP Resource definition"""
    uri: str
    name: str
    description: str
    mime_type: str
    size: Optional[int] = None


@dataclass
class MCPExecutionResult:
    """MCP Execution result"""
    success: bool
    data: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    resource_usage: Optional[Dict[str, Any]] = None
    timestamp: str = ""
    tool_name: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


class BaseManager(ABC):
    """Base class for all domain-specific managers"""
    
    def __init__(self, name: str, security_config: Dict[str, Any]):
        self.name = name
        self.security_config = security_config
        self.tools = {}
        self.resources = {}
        self._initialize_tools()
        self._initialize_resources()
    
    @abstractmethod
    def _initialize_tools(self):
        """Initialize tools for this manager"""
        pass
    
    @abstractmethod
    def _initialize_resources(self):
        """Initialize resources for this manager"""
        pass
    
    @abstractmethod
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> MCPExecutionResult:
        """Execute a tool with given parameters"""
        pass
    
    def get_tools(self) -> Dict[str, MCPTool]:
        """Get all tools for this manager"""
        return self.tools
    
    def get_resources(self) -> Dict[str, MCPResource]:
        """Get all resources for this manager"""
        return self.resources
    
    def validate_security(self, operation: str, parameters: Dict[str, Any]) -> tuple[bool, str]:
        """Validate security for operation"""
        # Default implementation - override in subclasses
        return True, ""


class BashManager(BaseManager):
    """Secure bash command execution manager"""
    
    def _initialize_tools(self):
        self.tools = {
            "bash_execute": MCPTool(
                name="bash_execute",
                description="Execute bash commands in secure sandbox",
                input_schema={
                    "type": "object",
                    "properties": {
                        "command": {"type": "string"},
                        "timeout": {"type": "integer", "default": 30},
                        "working_directory": {"type": "string", "default": "/tmp"}
                    },
                    "required": ["command"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "output": {"type": "string"},
                        "exit_code": {"type": "integer"},
                        "execution_time": {"type": "number"}
                    }
                },
                category="system",
                manager="BashManager",
                security_level="medium",
                async_execution=True
            ),
            "bash_validate": MCPTool(
                name="bash_validate",
                description="Validate bash command for security",
                input_schema={
                    "type": "object",
                    "properties": {
                        "command": {"type": "string"}
                    },
                    "required": ["command"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "safe": {"type": "boolean"},
                        "violations": {"type": "array"},
                        "recommendations": {"type": "array"}
                    }
                },
                category="security",
                manager="BashManager",
                security_level="low",
                async_execution=False
            )
        }
    
    def _initialize_resources(self):
        self.resources = {
            "bash_docs": MCPResource(
                uri="resource://bash/documentation",
                name="Bash Documentation",
                description="Reference documentation for bash commands",
                mime_type="text/markdown"
            )
        }
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> MCPExecutionResult:
        """Execute bash tool"""
        start_time = datetime.utcnow().timestamp()
        
        try:
            if tool_name == "bash_execute":
                return await self._execute_bash(parameters)
            elif tool_name == "bash_validate":
                return self._validate_bash(parameters)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
        except Exception as e:
            return MCPExecutionResult(
                success=False,
                data=None,
                error=str(e),
                execution_time=datetime.utcnow().timestamp() - start_time,
                tool_name=tool_name
            )
    
    async def _execute_bash(self, params: Dict[str, Any]) -> MCPExecutionResult:
        """Execute bash command with security validation"""
        command = params["command"]
        timeout = params.get("timeout", 30)
        
        # Security validation
        is_safe, violation_msg = self.validate_security("execute", {"command": command})
        if not is_safe:
            return MCPExecutionResult(
                success=False,
                data=None,
                error=f"Security violation: {violation_msg}",
                tool_name="bash_execute"
            )
        
        # Import and use the existing executor
        from app import executor
        result = executor.execute_code(
            code=f"#!/bin/bash\n{command}",
            language="bash",
            job_id=str(uuid.uuid4()),
            timeout=timeout
        )
        
        return MCPExecutionResult(
            success=result["success"],
            data={
                "output": result["output"],
                "exit_code": result["exit_code"],
                "execution_time": result["execution_time"]
            },
            error=result.get("error"),
            execution_time=result["execution_time"],
            tool_name="bash_execute"
        )
    
    def _validate_bash(self, params: Dict[str, Any]) -> MCPExecutionResult:
        """Validate bash command for security"""
        command = params["command"]
        
        # Security patterns
        dangerous_patterns = [
            r"rm\s+-rf",
            r"sudo\s",
            r"chmod\s+777",
            r"curl\s+",
            r"wget\s+",
            r"nc\s",
            r"/dev/",
            r"/proc/",
            r"/sys/"
        ]
        
        violations = []
        for pattern in dangerous_patterns:
            if command.lower().find(pattern) != -1:
                violations.append(f"Dangerous pattern detected: {pattern}")
        
        return MCPExecutionResult(
            success=True,
            data={
                "safe": len(violations) == 0,
                "violations": violations,
                "recommendations": ["Avoid system operations", "Use safe file operations only"]
            },
            tool_name="bash_validate"
        )
    
    def validate_security(self, operation: str, parameters: Dict[str, Any]) -> tuple[bool, str]:
        """Validate bash security"""
        if operation == "execute":
            command = parameters.get("command", "")
            
            # Critical security checks
            critical_patterns = [
                "rm -rf", "sudo", "chmod 777", "mkfs", "mount", "umount",
                "curl http", "wget http", "nc -l", "telnet", "ssh",
                "/etc/", "/proc/", "/sys/", "/dev/", "reboot", "shutdown"
            ]
            
            for pattern in critical_patterns:
                if pattern in command.lower():
                    return False, f"Security violation: {pattern} detected"
        
        return True, ""


class PythonManager(BaseManager):
    """Sandboxed Python code execution manager"""
    
    def _initialize_tools(self):
        self.tools = {
            "python_execute": MCPTool(
                name="python_execute",
                description="Execute Python code in secure sandbox",
                input_schema={
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "timeout": {"type": "integer", "default": 30},
                        "packages": {"type": "array", "items": {"type": "string"}, "default": []}
                    },
                    "required": ["code"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "output": {"type": "string"},
                        "result": {"type": "any"},
                        "execution_time": {"type": "number"}
                    }
                },
                category="execution",
                manager="PythonManager",
                security_level="medium",
                async_execution=True
            ),
            "python_analyze": MCPTool(
                name="python_analyze",
                description="Analyze Python code for security and complexity",
                input_schema={
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"}
                    },
                    "required": ["code"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "security_report": {"type": "object"},
                        "complexity_score": {"type": "integer"},
                        "recommendations": {"type": "array"}
                    }
                },
                category="analysis",
                manager="PythonManager",
                security_level="low",
                async_execution=False
            )
        }
    
    def _initialize_resources(self):
        self.resources = {
            "python_stdlib": MCPResource(
                uri="resource://python/stdlib",
                name="Python Standard Library",
                description="Documentation for Python standard library",
                mime_type="text/markdown"
            )
        }
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> MCPExecutionResult:
        """Execute Python tool"""
        start_time = datetime.utcnow().timestamp()
        
        try:
            if tool_name == "python_execute":
                return await self._execute_python(parameters)
            elif tool_name == "python_analyze":
                return self._analyze_python(parameters)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
        except Exception as e:
            return MCPExecutionResult(
                success=False,
                data=None,
                error=str(e),
                execution_time=datetime.utcnow().timestamp() - start_time,
                tool_name=tool_name
            )
    
    async def _execute_python(self, params: Dict[str, Any]) -> MCPExecutionResult:
        """Execute Python code"""
        code = params["code"]
        timeout = params.get("timeout", 30)
        
        # Security validation
        is_safe, violation_msg = self.validate_security("execute", {"code": code})
        if not is_safe:
            return MCPExecutionResult(
                success=False,
                data=None,
                error=f"Security violation: {violation_msg}",
                tool_name="python_execute"
            )
        
        # Use existing executor
        from app import executor
        result = executor.execute_code(
            code=code,
            language="python",
            job_id=str(uuid.uuid4()),
            timeout=timeout
        )
        
        return MCPExecutionResult(
            success=result["success"],
            data={
                "output": result["output"],
                "result": result.get("result"),
                "execution_time": result["execution_time"]
            },
            error=result.get("error"),
            execution_time=result["execution_time"],
            tool_name="python_execute"
        )
    
    def _analyze_python(self, params: Dict[str, Any]) -> MCPExecutionResult:
        """Analyze Python code"""
        code = params["code"]
        
        # Use existing security analysis
        from app import executor
        security_result = executor.interceptor.analyze_code(code, "python")
        
        return MCPExecutionResult(
            success=True,
            data={
                "security_report": security_result,
                "complexity_score": security_result.get("complexity_score", 0),
                "recommendations": security_result.get("recommendations", [])
            },
            tool_name="python_analyze"
        )
    
    def validate_security(self, operation: str, parameters: Dict[str, Any]) -> tuple[bool, str]:
        """Validate Python security"""
        if operation == "execute":
            code = parameters.get("code", "")
            
            # Critical security patterns
            critical_patterns = [
                "import os", "import sys", "import subprocess",
                "os.system", "os.popen", "subprocess.call",
                "eval(", "exec(", "__import__",
                "open('/etc", "open('/proc", "open('/sys"
            ]
            
            for pattern in critical_patterns:
                if pattern in code.lower():
                    return False, f"Security violation: {pattern} detected"
        
        return True, ""


class FileManager(BaseManager):
    """Safe file operations manager"""
    
    def _initialize_tools(self):
        self.tools = {
            "file_read": MCPTool(
                name="file_read",
                description="Read file contents from sandbox directory",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "encoding": {"type": "string", "default": "utf-8"}
                    },
                    "required": ["path"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "size": {"type": "integer"},
                        "encoding": {"type": "string"}
                    }
                },
                category="file_operations",
                manager="FileManager",
                security_level="low",
                async_execution=False
            ),
            "file_write": MCPTool(
                name="file_write",
                description="Write content to file in sandbox directory",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"},
                        "encoding": {"type": "string", "default": "utf-8"}
                    },
                    "required": ["path", "content"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "size": {"type": "integer"},
                        "path": {"type": "string"}
                    }
                },
                category="file_operations",
                manager="FileManager",
                security_level="medium",
                async_execution=False
            ),
            "file_list": MCPTool(
                name="file_list",
                description="List files in sandbox directory",
                input_schema={
                    "type": "object",
                    "properties": {
                        "directory": {"type": "string", "default": "/tmp/code_sandbox"},
                        "recursive": {"type": "boolean", "default": False}
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "files": {"type": "array"},
                        "directories": {"type": "array"},
                        "total_size": {"type": "integer"}
                    }
                },
                category="file_operations",
                manager="FileManager",
                security_level="low",
                async_execution=False
            )
        }
    
    def _initialize_resources(self):
        self.resources = {
            "sandbox_fs": MCPResource(
                uri="resource://filesystem/sandbox",
                name="Sandbox Filesystem",
                description="Virtual filesystem for sandboxed operations",
                mime_type="application/json"
            )
        }
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> MCPExecutionResult:
        """Execute file operation tool"""
        start_time = datetime.utcnow().timestamp()
        
        try:
            if tool_name == "file_read":
                return await self._read_file(parameters)
            elif tool_name == "file_write":
                return await self._write_file(parameters)
            elif tool_name == "file_list":
                return self._list_files(parameters)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
        except Exception as e:
            return MCPExecutionResult(
                success=False,
                data=None,
                error=str(e),
                execution_time=datetime.utcnow().timestamp() - start_time,
                tool_name=tool_name
            )
    
    async def _read_file(self, params: Dict[str, Any]) -> MCPExecutionResult:
        """Read file contents"""
        import os
        path = params["path"]
        encoding = params.get("encoding", "utf-8")
        
        # Security validation
        is_safe, violation_msg = self.validate_security("read", {"path": path})
        if not is_safe:
            return MCPExecutionResult(
                success=False,
                data=None,
                error=f"Security violation: {violation_msg}",
                tool_name="file_read"
            )
        
        # Ensure path is within sandbox
        if not path.startswith("/tmp/code_sandbox"):
            return MCPExecutionResult(
                success=False,
                data=None,
                error="Access denied: outside sandbox directory",
                tool_name="file_read"
            )
        
        try:
            with open(path, "r", encoding=encoding) as f:
                content = f.read()
            
            return MCPExecutionResult(
                success=True,
                data={
                    "content": content,
                    "size": len(content.encode(encoding)),
                    "encoding": encoding
                },
                tool_name="file_read"
            )
        except Exception as e:
            return MCPExecutionResult(
                success=False,
                data=None,
                error=f"File read error: {str(e)}",
                tool_name="file_read"
            )
    
    async def _write_file(self, params: Dict[str, Any]) -> MCPExecutionResult:
        """Write file contents"""
        import os
        path = params["path"]
        content = params["content"]
        encoding = params.get("encoding", "utf-8")
        
        # Security validation
        is_safe, violation_msg = self.validate_security("write", {"path": path})
        if not is_safe:
            return MCPExecutionResult(
                success=False,
                data=None,
                error=f"Security violation: {violation_msg}",
                tool_name="file_write"
            )
        
        # Ensure path is within sandbox
        if not path.startswith("/tmp/code_sandbox"):
            return MCPExecutionResult(
                success=False,
                data=None,
                error="Access denied: outside sandbox directory",
                tool_name="file_write"
            )
        
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            with open(path, "w", encoding=encoding) as f:
                f.write(content)
            
            return MCPExecutionResult(
                success=True,
                data={
                    "success": True,
                    "size": len(content.encode(encoding)),
                    "path": path
                },
                tool_name="file_write"
            )
        except Exception as e:
            return MCPExecutionResult(
                success=False,
                data=None,
                error=f"File write error: {str(e)}",
                tool_name="file_write"
            )
    
    def _list_files(self, params: Dict[str, Any]) -> MCPExecutionResult:
        """List files in directory"""
        import os
        directory = params.get("directory", "/tmp/code_sandbox")
        recursive = params.get("recursive", False)
        
        # Security validation
        is_safe, violation_msg = self.validate_security("list", {"directory": directory})
        if not is_safe:
            return MCPExecutionResult(
                success=False,
                data=None,
                error=f"Security violation: {violation_msg}",
                tool_name="file_list"
            )
        
        # Ensure directory is within sandbox
        if not directory.startswith("/tmp/code_sandbox"):
            return MCPExecutionResult(
                success=False,
                data=None,
                error="Access denied: outside sandbox directory",
                tool_name="file_list"
            )
        
        try:
            files = []
            directories = []
            total_size = 0
            
            if os.path.exists(directory):
                for item in os.listdir(directory):
                    item_path = os.path.join(directory, item)
                    if os.path.isfile(item_path):
                        files.append({
                            "name": item,
                            "size": os.path.getsize(item_path),
                            "modified": os.path.getmtime(item_path)
                        })
                        total_size += os.path.getsize(item_path)
                    elif os.path.isdir(item_path):
                        directories.append({
                            "name": item,
                            "created": os.path.getctime(item_path)
                        })
            
            return MCPExecutionResult(
                success=True,
                data={
                    "files": files,
                    "directories": directories,
                    "total_size": total_size
                },
                tool_name="file_list"
            )
        except Exception as e:
            return MCPExecutionResult(
                success=False,
                data=None,
                error=f"File list error: {str(e)}",
                tool_name="file_list"
            )
    
    def validate_security(self, operation: str, parameters: Dict[str, Any]) -> tuple[bool, str]:
        """Validate file operation security"""
        if operation in ["read", "write", "list"]:
            path = parameters.get("path", parameters.get("directory", ""))
            
            # Disallow access to system directories
            dangerous_paths = ["/etc/", "/proc/", "/sys/", "/var/", "/usr/"]
            
            for dangerous_path in dangerous_paths:
                if path.startswith(dangerous_path):
                    return False, f"Security violation: access to {dangerous_path} denied"
        
        return True, ""


class WebManager(BaseManager):
    """Secure web browsing and scraping manager"""
    
    def _initialize_tools(self):
        self.tools = {
            "web_fetch": MCPTool(
                name="web_fetch",
                description="Fetch web content with security validation",
                input_schema={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"},
                        "method": {"type": "string", "default": "GET"},
                        "headers": {"type": "object", "default": {}},
                        "timeout": {"type": "integer", "default": 10}
                    },
                    "required": ["url"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "status_code": {"type": "integer"},
                        "content": {"type": "string"},
                        "headers": {"type": "object"},
                        "url": {"type": "string"}
                    }
                },
                category="web_operations",
                manager="WebManager",
                security_level="medium",
                async_execution=True
            ),
            "web_search": MCPTool(
                name="web_search",
                description="Perform web search with result extraction",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "num_results": {"type": "integer", "default": 5},
                        "safe_search": {"type": "boolean", "default": True}
                    },
                    "required": ["query"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "results": {"type": "array"},
                        "total_results": {"type": "integer"},
                        "query": {"type": "string"}
                    }
                },
                category="web_operations",
                manager="WebManager",
                security_level="medium",
                async_execution=True
            )
        }
    
    def _initialize_resources(self):
        self.resources = {
            "web_docs": MCPResource(
                uri="resource://web/documentation",
                name="Web API Documentation",
                description="Documentation for web operations",
                mime_type="text/markdown"
            )
        }
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> MCPExecutionResult:
        """Execute web tool"""
        start_time = datetime.utcnow().timestamp()
        
        try:
            if tool_name == "web_fetch":
                return await self._fetch_web(parameters)
            elif tool_name == "web_search":
                return await self._search_web(parameters)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
        except Exception as e:
            return MCPExecutionResult(
                success=False,
                data=None,
                error=str(e),
                execution_time=datetime.utcnow().timestamp() - start_time,
                tool_name=tool_name
            )
    
    async def _fetch_web(self, params: Dict[str, Any]) -> MCPExecutionResult:
        """Fetch web content"""
        import aiohttp
        import asyncio
        
        url = params["url"]
        method = params.get("method", "GET")
        headers = params.get("headers", {})
        timeout = params.get("timeout", 10)
        
        # Security validation
        is_safe, violation_msg = self.validate_security("fetch", {"url": url})
        if not is_safe:
            return MCPExecutionResult(
                success=False,
                data=None,
                error=f"Security violation: {violation_msg}",
                tool_name="web_fetch"
            )
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.request(method, url, headers=headers) as response:
                    content = await response.text()
                    
                    return MCPExecutionResult(
                        success=True,
                        data={
                            "status_code": response.status,
                            "content": content[:10000],  # Limit content size
                            "headers": dict(response.headers),
                            "url": str(response.url)
                        },
                        tool_name="web_fetch"
                    )
        except Exception as e:
            return MCPExecutionResult(
                success=False,
                data=None,
                error=f"Web fetch error: {str(e)}",
                tool_name="web_fetch"
            )
    
    async def _search_web(self, params: Dict[str, Any]) -> MCPExecutionResult:
        """Perform web search"""
        query = params["query"]
        num_results = params.get("num_results", 5)
        
        # Use existing search functionality
        try:
            from batch_web_search import batch_web_search
            
            # Convert to our search format
            search_results = await batch_web_search([{
                "query": query,
                "num_results": num_results,
                "cursor": 1
            }])
            
            return MCPExecutionResult(
                success=True,
                data={
                    "results": search_results[0] if search_results else [],
                    "total_results": len(search_results[0]) if search_results else 0,
                    "query": query
                },
                tool_name="web_search"
            )
        except Exception as e:
            return MCPExecutionResult(
                success=False,
                data=None,
                error=f"Web search error: {str(e)}",
                tool_name="web_search"
            )
    
    def validate_security(self, operation: str, parameters: Dict[str, Any]) -> tuple[bool, str]:
        """Validate web operation security"""
        if operation == "fetch":
            url = parameters.get("url", "")
            
            # Only allow HTTP/HTTPS
            if not url.startswith(("http://", "https://")):
                return False, "Security violation: only HTTP/HTTPS URLs allowed"
            
            # Block local/internal addresses
            blocked_domains = ["localhost", "127.0.0.1", "0.0.0.0", "::1"]
            for domain in blocked_domains:
                if domain in url:
                    return False, f"Security violation: access to {domain} denied"
        
        return True, ""


class KnowledgeBaseManager(BaseManager):
    """Structured document storage with semantic search"""
    
    def _initialize_tools(self):
        self.tools = {
            "kb_store": MCPTool(
                name="kb_store",
                description="Store document in knowledge base",
                input_schema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "metadata": {"type": "object", "default": {}},
                        "tags": {"type": "array", "items": {"type": "string"}, "default": []},
                        "doc_type": {"type": "string", "default": "text"}
                    },
                    "required": ["content"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "document_id": {"type": "string"},
                        "success": {"type": "boolean"},
                        "tags": {"type": "array"}
                    }
                },
                category="knowledge",
                manager="KnowledgeBaseManager",
                security_level="low",
                async_execution=False
            ),
            "kb_search": MCPTool(
                name="kb_search",
                description="Search knowledge base documents",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "max_results": {"type": "integer", "default": 10},
                        "tags": {"type": "array", "items": {"type": "string"}, "default": []}
                    },
                    "required": ["query"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "results": {"type": "array"},
                        "total_results": {"type": "integer"},
                        "query": {"type": "string"}
                    }
                },
                category="knowledge",
                manager="KnowledgeBaseManager",
                security_level="low",
                async_execution=False
            )
        }
    
    def _initialize_resources(self):
        self.resources = {
            "kb_index": MCPResource(
                uri="resource://knowledge/index",
                name="Knowledge Base Index",
                description="Index of stored documents",
                mime_type="application/json"
            )
        }
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> MCPExecutionResult:
        """Execute knowledge base tool"""
        start_time = datetime.utcnow().timestamp()
        
        try:
            if tool_name == "kb_store":
                return self._store_document(parameters)
            elif tool_name == "kb_search":
                return self._search_documents(parameters)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
        except Exception as e:
            return MCPExecutionResult(
                success=False,
                data=None,
                error=str(e),
                execution_time=datetime.utcnow().timestamp() - start_time,
                tool_name=tool_name
            )
    
    def _store_document(self, params: Dict[str, Any]) -> MCPExecutionResult:
        """Store document in knowledge base"""
        import os
        import json
        import hashlib
        
        content = params["content"]
        metadata = params.get("metadata", {})
        tags = params.get("tags", [])
        doc_type = params.get("doc_type", "text")
        
        # Generate document ID
        doc_id = hashlib.md5(content.encode()).hexdigest()
        
        # Create storage directory
        kb_dir = "/tmp/code_sandbox/knowledge_base"
        os.makedirs(kb_dir, exist_ok=True)
        
        # Store document
        doc_data = {
            "id": doc_id,
            "content": content,
            "metadata": metadata,
            "tags": tags,
            "doc_type": doc_type,
            "created": datetime.utcnow().isoformat()
        }
        
        try:
            doc_path = os.path.join(kb_dir, f"{doc_id}.json")
            with open(doc_path, "w") as f:
                json.dump(doc_data, f, indent=2)
            
            return MCPExecutionResult(
                success=True,
                data={
                    "document_id": doc_id,
                    "success": True,
                    "tags": tags
                },
                tool_name="kb_store"
            )
        except Exception as e:
            return MCPExecutionResult(
                success=False,
                data=None,
                error=f"KB store error: {str(e)}",
                tool_name="kb_store"
            )
    
    def _search_documents(self, params: Dict[str, Any]) -> MCPExecutionResult:
        """Search documents in knowledge base"""
        import os
        import json
        import re
        
        query = params["query"]
        max_results = params.get("max_results", 10)
        tags = params.get("tags", [])
        
        kb_dir = "/tmp/code_sandbox/knowledge_base"
        
        try:
            results = []
            
            if os.path.exists(kb_dir):
                for filename in os.listdir(kb_dir):
                    if filename.endswith(".json"):
                        doc_path = os.path.join(kb_dir, filename)
                        with open(doc_path, "r") as f:
                            doc_data = json.load(f)
                        
                        # Simple text matching
                        content = doc_data.get("content", "")
                        doc_tags = doc_data.get("tags", [])
                        
                        # Check if query matches content
                        if query.lower() in content.lower():
                            # Check tag filter
                            if not tags or any(tag in doc_tags for tag in tags):
                                results.append({
                                    "id": doc_data.get("id"),
                                    "content_preview": content[:200] + "..." if len(content) > 200 else content,
                                    "tags": doc_tags,
                                    "metadata": doc_data.get("metadata", {}),
                                    "created": doc_data.get("created")
                                })
                        
                        if len(results) >= max_results:
                            break
            
            return MCPExecutionResult(
                success=True,
                data={
                    "results": results,
                    "total_results": len(results),
                    "query": query
                },
                tool_name="kb_search"
            )
        except Exception as e:
            return MCPExecutionResult(
                success=False,
                data=None,
                error=f"KB search error: {str(e)}",
                tool_name="kb_search"
            )
    
    def validate_security(self, operation: str, parameters: Dict[str, Any]) -> tuple[bool, str]:
        """Validate knowledge base operation security"""
        # Knowledge base operations are generally safe
        return True, ""


# Export all managers
__all__ = [
    'BaseManager', 'BashManager', 'PythonManager', 'FileManager', 
    'WebManager', 'KnowledgeBaseManager', 'MCPTool', 'MCPResource', 'MCPExecutionResult'
]