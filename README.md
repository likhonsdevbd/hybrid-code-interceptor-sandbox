# 🔒 Code Interceptor + Agentic Sandbox

A production-ready, secure code execution environment designed for HuggingFace Spaces. This system provides comprehensive security analysis, process isolation, and multi-language support for safe code execution.

## 🚀 Features

- **🛡️ Security-First Design**: Multi-layer security with static analysis and runtime restrictions
- **🔍 Static Code Analysis**: Pattern-based detection of dangerous operations
- **⚡ Multi-Language Support**: Python, JavaScript, Bash, C++, Rust
- **⏱️ Resource Controls**: CPU time, memory, and output size limits
- **🔄 Process Isolation**: Secure execution without container dependencies
- **📊 Real-time Monitoring**: Execution tracking and security reporting
- **🤖 Agent-Friendly API**: RESTful interface designed for automation

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI +     │    │   Security      │    │   Sandbox       │
│   Gradio UI     │────│   Interceptor   │────│   Executor      │
│                 │    │                 │    │                 │
│ - REST API      │    │ - Pattern Match │    │ - Process Ctrl  │
│ - WebSocket     │    │ - AST Analysis  │    │ - Resource Limit│
│ - Gradio UI     │    │ - Complexity    │    │ - Isolation     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔐 Security Features

### Static Analysis
- **Pattern Detection**: Regex-based matching for dangerous operations
- **AST Analysis**: Abstract Syntax Tree parsing for Python
- **Complexity Scoring**: Code complexity and length validation
- **Language-Specific Rules**: Custom rules per programming language

### Runtime Protection
- **Process Isolation**: Non-root user execution
- **Resource Limits**: CPU, memory, and I/O restrictions
- **Timeout Enforcement**: Configurable execution timeouts
- **Output Sanitization**: Large output truncation and monitoring

### Security Patterns Detected
- File system operations (`/dev/`, `/proc/`, `/sys/`)
- Network operations (`nc`, `curl`, `wget`, `requests`)
- System operations (`sudo`, `reboot`, `shutdown`)
- Privilege escalation (`chmod 777`, `chown`)
- Code injection (`eval()`, `exec()`, `os.system`)
- Cryptographic operations (`hashlib.md5`, `hashlib.sha1`)

## 🛠️ Installation & Deployment

### For HuggingFace Spaces

1. **Create a new Space** on HuggingFace Spaces
2. **Choose Hardware**: CPU or GPU (CPU recommended for this application)
3. **Set Build Command**: Leave empty (uses Dockerfile)
4. **Add Files**: Copy all files from this repository

### Local Development

```bash
# Clone repository
git clone <repository-url>
cd code-interceptor-sandbox

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

### Docker Deployment

```bash
# Build image
docker build -t code-sandbox .

# Run container
docker run -p 7860:7860 code-sandbox
```

## 📚 API Documentation

### REST Endpoints

#### `GET /`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "service": "Code Interceptor Sandbox",
  "version": "1.0.0",
  "timestamp": "2025-11-18T12:49:34Z"
}
```

#### `POST /execute`
Execute code in secure sandbox

**Request:**
```json
{
  "code": "print('Hello World')",
  "language": "python",
  "timeout": 10
}
```

**Response:**
```json
{
  "success": true,
  "output": "Hello World\n",
  "error": "",
  "exit_code": 0,
  "execution_time": 0.123,
  "security_report": {
    "allowed": true,
    "violations": [],
    "complexity_score": 1
  }
}
```

#### `GET /languages`
Get supported programming languages

**Response:**
```json
{
  "languages": [
    {
      "name": "python",
      "command": "python3",
      "file_extension": ".py",
      "timeout_multiplier": 1.0
    }
  ]
}
```

#### `GET /security/policy`
Get security policy information

**Response:**
```json
{
  "max_execution_time": 30,
  "max_memory_mb": 256,
  "max_output_size": 8192,
  "dangerous_patterns_count": 25,
  "security_features": [
    "Static code analysis",
    "Pattern-based detection",
    "Resource limits",
    "Process isolation",
    "Sandbox execution"
  ]
}
```

## 🌍 Supported Languages

| Language | Command | Extension | Timeout Multiplier |
|----------|---------|-----------|-------------------|
| Python   | `python3` | `.py` | 1.0x |
| JavaScript | `node` | `.js` | 1.0x |
| Bash | `bash` | `.sh` | 1.0x |
| C++ | `g++ -O2 -std=c++17` | `.cpp` | 2.0x |
| Rust | `rustc -O` | `.rs` | 2.0x |

## 🔧 Configuration

### Environment Variables

- `MAX_EXECUTION_TIME`: Maximum execution time in seconds (default: 30)
- `MAX_MEMORY_MB`: Maximum memory usage in MB (default: 256)
- `MAX_OUTPUT_SIZE`: Maximum output size in bytes (default: 8192)
- `SANDBOX_DIR`: Sandbox directory path (default: `/tmp/code_sandbox`)

### Security Settings

Edit `app.py` to customize:

```python
# Security Configuration
MAX_EXECUTION_TIME = 30  # seconds
MAX_MEMORY_MB = 256
MAX_OUTPUT_SIZE = 8192  # bytes
```

## 🧪 Usage Examples

### Python Example
```python
print("Secure Python execution!")
import json
data = {"message": "Hello from sandbox"}
print(json.dumps(data, indent=2))
```

### JavaScript Example
```javascript
console.log("Secure JavaScript execution!");
const data = { message: "Hello from sandbox", timestamp: new Date() };
console.log(JSON.stringify(data, null, 2));
```

### Bash Example
```bash
#!/bin/bash
echo "Secure Bash execution!"
echo "Current directory: $(pwd)"
echo "User: $(whoami)"
```

## 🚫 Security Restrictions

The following operations are **blocked** for security:

- File system access to `/dev/`, `/proc/`, `/sys/`
- Network operations (`nc`, `curl`, `wget`, network requests)
- System operations (`sudo`, `reboot`, `shutdown`)
- Privilege escalation (`chmod 777`, `chown`)
- Dynamic code execution (`eval()`, `exec()`, `os.system`)
- Cryptographic operations using weak algorithms
- Database connections
- Process spawning beyond basic execution

## 📈 Monitoring & Logging

### Execution Metrics
- Execution time
- Memory usage
- Output size
- Exit codes
- Security violations

### Security Reporting
- Pattern violations
- AST analysis results
- Complexity scores
- Recommendations

## 🔄 Integration with Agents

### Basic Integration
```python
import requests

# Execute code
response = requests.post("https://your-space.hf.space/execute", json={
    "code": "print('Hello from agent!')",
    "language": "python"
})

result = response.json()
if result["success"]:
    print(result["output"])
else:
    print(f"Error: {result['error']}")
```

### Security Analysis
```python
# Get security report
result = executor.execute_code(code, language)
if result["security_report"]["violations"]:
    print("Security warnings detected")
    for violation in result["security_report"]["violations"]:
        print(f"Line {violation['line']}: {violation['pattern']}")
```

## 🛡️ Production Considerations

### For Production Deployment
1. **Container Orchestration**: Use Kubernetes for scaling
2. **Database Integration**: Add persistent storage for audit logs
3. **Monitoring**: Integrate with Prometheus/Grafana
4. **Authentication**: Add JWT-based API authentication
5. **Rate Limiting**: Implement request throttling
6. **WebSocket Support**: Add real-time execution streaming

### Security Hardening
1. **Network Isolation**: Deploy in isolated network segments
2. **Image Scanning**: Regular vulnerability scans
3. **Audit Logging**: Comprehensive security event logging
4. **Regular Updates**: Keep dependencies updated
5. **Penetration Testing**: Regular security assessments

## 🐛 Troubleshooting

### Common Issues

**"Language not supported"**
- Check if language is in `LANGUAGE_CONFIGS`
- Verify language name spelling

**"Security violation detected"**
- Review code for dangerous patterns
- Check security violations in response
- Modify code to remove blocked operations

**"Execution timeout"**
- Reduce code complexity
- Decrease timeout value
- Check for infinite loops

**"Memory limit exceeded"**
- Optimize memory usage
- Increase memory limit if safe
- Review data structures

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure security checks pass
5. Submit a pull request

## ⚠️ Disclaimer

This sandbox is designed for educational and development purposes. While it includes multiple security layers, no system is 100% secure. Always review and test code before execution in production environments.