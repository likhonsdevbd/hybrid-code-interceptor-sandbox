"""
Example Configuration for Code Interceptor + Agentic Sandbox
Demonstrates how to customize security settings and limits
"""

from security_config import SecurityConfig


class CustomSandboxConfig(SecurityConfig):
    """Example of custom configuration for specific use cases"""
    
    # Educational environment - more permissive
    @classmethod
    def get_educational_config(cls):
        """Configuration optimized for educational use"""
        return {
            "MAX_EXECUTION_TIME": 60,  # Longer time for learning
            "MAX_MEMORY_MB": 512,      # More memory for complex programs
            "MAX_OUTPUT_SIZE": 16384,  # Larger output for debugging
            "ALLOWED_EXTENSIONS": [".py", ".js", ".sh", ".cpp", ".rs"],
            "EDUCATIONAL_PATTERNS_ONLY": True
        }
    
    # Production environment - strict security
    @classmethod
    def get_production_config(cls):
        """Configuration for production deployment"""
        return {
            "MAX_EXECUTION_TIME": 10,   # Strict time limits
            "MAX_MEMORY_MB": 128,       # Minimal memory
            "MAX_OUTPUT_SIZE": 4096,    # Limited output
            "STRICT_SECURITY": True,
            "AUDIT_ALL_EXECUTIONS": True,
            "ALLOW_NETWORK": False,
            "ENABLE_COMPREHENSIVE_LOGGING": True
        }
    
    # Research environment - balanced security
    @classmethod
    def get_research_config(cls):
        """Configuration for research and experimentation"""
        return {
            "MAX_EXECUTION_TIME": 120,  # Longer for research code
            "MAX_MEMORY_MB": 1024,      # More memory for algorithms
            "MAX_OUTPUT_SIZE": 32768,   # Larger output for analysis
            "ALLOW_IMPORT_OPERATIONS": True,
            "ALLOW_FILE_OPERATIONS": True,
            "RESEARCH_MODE": True,
            "DETAILED_SECURITY_REPORTING": True
        }


# Example usage patterns
def demonstrate_configurations():
    """Demonstrate different configuration approaches"""
    
    print("=== Code Interceptor Sandbox Configurations ===\n")
    
    # Default configuration
    print("1. DEFAULT CONFIGURATION:")
    print(f"   Max Execution Time: {SecurityConfig.MAX_EXECUTION_TIME}s")
    print(f"   Max Memory: {SecurityConfig.MAX_MEMORY_MB}MB")
    print(f"   Max Output: {SecurityConfig.MAX_OUTPUT_SIZE}bytes")
    print(f"   Security Patterns: {len(SecurityConfig.DANGEROUS_PATTERNS)}")
    print()
    
    # Educational configuration
    edu_config = CustomSandboxConfig.get_educational_config()
    print("2. EDUCATIONAL CONFIGURATION:")
    for key, value in edu_config.items():
        print(f"   {key}: {value}")
    print()
    
    # Production configuration
    prod_config = CustomSandboxConfig.get_production_config()
    print("3. PRODUCTION CONFIGURATION:")
    for key, value in prod_config.items():
        print(f"   {key}: {value}")
    print()
    
    # Research configuration
    research_config = CustomSandboxConfig.get_research_config()
    print("4. RESEARCH CONFIGURATION:")
    for key, value in research_config.items():
        print(f"   {key}: {value}")
    print()


# Language-specific security examples
def demonstrate_language_security():
    """Show language-specific security configurations"""
    
    print("=== Language-Specific Security ===\n")
    
    languages = ["python", "javascript", "bash", "cpp", "rust"]
    
    for lang in languages:
        rules = SecurityConfig.get_language_config(lang)
        complexity = SecurityConfig.get_complexity_limits(lang)
        
        print(f"{lang.upper()} Language:")
        print(f"  Security Rules: {len(rules) if rules else 'None'}")
        print(f"  Complexity Limits: {complexity}")
        print()


if __name__ == "__main__":
    demonstrate_configurations()
    demonstrate_language_security()
    
    print("=== Configuration Tips ===\n")
    print("1. Choose configuration based on use case:")
    print("   - Educational: Allow more freedom for learning")
    print("   - Production: Maximum security, strict limits")
    print("   - Research: Balance between security and functionality")
    print()
    print("2. Customize by modifying security_config.py:")
    print("   - Adjust resource limits")
    print("   - Add/remove security patterns")
    print("   - Configure language-specific rules")
    print()
    print("3. Environment variables override config:")
    print("   export MAX_EXECUTION_TIME=60")
    print("   export MAX_MEMORY_MB=512")
    print()
    print("4. Test configurations:")
    print("   python example_config.py")