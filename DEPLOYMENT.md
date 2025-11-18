# 🌍 HuggingFace Spaces Deployment Guide

## Overview
This repository contains a **production-ready Code Interceptor + Agentic Sandbox** system specifically optimized for HuggingFace Spaces deployment. The system provides secure, multi-language code execution with comprehensive security analysis.

## 🚀 Quick Deployment to HuggingFace Spaces

### Step 1: Create a New Space
1. Go to [huggingface.co/spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Fill in the details:
   - **Space name**: `code-interceptor-sandbox` (or your preferred name)
   - **License**: `mit`
   - **SDK**: **Docker**
   - **Hardware**: **CPU basic** (recommended) or **GPU** if needed
   - **Visibility**: Public or Private

### Step 2: Upload Files
Copy all files from this repository to your Space:

```
📁 code-interceptor-sandbox/
├── 📄 app.py                     # Main FastAPI + Gradio application
├── 📄 requirements.txt           # Python dependencies
├── 📄 Dockerfile                 # Docker configuration for HF Spaces
├── 📄 .dockerignore             # Docker ignore rules
├── 📄 README.md                  # Comprehensive documentation
├── 📄 security_config.py         # Security configuration
├── 📄 static_analysis_rules.py   # Static analysis rules
├── 📄 test_sandbox.py           # Comprehensive test suite
├── 📄 deploy.sh                 # Deployment automation script
└── 📄 DEPLOYMENT.md             # This file
```

### Step 3: Automatic Build & Deploy
HF Spaces will automatically:
1. Build the Docker image using the `Dockerfile`
2. Install all dependencies from `requirements.txt`
3. Start the application on port 7860
4. Provide a public URL for access

## 🌐 Access Your Sandbox

After deployment, your Space will be available at:
```
https://your-username-code-interceptor-sandbox.hf.space
```

## 🛠️ Local Development

For local testing and development:

```bash
# Clone or download the files
cd code-interceptor-sandbox

# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py
```

The application will be available at `http://localhost:7860`

## 🔧 Configuration

### Environment Variables
Set these environment variables in HF Spaces settings:

```bash
MAX_EXECUTION_TIME=30      # Maximum execution time (seconds)
MAX_MEMORY_MB=256          # Maximum memory usage (MB)
MAX_OUTPUT_SIZE=8192       # Maximum output size (bytes)
SANDBOX_DIR=/tmp/code_sandbox  # Sandbox directory
```

### Security Settings
Edit `security_config.py` to customize:
- Security patterns and rules
- Resource limits
- Allowed file extensions
- Execution timeouts

## 📊 Features

### 🔒 Security Features
- **Multi-layer Security**: Static analysis + runtime restrictions
- **Pattern Detection**: 25+ dangerous operation patterns
- **Language-Specific Rules**: Custom rules for each language
- **Process Isolation**: Non-root execution with resource limits
- **Timeout Enforcement**: Automatic timeout and cleanup

### 💻 Supported Languages
| Language | Runtime | Extension | Features |
|----------|---------|-----------|----------|
| **Python 3** | `python3` | `.py` | Full standard library |
| **JavaScript** | `node` | `.js` | Node.js runtime |
| **Bash** | `bash` | `.sh` | Shell scripting |
| **C++** | `g++ -O2` | `.cpp` | Compilation + execution |
| **Rust** | `rustc -O` | `.rs` | Compilation + execution |

### 🎯 Use Cases
- **Educational Platforms**: Safe coding environment for students
- **Code Testing**: Automated testing and validation
- **Agent Integration**: Programmatic code execution for AI agents
- **Security Research**: Controlled environment for security analysis
- **Development Tools**: Online IDE and code playground

## 🔌 API Integration

### REST API Endpoints
```bash
# Health check
GET https://your-space.hf.space/

# Execute code
POST https://your-space.hf.space/execute
Content-Type: application/json

{
  "code": "print('Hello World')",
  "language": "python",
  "timeout": 10
}

# Get supported languages
GET https://your-space.hf.space/languages

# Get security policy
GET https://your-space.hf.space/security/policy
```

### Python Integration Example
```python
import requests

# Execute code
response = requests.post("https://your-space.hf.space/execute", json={
    "code": "result = 2 + 2\nprint(f'Result: {result}')",
    "language": "python"
})

result = response.json()
print(f"Success: {result['success']}")
print(f"Output: {result['output']}")
print(f"Security: {result['security_report']}")
```

## 🧪 Testing

Run the comprehensive test suite:
```bash
# Install test dependencies
pip install pytest

# Run tests
python test_sandbox.py

# Or with pytest
pytest test_sandbox.py -v
```

Test coverage:
- ✅ Security pattern detection
- ✅ Multi-language execution
- ✅ Resource limit enforcement
- ✅ Timeout handling
- ✅ Error handling and recovery

## 📈 Monitoring & Observability

### Health Monitoring
- Endpoint: `GET /health`
- Returns system status, limits, and supported languages

### Security Analysis
- Comprehensive security reports for each execution
- Risk scoring and severity classification
- Category-based violation breakdown

### Performance Metrics
- Execution time tracking
- Memory usage monitoring
- Output size tracking

## 🚨 Security Considerations

### What's Blocked
❌ **File System Access**: `/dev/`, `/proc/`, `/sys/`, `/etc/`
❌ **Network Operations**: `curl`, `wget`, `requests`, `fetch`
❌ **System Commands**: `sudo`, `reboot`, `kill`, `rm -rf`
❌ **Code Injection**: `eval()`, `exec()`, `os.system`
❌ **Privilege Escalation**: `chmod 777`, `chown`, `setuid`

### What's Allowed
✅ **Safe Computation**: Math operations, data processing
✅ **File I/O**: Within sandbox directory only
✅ **Standard Libraries**: Language standard libraries
✅ **Output Generation**: Console output, return values
✅ **Algorithm Implementation**: Sorting, searching, etc.

## 🔧 Customization

### Adding New Languages
1. Add language config to `LANGUAGE_CONFIGS` in `app.py`
2. Update `SECURITY_CONFIG` with language-specific rules
3. Add static analysis rules in `static_analysis_rules.py`
4. Update Dockerfile if additional dependencies needed

### Extending Security Rules
1. Edit `static_analysis_rules.py`
2. Add new `SecurityRule` instances
3. Define patterns, severity, and recommendations
4. Update language-specific rules

### Customizing Limits
Edit `security_config.py`:
```python
MAX_EXECUTION_TIME = 60  # Increase timeout
MAX_MEMORY_MB = 512      # Increase memory
MAX_OUTPUT_SIZE = 16384  # Increase output limit
```

## 🐛 Troubleshooting

### Common Issues

**Build Fails**
- Check `requirements.txt` syntax
- Verify `Dockerfile` instructions
- Ensure all dependencies are available

**Runtime Errors**
- Check security violations in response
- Verify language support
- Review timeout settings

**Performance Issues**
- Reduce execution timeouts
- Optimize code complexity
- Monitor resource usage

### Debug Mode
Set environment variable for verbose logging:
```bash
DEBUG=true
```

## 📚 Additional Resources

- **Documentation**: See `README.md` for comprehensive docs
- **API Reference**: FastAPI auto-generated docs at `/docs`
- **Security Rules**: Detailed in `static_analysis_rules.py`
- **Tests**: Full test suite in `test_sandbox.py`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure security checks pass
5. Submit a pull request

## ⚖️ License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the comprehensive README
3. Run the test suite for validation
4. Submit an issue in the repository

---

**🎉 Ready to deploy!** Your secure code execution environment is now ready for HuggingFace Spaces.