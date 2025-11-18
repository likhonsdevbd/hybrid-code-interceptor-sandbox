#!/bin/bash

# Deployment script for Code Interceptor + Agentic Sandbox
# Handles both local development and HuggingFace Spaces deployment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're on HuggingFace Spaces
is_hf_spaces() {
    [[ "$HF_SPACE" == "true" ]] || [[ -n "$HF_SPACE" ]]
}

# Check if Docker is available
check_docker() {
    if command -v docker &> /dev/null; then
        print_success "Docker is available"
        return 0
    else
        print_warning "Docker is not available"
        return 1
    fi
}

# Check if required tools are available
check_requirements() {
    print_status "Checking requirements..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    local python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
    print_success "Python $python_version found"
    
    # Check pip
    if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
        print_error "pip is required but not installed"
        exit 1
    fi
    
    # Check if we're in HF Spaces or have internet for package installation
    if is_hf_spaces; then
        print_status "Detected HuggingFace Spaces environment"
    else
        print_status "Local development environment detected"
    fi
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if [[ -f "requirements.txt" ]]; then
        if command -v pip3 &> /dev/null; then
            pip3 install -r requirements.txt
        else
            pip install -r requirements.txt
        fi
        print_success "Dependencies installed successfully"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Build Docker image (for local testing)
build_docker() {
    if ! check_docker; then
        return 1
    fi
    
    print_status "Building Docker image..."
    
    if [[ -f "Dockerfile" ]]; then
        docker build -t code-interceptor-sandbox .
        print_success "Docker image built successfully"
    else
        print_error "Dockerfile not found"
        return 1
    fi
}

# Run tests
run_tests() {
    print_status "Running tests..."
    
    if [[ -f "test_sandbox.py" ]]; then
        if command -v pytest &> /dev/null; then
            python3 -m pytest test_sandbox.py -v
        else
            print_warning "pytest not available, running basic tests manually"
            python3 -c "
import sys
sys.path.append('.')
from app import executor
result = executor.execute_code('print(\"Test\")', 'python', 'test')
if result['success']:
    print('✅ Basic test passed')
else:
    print('❌ Basic test failed')
    sys.exit(1)
"
        fi
        print_success "Tests completed"
    else
        print_warning "No test file found, skipping tests"
    fi
}

# Start the application
start_application() {
    print_status "Starting Code Interceptor + Agentic Sandbox..."
    
    if is_hf_spaces; then
        # HF Spaces expects Gradio on port 7860
        print_status "Starting on HuggingFace Spaces..."
        python3 app.py
    else
        # Local development
        print_status "Starting locally..."
        
        # Check if we should use Docker
        if [[ "$1" == "--docker" ]]; then
            if check_docker; then
                print_status "Starting with Docker..."
                docker run -p 7860:7860 code-interceptor-sandbox
            else
                print_error "Docker not available"
                exit 1
            fi
        else
            # Direct Python execution
            python3 app.py
        fi
    fi
}

# Health check
health_check() {
    print_status "Performing health check..."
    
    # Wait for service to start
    sleep 5
    
    if curl -f http://localhost:7860/ &> /dev/null; then
        print_success "Health check passed"
    else
        print_error "Health check failed"
        return 1
    fi
}

# Deploy to HuggingFace Spaces
deploy_hf_spaces() {
    print_status "Deploying to HuggingFace Spaces..."
    
    # Check if we're in the right directory
    if [[ ! -f "README.md" ]] || [[ ! -f "app.py" ]]; then
        print_error "Not in the correct directory for HF Spaces deployment"
        exit 1
    fi
    
    # Verify all required files exist
    local required_files=("app.py" "requirements.txt" "Dockerfile" "README.md")
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            print_error "Required file missing: $file"
            exit 1
        fi
    done
    
    print_success "All required files present"
    print_status "To deploy to HF Spaces:"
    echo "  1. Create a new Space on https://huggingface.co/spaces"
    echo "  2. Choose 'Docker' as SDK"
    echo "  3. Upload these files to your repository"
    echo "  4. The space will automatically build and deploy"
}

# Print usage information
usage() {
    echo "Code Interceptor + Agentic Sandbox Deployment Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  install     Install dependencies and prepare environment"
    echo "  test        Run test suite"
    echo "  start       Start the application"
    echo "  docker      Build and run with Docker"
    echo "  deploy-hf   Prepare for HuggingFace Spaces deployment"
    echo "  health      Perform health check"
    echo "  help        Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  HF_SPACE    Set to 'true' when running on HuggingFace Spaces"
    echo "  MAX_EXECUTION_TIME    Maximum execution time in seconds"
    echo "  MAX_MEMORY_MB         Maximum memory usage in MB"
    echo ""
    echo "Examples:"
    echo "  $0 install && $0 test && $0 start"
    echo "  $0 docker"
    echo "  HF_SPACE=true $0 start"
}

# Main execution
main() {
    local command="${1:-help}"
    
    case "$command" in
        install)
            check_requirements
            install_dependencies
            print_success "Installation completed"
            ;;
        test)
            check_requirements
            install_dependencies
            run_tests
            ;;
        start)
            check_requirements
            install_dependencies
            start_application "$@"
            ;;
        docker)
            check_requirements
            install_dependencies
            build_docker
            start_application --docker
            ;;
        deploy-hf)
            deploy_hf_spaces
            ;;
        health)
            health_check
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            print_error "Unknown command: $command"
            usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"