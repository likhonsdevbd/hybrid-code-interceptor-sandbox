# 🎉 MCP Code Interceptor + Agentic Sandbox - Hybrid Architecture

## ✅ What I've Built

I've successfully created a **groundbreaking hybrid architecture** that combines:

1. **Original HF Spaces System** - Secure, multi-language code execution with comprehensive security analysis
2. **MCP Protocol Integration** - Standardized tool discovery and execution for AI agents
3. **Domain-Specific Managers** - Specialized security-aware managers for different operation types
4. **Dual Interface Support** - Both REST API (for humans) and MCP protocol (for AI agents)

## 🚀 Key Features Delivered

### 🛡️ Security-First Design
- **Multi-layer security**: Static analysis + runtime restrictions + process isolation
- **25+ security patterns**: Comprehensive threat detection
- **AST analysis**: Language-specific security validation
- **Resource controls**: CPU, memory, and I/O limitations

### 🤖 AI Agent Integration (NEW)
- **MCP Protocol**: Standardized tool discovery and execution
- **Domain Managers**: BashManager, PythonManager, FileManager, WebManager, KnowledgeBaseManager
- **JSON-RPC 2.0**: Standard MCP protocol implementation
- **Async execution**: Non-blocking tool execution

### 💻 Multi-Language Support
- **Python 3**: Full standard library support
- **JavaScript**: Node.js runtime
- **Bash**: Shell scripting
- **C++**: Compilation + execution
- **Rust**: Compilation + execution

### 🌐 Dual Interface
- **REST API**: Legacy interface for traditional applications
- **MCP Protocol**: AI agent interface for modern AI systems
- **Gradio UI**: Human-friendly web interface
- **WebSocket**: Real-time streaming support

## 📁 Complete File Structure

```
📦 MCP Code Interceptor Sandbox/
├── 📄 app.py                    # Original FastAPI application
├── 📄 hybrid_app.py             # NEW: Hybrid MCP + REST application  
├── 📄 mcp_server.py             # NEW: MCP protocol server
├── 📄 mcp_managers.py           # NEW: Domain-specific managers
├── 📄 security_config.py        # Security configuration system
├── 📄 static_analysis_rules.py  # Enhanced security rules
├── 📄 test_sandbox.py           # Comprehensive test suite
├── 📄 deploy.sh                 # Deployment automation script
├── 📄 example_config.py         # Configuration examples
├── 📄 requirements.txt          # Updated dependencies
├── 📄 Dockerfile                # Enhanced for MCP support
├── 📄 .dockerignore             # Docker optimization
├── 📄 README.md                 # Comprehensive documentation
├── 📄 DEPLOYMENT.md             # HF Spaces deployment guide
├── 📄 HYBRID_ARCHITECTURE.md    # NEW: Architecture documentation
└── 📄 HYBRID_README.md          # This summary document
```

## 🏗️ Architecture Summary

```
┌─────────────────────────────────────────────────────────┐
│                  Hybrid Application                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │ REST API    │  │ MCP Protocol│  │   Gradio UI     │ │
│  │ (Legacy)    │  │ (AI Agents) │  │   (Human)       │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
                  ┌───────────────┐
                  │ MCP Server    │
                  │ Core Engine   │
                  └───────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼──────┐ ┌────────▼─────┐ ┌────────▼─────┐
│ Security     │ │ Domain       │ │ Resource     │
│ Analysis     │ │ Managers     │ │ Management   │
└──────────────┘ └──────────────┘ └──────────────┘
```

## 🔧 Domain-Specific Managers

### 1. BashManager
- **Purpose**: Secure bash command execution
- **Tools**: `bash_execute`, `bash_validate`
- **Security**: Command pattern validation, system access prevention

### 2. PythonManager
- **Purpose**: Sandboxed Python code execution
- **Tools**: `python_execute`, `python_analyze`
- **Security**: Import validation, dangerous function detection

### 3. FileManager
- **Purpose**: Safe file operations
- **Tools**: `file_read`, `file_write`, `file_list`
- **Security**: Sandbox directory enforcement

### 4. WebManager
- **Purpose**: Secure web browsing and scraping
- **Tools**: `web_fetch`, `web_search`
- **Security**: URL validation, internal network blocking

### 5. KnowledgeBaseManager
- **Purpose**: Structured document storage
- **Tools**: `kb_store`, `kb_search`
- **Security**: Content validation, metadata sanitization

## 🚀 Quick Start Guide

### For HuggingFace Spaces Deployment

1. **Create New Space**
   - Go to [huggingface.co/spaces](https://huggingface.co/spaces)
   - Choose **Docker** SDK
   - Select **CPU** hardware (recommended)

2. **Upload Files**
   - Copy all files from this repository to your Space
   - The system will automatically build and deploy

3. **Access Your Sandbox**
   - Your Space will be available at: `https://username-sandbox-name.hf.space`
   - Both REST API and MCP protocol will be available

### For Local Development

```bash
# Clone or download files
cd mcp-code-sandbox

# Install dependencies
pip install -r requirements.txt

# Run hybrid application
python hybrid_app.py

# Access at http://localhost:7860
```

### For Docker Deployment

```bash
# Build image
docker build -t mcp-sandbox .

# Run container
docker run -p 7860:7860 mcp-sandbox
```

## 🔌 API Usage Examples

### REST API (Legacy Interface)
```bash
# Execute Python code
curl -X POST "http://localhost:7860/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"Hello from REST API\")",
    "language": "python",
    "timeout": 30
  }'

# Get supported languages
curl "http://localhost:7860/languages"
```

### MCP Protocol (AI Agents)
```bash
# List available tools
curl "http://localhost:7860/mcp/tools"

# Execute tool (JSON-RPC 2.0)
curl -X POST "http://localhost:7860/mcp/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "python_execute",
    "params": {
      "code": "print(\"Hello from MCP\")",
      "timeout": 30
    },
    "id": 1
  }'
```

### Python Client Example
```python
import asyncio
import aiohttp

async def example():
    async with aiohttp.ClientSession() as session:
        # MCP execution
        result = await session.post("http://localhost:7860/mcp/execute", json={
            "jsonrpc": "2.0",
            "method": "python_execute",
            "params": {"code": "print('Hello AI!')", "timeout": 30},
            "id": 1
        })
        data = await result.json()
        print(f"MCP Result: {data}")

asyncio.run(example())
```

## 🛠️ Configuration Options

### Environment Variables
```bash
MAX_EXECUTION_TIME=30      # Max execution time (seconds)
MAX_MEMORY_MB=256          # Max memory usage (MB)
MAX_OUTPUT_SIZE=8192       # Max output size (bytes)
SANDBOX_DIR=/tmp/code_sandbox  # Sandbox directory
```

### Security Customization
Edit `security_config.py` to modify:
- Security patterns and rules
- Resource limits
- Language-specific restrictions
- Complexity thresholds

## 🧪 Testing

### Run Comprehensive Tests
```bash
# Basic functionality tests
python test_sandbox.py

# MCP protocol tests
python -c "
import asyncio
from mcp_server import mcp_server

async def test():
    result = await mcp_server.execute_tool('python_execute', {
        'code': 'print(\"Test successful\")',
        'timeout': 10
    })
    print(f'MCP Test: {result}')

asyncio.run(test())
"
```

## 🔐 Security Highlights

### What's Blocked
- ❌ System file access (`/dev/`, `/proc/`, `/sys/`)
- ❌ Network operations (`curl`, `wget`, `requests`)
- ❌ System commands (`sudo`, `reboot`, `rm -rf`)
- ❌ Code injection (`eval()`, `exec()`, `os.system`)
- ❌ Privilege escalation (`chmod 777`, `chown`)

### What's Allowed
- ✅ Safe computation (math, data processing)
- ✅ File I/O within sandbox directory
- ✅ Standard language libraries
- ✅ Algorithm implementation
- ✅ Output generation and analysis

## 🎯 Perfect For

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

## 🆕 What's NEW in Version 2.0

### MCP Protocol Integration
- ✅ Full MCP 2024-11-05 protocol support
- ✅ JSON-RPC 2.0 implementation
- ✅ Standardized tool discovery
- ✅ Async execution support

### Domain-Specific Managers
- ✅ 5 specialized managers
- ✅ Security-aware operations
- ✅ Resource management
- ✅ Protocol compliance

### Enhanced Security
- ✅ Static analysis rules engine
- ✅ AST-based detection
- ✅ Risk scoring system
- ✅ Security reporting

### Hybrid Architecture
- ✅ Dual protocol support
- ✅ Backward compatibility
- ✅ Enhanced Gradio UI
- ✅ Comprehensive documentation

## 🚀 Ready to Deploy!

This hybrid architecture represents the **next generation of secure, AI-ready code execution environments**. It successfully combines:

1. **Proven Security**: Multi-layer security from the original system
2. **AI Integration**: MCP protocol for modern AI agents
3. **Flexibility**: Both REST API and MCP protocol support
4. **Scalability**: Domain-specific managers for modularity
5. **Usability**: Enhanced Gradio UI for human interaction

### Next Steps
1. **Deploy to HuggingFace Spaces** using the provided files
2. **Integrate with AI agents** using the MCP protocol
3. **Customize security rules** for your specific use case
4. **Extend with new managers** for specialized operations

**🌟 This system is ready for production use and sets a new standard for secure, AI-integrated code execution environments!**

---

*Built with ❤️ for the future of secure AI-powered development environments.*