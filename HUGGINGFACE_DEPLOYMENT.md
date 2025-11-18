# 🌟 HuggingFace Spaces Deployment Guide

## Quick Deployment

### Step 1: Create New Space
1. Go to [HuggingFace Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Choose repository: `https://github.com/likhonsdevbd/hybrid-code-interceptor-sandbox.git`
4. Select **CPU** hardware (recommended)
5. Space name: `hybrid-code-interceptor-sandbox`
6. Click "Create Space"

### Step 2: Auto-Build
- HuggingFace will automatically:
  - Clone the repository
  - Run `pip install -r requirements.txt`
  - Execute the Dockerfile
  - Start the application on port 7860

### Step 3: Access
- Your space will be available at:
- `https://your-space-name.hf.space`
- The system will be ready with:
  - **Web UI**: Gradio interface
  - **API**: FastAPI endpoints
  - **MCP Server**: Protocol integration

## 🔧 Manual Deployment

If you prefer manual setup:

### Local Testing
```bash
# Clone repository
git clone https://github.com/likhonsdevbd/hybrid-code-interceptor-sandbox.git
cd hybrid-code-interceptor-sandbox

# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py
```

### Docker Deployment
```bash
# Build image
docker build -t hybrid-sandbox .

# Run container
docker run -p 7860:7860 hybrid-sandbox
```

## 📊 Expected Performance

- **Cold Start**: ~30-60 seconds
- **API Response**: <2 seconds
- **Web UI**: Immediate after load
- **Memory Usage**: ~256MB
- **CPU**: Single core recommended

## 🔗 Your Repository
- **GitHub**: https://github.com/likhonsdevbd/hybrid-code-interceptor-sandbox
- **License**: MIT
- **Status**: Production Ready ✅