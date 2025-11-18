# Cloudflare Workers Deployment

This is a Cloudflare Workers version of the Hybrid Code Interceptor + Agentic Sandbox system.

## ⚠️ Important Limitations

Unlike the full Python version, the Cloudflare Workers version has significant limitations:

### 🚫 **What Won't Work**
- **Python execution** - Workers only support JavaScript
- **Subprocess spawning** - No `subprocess`, `exec`, `system` calls
- **File system access** - No persistent file operations
- **Full language support** - Only JavaScript execution
- **Complex resource monitoring** - Limited to Workers' built-in limits

### ✅ **What's Supported**
- **JavaScript execution** with security scanning
- **Pattern-based detection** of dangerous operations
- **Basic timeout enforcement** (up to 30 seconds)
- **Security violation reporting**
- **RESTful API** endpoints
- **Simple web UI** for testing

## 🛠️ Development Setup

### Prerequisites
```bash
# Install Node.js (v16+)
node --version

# Install Wrangler CLI
npm install -g wrangler

# Login to Cloudflare
wrangler login
```

### Local Development
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Test locally at
# http://localhost:8787
```

### Deploy to Cloudflare Workers
```bash
# Deploy to production
npm run deploy

# Or deploy to specific environment
wrangler deploy --env production
```

## 🗄️ Database Setup (Optional)

### D1 Database
```bash
# Create D1 database
wrangler d1 create execution_logs

# Apply schema
wrangler d1 execute execution_logs --local --file=./migrations/0001_initial_schema.sql

# Apply to production
wrangler d1 execute execution_logs --file=./migrations/0001_initial_schema.sql
```

### Configure Environment
Update `wrangler.toml` with your database ID:
```toml
[[env.production.d1_databases]]
binding = "DB"
database_name = "execution_logs"
database_id = "your-database-id"
```

## 🔧 Environment Variables

### Required
```bash
# Set via Wrangler CLI
wrangler secret put ENVIRONMENT
wrangler secret put MAX_EXECUTION_TIME
wrangler secret put MAX_MEMORY_MB
```

### Optional
```bash
# For enhanced logging
wrangler secret put DATABASE_URL
wrangler secret put LOG_LEVEL
```

## 🌐 API Endpoints

### Health Check
```bash
curl https://your-worker.workers.dev/
```

### Execute JavaScript
```bash
curl -X POST https://your-worker.workers.dev/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "console.log(\"Hello World\"); 2 + 2",
    "language": "javascript",
    "timeout": 10
  }'
```

### Get Languages
```bash
curl https://your-worker.workers.dev/languages
```

### Security Policy
```bash
curl https://your-worker.workers.dev/security/policy
```

## 🎨 Web Interface

Access the simple web UI at:
```
https://your-worker.workers.dev/ui
```

## 📊 Security Features

### Pattern Detection
The system scans for these dangerous patterns:
- `eval()`, `Function()` - Dynamic code execution
- `fetch()`, `XMLHttpRequest` - Network requests
- `process.`, `global.` - System access
- `import`, `require` - Module loading
- Infinite loops - `while(true)`, `for(;;)`

### Severity Levels
- **High**: Blocks execution immediately
- **Medium**: Allows with warnings
- **Low**: Informational only

### Resource Limits
- **Timeout**: 10-30 seconds (configurable)
- **Output Size**: 8KB max
- **Complexity Score**: 100 max points

## 🏗️ Architecture

```
Cloudflare Workers
├── Request Router
├── Security Analyzer
│   ├── Pattern Detection
│   ├── Complexity Scoring
│   └── Violation Reporting
├── Code Executor
│   ├── JavaScript Sandbox
│   ├── Timeout Enforcement
│   └── Output Capture
└── Response Handler
    ├── CORS Headers
    ├── JSON Response
    └── Error Handling
```

## 📈 Monitoring

### Workers Analytics
Access Cloudflare Workers Analytics in your dashboard:
- Request counts
- Error rates
- Execution times
- Resource usage

### D1 Database (Optional)
Query execution statistics:
```sql
SELECT * FROM execution_stats ORDER BY date DESC LIMIT 10;
```

## 🚀 Performance

### Expected Performance
- **Cold Start**: ~100-500ms
- **Warm Requests**: ~10-50ms
- **JavaScript Execution**: ~5-20ms
- **Security Analysis**: ~1-5ms

### Scalability
- **Automatic scaling** to thousands of requests
- **Global CDN** distribution
- **No server maintenance** required

## 🔒 Security Considerations

### Cloudflare Workers Security
- **Isolated runtime** per request
- **No persistent state** between requests
- **Automatic DDoS protection**
- **SSL/TLS encryption** by default

### Application Security
- **Input validation** for all endpoints
- **CORS protection** configured
- **Timeout enforcement** prevents infinite loops
- **Pattern scanning** blocks dangerous operations

## 🐛 Troubleshooting

### Common Issues

**"Function timeout"**
- Reduce code complexity
- Remove infinite loops
- Lower timeout value

**"Security violation"**
- Remove `eval()`, `fetch()`, `process.`
- Check security report for line numbers
- See `/security/policy` for rules

**"Out of memory"**
- Reduce output size
- Optimize data structures
- Lower complexity score

**"CORS errors"**
- Check `Access-Control-Allow-Origin` header
- Verify request method/headers
- Test with curl first

### Debug Mode
Set `ENVIRONMENT=development` to enable:
- Detailed error messages
- Extended logging
- Debug information in responses

## 📋 Migration from Python Version

If migrating from the full Python version:

### Changes Required
1. **Languages**: Only JavaScript supported
2. **Libraries**: No external libraries
3. **Storage**: Use D1 database or KV storage
4. **UI**: Simplified HTML instead of Gradio
5. **Deployment**: Cloudflare Workers instead of Docker

### Data Migration
- No automatic migration available
- Export logs from Python version
- Import to D1 database manually
- Recreate API clients for Workers API

## 🔗 Links

- **Cloudflare Workers**: https://workers.cloudflare.com/
- **Wrangler Documentation**: https://developers.cloudflare.com/workers/wrangler/
- **Workers Examples**: https://github.com/cloudflare/workers-examples
- **D1 Database**: https://developers.cloudflare.com/d1/

---

**Note**: This is a simplified version for Cloudflare Workers deployment. For full functionality, use the Python version with Docker or HuggingFace Spaces.