# 🤖 Hybrid MCP + REST API Architecture

## Overview

The **MCP Code Interceptor + Agentic Sandbox** is a groundbreaking hybrid architecture that combines the best of both worlds:

1. **REST API Interface**: Direct, simple API access for traditional applications
2. **MCP Protocol**: Standardized tool discovery and execution for AI agents

This hybrid approach serves both human users and AI agents seamlessly within the HuggingFace Spaces environment.

## 🏗️ Architecture Components

### Core System
```
┌─────────────────────────────────────────────────────────────┐
│                    Hybrid Application                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  REST API       │  │  MCP Protocol   │  │  Gradio UI   │ │
│  │  (Legacy)       │  │  (AI Agents)    │  │  (Human)     │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────────────┐
                    │  MCP Server     │
                    │  Core Engine    │
                    └─────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐  ┌────────▼───────┐  ┌─────────▼──────┐
│ Domain Managers │  │ Security       │  │ Resource       │
│  - BashManager  │  │ - Static       │  │ - File System  │
│  - PythonManager│  │ - Runtime      │  │ - Memory       │
│  - FileManager  │  │ - Pattern      │  │ - CPU          │
│  - WebManager   │  │ - AST          │  │ - Network      │
│  - KnowledgeMgr │  └────────────────┘  └────────────────┘
└─────────────────┘
```

### Domain-Specific Managers

#### 1. **BashManager** - Secure Command Execution
- **Tools**: `bash_execute`, `bash_validate`
- **Security**: Command pattern validation, system access prevention
- **Use Cases**: Shell scripting, system administration, automation

#### 2. **PythonManager** - Sandboxed Python Execution  
- **Tools**: `python_execute`, `python_analyze`
- **Security**: Import validation, dangerous function detection
- **Use Cases**: Data processing, algorithm implementation, AI/ML code

#### 3. **FileManager** - Safe File Operations
- **Tools**: `file_read`, `file_write`, `file_list`
- **Security**: Sandbox directory enforcement, path validation
- **Use Cases**: Data storage, configuration management, document processing

#### 4. **WebManager** - Secure Web Operations
- **Tools**: `web_fetch`, `web_search` 
- **Security**: URL validation, internal network blocking
- **Use Cases**: Data scraping, API calls, information retrieval

#### 5. **KnowledgeBaseManager** - Structured Document Storage
- **Tools**: `kb_store`, `kb_search`
- **Security**: Content validation, metadata sanitization
- **Use Cases**: Knowledge management, document indexing, semantic search

## 🔌 Protocol Support

### REST API (Legacy Interface)
```bash
# Code execution
POST /execute
{
  "code": "print('Hello')",
  "language": "python",
  "timeout": 30
}

# System info
GET /languages
GET /security/policy
GET /health
```

### MCP Protocol (AI Agent Interface)
```bash
# Tool discovery
GET /mcp/tools
GET /mcp/resources

# Tool execution (JSON-RPC 2.0)
POST /mcp/execute
{
  "jsonrpc": "2.0",
  "method": "python_execute",
  "params": {
    "code": "print('Hello from MCP')",
    "timeout": 30
  },
  "id": 1
}

# Protocol info
GET /mcp/protocol-info
```

## 🛠️ MCP Tool Reference

### Code Execution Tools

#### `python_execute`
Execute Python code with security analysis.
```json
{
  "code": "import math\nprint(math.sqrt(16))",
  "timeout": 30,
  "packages": ["numpy"]
}
```

#### `bash_execute`
Execute bash commands safely.
```json
{
  "command": "echo 'Hello World' && date",
  "timeout": 15,
  "working_directory": "/tmp"
}
```

### File Operations Tools

#### `file_write`
Write content to sandbox files.
```json
{
  "path": "/tmp/code_sandbox/output.txt",
  "content": "Hello from file operation",
  "encoding": "utf-8"
}
```

#### `file_read`
Read content from sandbox files.
```json
{
  "path": "/tmp/code_sandbox/data.txt",
  "encoding": "utf-8"
}
```

### Security Analysis Tools

#### `python_analyze`
Analyze Python code for security issues.
```json
{
  "code": "import os\nos.system('echo test')"
}
```

#### `bash_validate`
Validate bash commands for security.
```json
{
  "command": "rm -rf /tmp/test"
}
```

## 🤖 AI Agent Integration

### Example: Claude Desktop Integration
```json
{
  "mcpServers": {
    "code-sandbox": {
      "command": "python",
      "args": ["-m", "uvicorn", "mcp_server:app", "--host", "0.0.0.0", "--port", "3000"],
      "env": {
        "MAX_EXECUTION_TIME": "30",
        "MAX_MEMORY_MB": "256"
      }
    }
  }
}
```

### Example: Python Client Integration
```python
import asyncio
import aiohttp
from mcp_client import MCPClient

async def main():
    async with MCPClient("http://localhost:7860") as client:
        # Execute Python code
        result = await client.execute_python('''
import json
data = {"message": "Hello from AI", "tools": ["python", "bash"]}
print(json.dumps(data, indent=2))
        ''')
        
        print(f"Result: {result}")

asyncio.run(main())
```

## 🔐 Security Model

### Multi-Layer Security
1. **Static Analysis**: Pattern matching, AST analysis, complexity scoring
2. **Runtime Protection**: Resource limits, process isolation, timeout enforcement
3. **Network Security**: Internal address blocking, HTTPS enforcement
4. **File System Security**: Sandbox directory enforcement, path validation

### Security Levels
- **CRITICAL**: System commands, privilege escalation, code injection
- **HIGH**: File system access, network operations, unsafe functions
- **MEDIUM**: Import operations, reflection, deserialization
- **LOW**: Debug output, non-critical operations

### Resource Limits
- **Execution Time**: 30 seconds (configurable)
- **Memory Usage**: 256 MB (configurable)
- **Output Size**: 8KB (configurable)
- **File Operations**: Sandbox directory only

## 📊 Monitoring & Observability

### Health Endpoints
- `GET /` - Basic health check
- `GET /health` - Detailed system status
- `GET /mcp/protocol-info` - MCP protocol capabilities

### Security Reporting
Each execution includes comprehensive security analysis:
- Security violations with line numbers
- Risk scoring (0-100)
- Severity breakdown
- Recommendations
- Complexity metrics

### Performance Metrics
- Execution time tracking
- Resource usage monitoring
- Success/failure rates
- Tool usage statistics

## 🚀 Deployment Options

### HuggingFace Spaces (Recommended)
```bash
# Create new Space
1. Go to huggingface.co/spaces
2. Choose Docker SDK
3. Upload all files from repository
4. Deploy automatically
```

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run hybrid application
python hybrid_app.py

# Or run MCP server only
python -m uvicorn mcp_server:app --reload
```

### Docker Deployment
```bash
# Build image
docker build -t mcp-sandbox .

# Run container
docker run -p 7860:7860 mcp-sandbox

# With custom environment
docker run -p 7860:7860 \
  -e MAX_EXECUTION_TIME=60 \
  -e MAX_MEMORY_MB=512 \
  mcp-sandbox
```

## 🔧 Configuration

### Environment Variables
```bash
MAX_EXECUTION_TIME=30      # Maximum execution time (seconds)
MAX_MEMORY_MB=256          # Maximum memory usage (MB)
MAX_OUTPUT_SIZE=8192       # Maximum output size (bytes)
SANDBOX_DIR=/tmp/code_sandbox  # Sandbox directory path
```

### Security Configuration
Modify `security_config.py` to customize:
- Security patterns and rules
- Resource limits
- Language-specific restrictions
- Complexity thresholds

### Manager Configuration
Each manager can be customized in `mcp_managers.py`:
- Tool definitions
- Security validation rules
- Resource constraints
- Timeout settings

## 🧪 Testing

### Unit Tests
```bash
# Run comprehensive test suite
python test_sandbox.py

# Run with pytest
pytest test_sandbox.py -v
```

### MCP Integration Tests
```bash
# Test MCP protocol
python -c "
import asyncio
from mcp_server import mcp_server

async def test():
    result = await mcp_server.execute_tool('python_execute', {
        'code': 'print(\"Test\")',
        'timeout': 10
    })
    print(f'MCP Test: {result}')

asyncio.run(test())
"
```

### Load Testing
```bash
# Test concurrent executions
python -c "
import asyncio
import aiohttp

async def stress_test():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(10):
            task = session.post('http://localhost:7860/execute', json={
                'code': f'print(\"Test {i}\")',
                'language': 'python'
            })
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        print(f'Stress test completed: {len(results)} requests')

asyncio.run(stress_test())
"
```

## 🎯 Use Cases

### Educational Platforms
- Safe coding environment for students
- Interactive programming tutorials
- Security-conscious learning tools

### AI Agent Integration
- Standardized tool interface for AI systems
- Secure code execution for AI workflows
- Protocol-compliant agent communication

### Development Tools
- Online IDE and code playground
- Automated testing environment
- Code analysis and validation

### Research Applications
- Controlled environment for security research
- Algorithm testing and benchmarking
- Data processing and analysis

## 🔮 Future Enhancements

### Planned Features
1. **Advanced AI Integration**: Support for more AI frameworks
2. **Enhanced Security**: Machine learning-based threat detection
3. **Distributed Execution**: Multi-node sandbox coordination
4. **Advanced Monitoring**: Real-time security dashboards
5. **Custom Managers**: User-defined domain-specific managers

### Performance Optimizations
1. **Caching**: Result caching for repeated operations
2. **Container Orchestration**: Kubernetes-based scaling
3. **Resource Pooling**: Pre-initialized execution environments
4. **Load Balancing**: Intelligent request distribution

## 📚 Documentation

- **README.md**: Comprehensive project documentation
- **DEPLOYMENT.md**: HuggingFace Spaces deployment guide
- **API Documentation**: Auto-generated FastAPI docs at `/docs`
- **MCP Specification**: Protocol documentation and examples

## 🤝 Contributing

1. **Fork Repository**: Create your own fork
2. **Create Feature Branch**: `git checkout -b feature/amazing-feature`
3. **Add Tests**: Ensure comprehensive test coverage
4. **Security Review**: Run security analysis tools
5. **Submit PR**: Include detailed description and examples

## ⚖️ License

MIT License - see LICENSE file for details.

---

**🌟 Ready to Experience the Future of Code Execution!**

This hybrid architecture represents the next generation of secure, AI-ready code execution environments, combining proven security practices with modern AI agent integration standards.