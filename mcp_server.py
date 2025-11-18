"""
MCP Server Implementation
Core MCP protocol server that coordinates all domain managers
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import uuid

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from mcp_managers import (
    BashManager, PythonManager, FileManager, WebManager, KnowledgeBaseManager,
    MCPTool, MCPResource, MCPExecutionResult
)
from security_config import CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPRequest(BaseModel):
    """MCP request model"""
    jsonrpc: str = "2.0"
    id: Union[str, int, None] = None
    method: str
    params: Dict[str, Any] = {}


class MCPResponse(BaseModel):
    """MCP response model"""
    jsonrpc: str = "2.0"
    id: Union[str, int, None] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class MCPServer:
    """Main MCP Server that coordinates all managers"""
    
    def __init__(self):
        self.managers = {}
        self.tools = {}
        self.resources = {}
        self._initialize_managers()
        self._build_tool_index()
        self._build_resource_index()
        
        # Create FastAPI app
        self.app = FastAPI(
            title="MCP Code Interceptor Sandbox",
            description="Hybrid MCP + REST API for secure code execution",
            version="2.0.0"
        )
        
        self._setup_routes()
    
    def _initialize_managers(self):
        """Initialize all domain managers"""
        logger.info("Initializing MCP managers...")
        
        # Initialize managers with security configuration
        security_config = {
            "max_execution_time": CONFIG.MAX_EXECUTION_TIME,
            "max_memory_mb": CONFIG.MAX_MEMORY_MB,
            "sandbox_dir": CONFIG.SANDBOX_DIR
        }
        
        self.managers = {
            "bash": BashManager("bash", security_config),
            "python": PythonManager("python", security_config),
            "filesystem": FileManager("filesystem", security_config),
            "web": WebManager("web", security_config),
            "knowledge": KnowledgeBaseManager("knowledge", security_config)
        }
        
        logger.info(f"Initialized {len(self.managers)} managers")
    
    def _build_tool_index(self):
        """Build index of all available tools"""
        for manager_name, manager in self.managers.items():
            manager_tools = manager.get_tools()
            for tool_name, tool in manager_tools.items():
                # Create unique tool ID
                tool_id = f"{manager_name}.{tool_name}"
                self.tools[tool_id] = tool
                
                # Also index by name for convenience
                if tool_name not in [t.name for t in self.tools.values()]:
                    self.tools[tool_name] = tool
        
        logger.info(f"Indexed {len(self.tools)} tools")
    
    def _build_resource_index(self):
        """Build index of all available resources"""
        for manager_name, manager in self.managers.items():
            manager_resources = manager.get_resources()
            for resource_uri, resource in manager_resources.items():
                self.resources[resource_uri] = resource
        
        logger.info(f"Indexed {len(self.resources)} resources")
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/")
        async def root():
            """Health check and server info"""
            return {
                "service": "MCP Code Interceptor Sandbox",
                "version": "2.0.0",
                "status": "healthy",
                "protocols": ["mcp", "rest"],
                "managers": list(self.managers.keys()),
                "tools_count": len(self.tools),
                "resources_count": len(self.resources),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        @self.app.get("/health")
        async def health():
            """Detailed health check"""
            return {
                "status": "healthy",
                "managers": {
                    name: {"tools": len(manager.get_tools()), "resources": len(manager.get_resources())}
                    for name, manager in self.managers.items()
                },
                "configuration": {
                    "max_execution_time": CONFIG.MAX_EXECUTION_TIME,
                    "max_memory_mb": CONFIG.MAX_MEMORY_MB,
                    "sandbox_dir": CONFIG.SANDBOX_DIR
                }
            }
        
        @self.app.get("/mcp/tools")
        async def list_tools():
            """List all available MCP tools"""
            tools_list = []
            for tool_id, tool in self.tools.items():
                tools_list.append({
                    "id": tool_id,
                    "name": tool.name,
                    "description": tool.description,
                    "category": tool.category,
                    "manager": tool.manager,
                    "security_level": tool.security_level,
                    "async_execution": tool.async_execution,
                    "input_schema": tool.input_schema,
                    "output_schema": tool.output_schema,
                    "resource_limits": tool.resource_limits
                })
            
            return {
                "tools": tools_list,
                "total": len(tools_list)
            }
        
        @self.app.get("/mcp/resources")
        async def list_resources():
            """List all available MCP resources"""
            resources_list = []
            for uri, resource in self.resources.items():
                resources_list.append({
                    "uri": uri,
                    "name": resource.name,
                    "description": resource.description,
                    "mime_type": resource.mime_type,
                    "size": resource.size
                })
            
            return {
                "resources": resources_list,
                "total": len(resources_list)
            }
        
        @self.app.post("/mcp/execute")
        async def mcp_execute(request: MCPRequest):
            """Execute MCP tool"""
            try:
                result = await self.execute_tool(request.method, request.params)
                return MCPResponse(
                    id=request.id,
                    result=result
                )
            except Exception as e:
                logger.error(f"MCP execution error: {e}")
                return MCPResponse(
                    id=request.id,
                    error={
                        "code": -32603,
                        "message": str(e)
                    }
                )
        
        @self.app.get("/mcp/tool/{tool_name}")
        async def get_tool_info(tool_name: str):
            """Get information about a specific tool"""
            tool = self.tools.get(tool_name)
            if not tool:
                raise HTTPException(status_code=404, detail=f"Tool not found: {tool_name}")
            
            return {
                "name": tool.name,
                "description": tool.description,
                "category": tool.category,
                "manager": tool.manager,
                "security_level": tool.security_level,
                "input_schema": tool.input_schema,
                "output_schema": tool.output_schema,
                "resource_limits": tool.resource_limits
            }
        
        @self.app.get("/mcp/resource/{resource_uri:path}")
        async def get_resource(resource_uri: str):
            """Get information about a specific resource"""
            resource = self.resources.get(resource_uri)
            if not resource:
                raise HTTPException(status_code=404, detail=f"Resource not found: {resource_uri}")
            
            return {
                "uri": resource.uri,
                "name": resource.name,
                "description": resource.description,
                "mime_type": resource.mime_type,
                "size": resource.size
            }
        
        # Legacy REST API endpoints (from original system)
        @self.app.post("/execute")
        async def execute_code_legacy(code: str, language: str, timeout: Optional[int] = None):
            """Legacy code execution endpoint"""
            from app import executor
            result = executor.execute_code(
                code=code,
                language=language,
                job_id=str(uuid.uuid4()),
                timeout=timeout
            )
            return result
        
        @self.app.get("/languages")
        async def get_languages():
            """Get supported languages"""
            return {
                "languages": list(CONFIG.SAFE_EXTENSIONS.keys())
            }
        
        @self.app.get("/security/policy")
        async def get_security_policy():
            """Get security policy"""
            return {
                "max_execution_time": CONFIG.MAX_EXECUTION_TIME,
                "max_memory_mb": CONFIG.MAX_MEMORY_MB,
                "max_output_size": CONFIG.MAX_OUTPUT_SIZE,
                "security_features": [
                    "Static code analysis",
                    "Pattern-based detection", 
                    "Resource limits",
                    "Process isolation",
                    "Sandbox execution",
                    "MCP protocol support"
                ]
            }
        
        @self.app.get("/mcp/protocol-info")
        async def mcp_protocol_info():
            """Get MCP protocol information"""
            return {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {
                        "listChanged": True
                    },
                    "resources": {
                        "subscribe": False,
                        "listChanged": True
                    },
                    "logging": {},
                    "prompts": {
                        "listChanged": False
                    },
                    "sampling": {}
                },
                "serverInfo": {
                    "name": "MCP Code Interceptor Sandbox",
                    "version": "2.0.0"
                }
            }
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP tool by name"""
        
        # Find tool
        tool = self.tools.get(tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")
        
        logger.info(f"Executing tool: {tool_name} with params: {parameters}")
        
        # Get manager
        manager = None
        for mgr in self.managers.values():
            if tool.manager in mgr.__class__.__name__:
                manager = mgr
                break
        
        if not manager:
            raise ValueError(f"Manager not found for tool: {tool_name}")
        
        # Execute tool
        result = await manager.execute_tool(tool_name, parameters)
        
        # Convert to MCP result format
        if result.success:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result.data)
                    }
                ],
                "isError": False
            }
        else:
            return {
                "content": [
                    {
                        "type": "text", 
                        "text": result.error or "Unknown error"
                    }
                ],
                "isError": True
            }
    
    async def list_tools_mcp(self) -> Dict[str, Any]:
        """List all tools in MCP format"""
        tools = []
        for tool_id, tool in self.tools.items():
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema
            })
        
        return {
            "tools": tools
        }
    
    async def list_resources_mcp(self) -> Dict[str, Any]:
        """List all resources in MCP format"""
        resources = []
        for uri, resource in self.resources.items():
            resources.append({
                "uri": uri,
                "name": resource.name,
                "description": resource.description,
                "mimeType": resource.mime_type
            })
        
        return {
            "resources": resources
        }
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information"""
        return {
            "name": "MCP Code Interceptor Sandbox",
            "version": "2.0.0",
            "description": "Hybrid MCP + REST API for secure code execution",
            "managers": list(self.managers.keys()),
            "tools_count": len(self.tools),
            "resources_count": len(self.resources),
            "protocols": ["mcp", "rest"]
        }


# Create global server instance
mcp_server = MCPServer()
app = mcp_server.app


# Example MCP client integration
class MCPClient:
    """Simple MCP client implementation"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def list_tools(self):
        """List all available tools"""
        async with self.session.get(f"{self.base_url}/mcp/tools") as response:
            return await response.json()
    
    async def execute_tool(self, tool_name: str, parameters: dict):
        """Execute a tool"""
        request = {
            "jsonrpc": "2.0",
            "method": tool_name,
            "params": parameters,
            "id": 1
        }
        
        async with self.session.post(
            f"{self.base_url}/mcp/execute",
            json=request
        ) as response:
            return await response.json()
    
    async def execute_python(self, code: str, timeout: int = 30):
        """Execute Python code using MCP"""
        return await self.execute_tool("python_execute", {
            "code": code,
            "timeout": timeout
        })
    
    async def execute_bash(self, command: str, timeout: int = 30):
        """Execute bash command using MCP"""
        return await self.execute_tool("bash_execute", {
            "command": command,
            "timeout": timeout
        })
    
    async def read_file(self, path: str):
        """Read file using MCP"""
        return await self.execute_tool("file_read", {
            "path": path
        })


# Example usage
async def main():
    """Example of using the MCP client"""
    print("MCP Server is running. Use the hybrid application for full functionality.")
    # Example usage would go here
    # async with MCPClient("http://localhost:7860") as client:
    #     tools = await client.list_tools()
    #     print(f"Available tools: {len(tools['tools'])}")


if __name__ == "__main__":
    asyncio.run(main())


# Export for easy import
__all__ = ['MCPServer', 'mcp_server', 'app']