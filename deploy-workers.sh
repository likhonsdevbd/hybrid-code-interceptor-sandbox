#!/bin/bash

# Cloudflare Workers Deployment Script
# Usage: ./deploy-workers.sh [environment]

set -e

ENVIRONMENT=${1:-production}
PROJECT_NAME="hybrid-code-interceptor-sandbox-cf"

echo "🚀 Deploying Hybrid Code Interceptor to Cloudflare Workers"
echo "Environment: $ENVIRONMENT"
echo "Project: $PROJECT_NAME"
echo ""

# Check if wrangler is installed
if ! command -v wrangler &> /dev/null; then
    echo "❌ Wrangler CLI not found!"
    echo "Install it with: npm install -g wrangler"
    exit 1
fi

# Check if logged in
echo "🔐 Checking Cloudflare authentication..."
wrangler whoami > /dev/null || {
    echo "❌ Not logged in to Cloudflare!"
    echo "Login with: wrangler login"
    exit 1
}

echo "✅ Authentication verified"
echo ""

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Run tests
echo "🧪 Running tests..."
npm run test || {
    echo "❌ Tests failed!"
    exit 1
}

# Type check
echo "🔍 Type checking..."
npm run type-check || {
    echo "❌ Type check failed!"
    exit 1
}

# Build project
echo "🏗️ Building project..."
npm run build

# Deploy
echo "🚀 Deploying to $ENVIRONMENT..."
wrangler deploy --env "$ENVIRONMENT"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🔗 Your Worker is now available at:"
echo "   https://$PROJECT_NAME.$ENVIRONMENT.workers.dev"
echo ""
echo "📊 Check the dashboard: https://dash.cloudflare.com"
echo "📖 View logs: wrangler tail"
echo ""
echo "Next steps:"
echo "1. Set environment variables: wrangler secret put ENVIRONMENT"
echo "2. Create D1 database (optional): wrangler d1 create execution_logs"
echo "3. Apply schema: wrangler d1 execute execution_logs --file=./migrations/0001_initial_schema.sql"
echo "4. Test the API: curl https://$PROJECT_NAME.$ENVIRONMENT.workers.dev/"
echo ""
echo "🌐 API Endpoints:"
echo "   GET  /           - Health check"
echo "   POST /execute    - Execute JavaScript"
echo "   GET  /languages  - Available languages"
echo "   GET  /security/policy - Security policy"
echo "   GET  /ui         - Web interface"