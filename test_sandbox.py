"""
Test cases for Code Interceptor + Agentic Sandbox
Comprehensive testing of security features and execution capabilities
"""

import pytest
import json
from app import executor, LANGUAGE_CONFIGS, DANGEROUS_PATTERNS


class TestSecurityInterceptor:
    """Test security interception functionality"""
    
    def test_python_safe_code(self):
        """Test that safe Python code passes security checks"""
        safe_code = '''
print("Hello World!")
numbers = [1, 2, 3, 4, 5]
result = sum(numbers)
print(f"Sum: {result}")
'''
        result = executor.interceptor.analyze_code(safe_code, "python")
        assert result["allowed"] is True
        assert len(result["violations"]) == 0
    
    def test_python_dangerous_code_detection(self):
        """Test detection of dangerous Python operations"""
        dangerous_code = '''
import os
os.system("rm -rf /")
eval("malicious code")
exec("dangerous()")
'''
        result = executor.interceptor.analyze_code(dangerous_code, "python")
        assert result["allowed"] is False
        assert len(result["violations"]) > 0
        
        # Check for specific violations
        violations_text = " ".join([v["context"] for v in result["violations"]])
        assert "os.system" in violations_text or "eval" in violations_text or "exec" in violations_text
    
    def test_javascript_dangerous_code(self):
        """Test detection of dangerous JavaScript operations"""
        dangerous_js = '''
eval("malicious code");
setTimeout("alert('hack')", 1000);
Function("return 42")();
'''
        result = executor.interceptor.analyze_code(dangerous_js, "javascript")
        assert result["allowed"] is False
        assert len(result["violations"]) > 0
    
    def test_bash_dangerous_commands(self):
        """Test detection of dangerous bash commands"""
        dangerous_bash = '''
#!/bin/bash
nc -l 8080
curl http://malicious.com
sudo rm -rf /
'''
        result = executor.interceptor.analyze_code(dangerous_bash, "bash")
        assert result["allowed"] is False
        assert len(result["violations"]) > 0
    
    def test_complexity_calculation(self):
        """Test code complexity scoring"""
        simple_code = "print('hello')"
        complex_code = '''
class ComplexClass:
    def complex_method(self):
        if True:
            for i in range(100):
                while True:
                    try:
                        print(i)
                    except Exception as e:
                        pass
'''
        simple_result = executor.interceptor.analyze_code(simple_code, "python")
        complex_result = executor.interceptor.analyze_code(complex_code, "python")
        
        assert simple_result["complexity_score"] < complex_result["complexity_score"]
        assert simple_result["complexity_score"] > 0


class TestSandboxExecutor:
    """Test sandbox execution functionality"""
    
    def test_python_execution(self):
        """Test Python code execution"""
        code = '''
result = 2 + 2
print(f"Result: {result}")
exit_code = 0 if result == 4 else 1
'''
        result = executor.execute_code(code, "python", "test-job-1")
        
        assert result["success"] is True
        assert "Result: 4" in result["output"]
        assert result["exit_code"] == 0
    
    def test_javascript_execution(self):
        """Test JavaScript code execution"""
        code = '''
const numbers = [1, 2, 3, 4, 5];
const sum = numbers.reduce((a, b) => a + b, 0);
console.log(`Sum: ${sum}`);
'''
        result = executor.execute_code(code, "javascript", "test-job-2")
        
        assert result["success"] is True
        assert "Sum: 15" in result["output"]
    
    def test_bash_execution(self):
        """Test Bash code execution"""
        code = '''
#!/bin/bash
echo "Hello from Bash!"
sum=$((1 + 2 + 3))
echo "Sum: $sum"
'''
        result = executor.execute_code(code, "bash", "test-job-3")
        
        assert result["success"] is True
        assert "Hello from Bash!" in result["output"]
        assert "Sum: 6" in result["output"]
    
    def test_cpp_compilation_and_execution(self):
        """Test C++ compilation and execution"""
        code = '''
#include <iostream>
#include <vector>
#include <numeric>

int main() {
    std::vector<int> numbers = {1, 2, 3, 4, 5};
    int sum = std::accumulate(numbers.begin(), numbers.end(), 0);
    std::cout << "Sum: " << sum << std::endl;
    return 0;
}
'''
        result = executor.execute_code(code, "cpp", "test-job-4", timeout=60)
        
        assert result["success"] is True
        assert "Sum: 15" in result["output"]
    
    def test_rust_compilation_and_execution(self):
        """Test Rust compilation and execution"""
        code = '''
fn main() {
    let numbers = vec![1, 2, 3, 4, 5];
    let sum: i32 = numbers.iter().sum();
    println!("Sum: {}", sum);
}
'''
        result = executor.execute_code(code, "rust", "test-job-5", timeout=60)
        
        assert result["success"] is True
        assert "Sum: 15" in result["output"]
    
    def test_security_violation_blocking(self):
        """Test that security violations are properly blocked"""
        malicious_code = '''
import os
os.system("echo 'This should be blocked'")
'''
        result = executor.execute_code(malicious_code, "python", "test-job-6")
        
        assert result["success"] is False
        assert "Security violation" in result["error"] or len(result.get("violations", [])) > 0
    
    def test_timeout_enforcement(self):
        """Test execution timeout enforcement"""
        infinite_loop = '''
import time
while True:
    time.sleep(1)
'''
        result = executor.execute_code(infinite_loop, "python", "test-job-7", timeout=2)
        
        # Should timeout and fail
        assert result["success"] is False
        assert "timeout" in result["error"].lower()
    
    def test_output_size_limiting(self):
        """Test output size limiting"""
        large_output = '''
for i in range(1000):
    print(f"Line {i}: " + "x" * 100)
'''
        result = executor.execute_code(large_output, "python", "test-job-8", timeout=10)
        
        # Should succeed but truncate output
        assert result["success"] is True
        # Check if output is truncated (should contain truncation marker)
        assert "..." in result["output"] or len(result["output"]) <= 9000  # Slightly larger than MAX_OUTPUT_SIZE
    
    def test_invalid_language(self):
        """Test handling of invalid programming languages"""
        code = "print('hello')"
        result = executor.execute_code(code, "invalid_language", "test-job-9")
        
        # Should fall back to default or handle gracefully
        assert isinstance(result, dict)
        assert "success" in result


class TestLanguageConfigurations:
    """Test language configuration settings"""
    
    def test_language_support(self):
        """Test that all configured languages are supported"""
        for lang in LANGUAGE_CONFIGS.keys():
            assert "command" in LANGUAGE_CONFIGS[lang]
            assert "file_extension" in LANGUAGE_CONFIGS[lang]
            assert "timeout_multiplier" in LANGUAGE_CONFIGS[lang]
    
    def test_language_commands(self):
        """Test language command configurations"""
        expected_commands = {
            "python": "python3",
            "javascript": "node",
            "bash": "bash",
            "cpp": "g++ -O2 -std=c++17 -o {out} {file} && {out}",
            "rust": "rustc -O -o {out} {file} && {out}"
        }
        
        for lang, expected_cmd in expected_commands.items():
            assert LANGUAGE_CONFIGS[lang]["command"] == expected_cmd


class TestSecurityPatterns:
    """Test security pattern definitions"""
    
    def test_pattern_completeness(self):
        """Test that security patterns cover important categories"""
        pattern_text = " ".join(DANGEROUS_PATTERNS)
        
        # Should cover various threat categories
        categories = {
            "filesystem": ["/dev/", "/proc/", "mkfs"],
            "network": ["nc", "curl", "wget"],
            "system": ["sudo", "reboot", "shutdown"],
            "code_injection": ["eval", "exec", "os.system"]
        }
        
        for category, patterns in categories.items():
            for pattern in patterns:
                # At least one pattern from each category should be present
                found = any(pattern.lower() in p.lower() for p in DANGEROUS_PATTERNS)
                assert found, f"Missing {category} pattern: {pattern}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])