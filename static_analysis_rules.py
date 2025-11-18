"""
Static Analysis Rules for Code Interceptor + Agentic Sandbox
Comprehensive security rules for multiple programming languages
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SecurityRule:
    """Security rule definition"""
    pattern: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    recommendation: str
    category: str
    language_specific: Dict[str, str]  # language -> specific pattern


class StaticAnalysisRules:
    """Collection of static analysis security rules"""
    
    def __init__(self):
        self.rules = self._initialize_rules()
    
    def _initialize_rules(self) -> List[SecurityRule]:
        """Initialize comprehensive security rules"""
        return [
            # ===== CRITICAL RULES =====
            SecurityRule(
                pattern=r"(eval|exec)\s*\(",
                severity="CRITICAL",
                description="Dynamic code execution detected",
                recommendation="Avoid using eval() or exec(). Use safer alternatives like ast.literal_eval() for data parsing.",
                category="code_injection",
                language_specific={
                    "python": r"(eval|exec|compile)\s*\(",
                    "javascript": r"(eval|Function)\s*\(",
                    "php": r"(eval|assert)\s*\(",
                }
            ),
            
            SecurityRule(
                pattern=r"os\.system\s*\(",
                severity="CRITICAL", 
                description="System command execution detected",
                recommendation="Avoid os.system(). Use subprocess.run() with proper input validation instead.",
                category="command_injection",
                language_specific={
                    "python": r"os\.system|subprocess\.(call|run|Popen)",
                    "javascript": r"child_process\.(exec|spawn|execSync)",
                    "c": r"system\s*\(|popen\s*\(",
                }
            ),
            
            SecurityRule(
                pattern=r"import\s+os|from\s+os",
                severity="CRITICAL",
                description="OS module import detected - potential for system access",
                recommendation="Avoid importing os module unless absolutely necessary. Use safer alternatives.",
                category="system_access",
                language_specific={
                    "python": r"import\s+os|from\s+os",
                    "javascript": r"require\(.*fs\)|import\s+.*fs",
                    "go": r"import\s+\".*os.*\"",
                }
            ),
            
            # ===== HIGH SEVERITY RULES =====
            SecurityRule(
                pattern=r"/dev/[a-zA-Z]+",
                severity="HIGH",
                description="Direct device file access",
                recommendation="Avoid accessing device files. Use proper APIs for device interaction.",
                category="filesystem",
                language_specific={
                    "python": r"/dev/(null|zero|random|urandom|stdin|stdout|stderr)",
                    "bash": r"/dev/(null|zero|random|urandom|stdin|stdout|stderr)",
                }
            ),
            
            SecurityRule(
                pattern=r"/proc",
                severity="HIGH",
                description="Process filesystem access",
                recommendation="Avoid accessing /proc filesystem. Use standard APIs instead.",
                category="system_info",
                language_specific={
                    "python": r"/proc/",
                    "bash": r"/proc/",
                }
            ),
            
            SecurityRule(
                pattern=r"sudo|su\s",
                severity="HIGH",
                description="Privilege escalation attempt",
                recommendation="Avoid privilege escalation. Run with minimal required permissions.",
                category="privilege_escalation",
                language_specific={
                    "bash": r"sudo|su\s",
                    "python": r"os\.setuid|os\.setgid",
                }
            ),
            
            SecurityRule(
                pattern=r"curl\s+|wget\s+",
                severity="HIGH",
                description="Network download detected",
                recommendation="Avoid arbitrary network downloads. Use verified package managers instead.",
                category="network",
                language_specific={
                    "bash": r"curl\s+|wget\s+",
                    "python": r"requests\.|urllib\.|httplib\.",
                    "javascript": r"fetch\(|XMLHttpRequest|axios\.",
                }
            ),
            
            SecurityRule(
                pattern=r"chmod\s+[467][0-7][0-7]",
                severity="HIGH",
                description="Insecure file permissions",
                recommendation="Use minimal required permissions. Avoid 777 permissions.",
                category="filesystem",
                language_specific={
                    "bash": r"chmod\s+[467][0-7][0-7]",
                    "python": r"os\.chmod.*0[467][0-7][0-7]",
                }
            ),
            
            # ===== MEDIUM SEVERITY RULES =====
            SecurityRule(
                pattern=r"open\s*\(\s*['\"]\/",
                severity="MEDIUM",
                description="File access in root directory",
                recommendation="Avoid accessing files in system directories. Use application-specific paths.",
                category="filesystem",
                language_specific={
                    "python": r"open\s*\(\s*['\"]\/(etc|var|tmp|usr|bin|sbin)",
                    "javascript": r"fs\.readFileSync\s*\(\s*['\"]\/",
                    "bash": r"(cat|echo|grep|ls)\s+['\"]\/",
                }
            ),
            
            SecurityRule(
                pattern=r"import\s+subprocess|from\s+subprocess",
                severity="MEDIUM",
                description="Subprocess module import",
                recommendation="Subprocess can be dangerous. Ensure proper input validation and sanitization.",
                category="process_management",
                language_specific={
                    "python": r"import\s+subprocess|from\s+subprocess",
                }
            ),
            
            SecurityRule(
                pattern=r"__import__",
                severity="MEDIUM",
                description="Dynamic import detected",
                recommendation="Avoid __import__. Use standard import statements with static module names.",
                category="code_injection",
                language_specific={
                    "python": r"__import__",
                }
            ),
            
            SecurityRule(
                pattern=r"pickle\.load|pickle\.loads",
                severity="MEDIUM",
                description="Pickle deserialization detected",
                recommendation="Pickle can execute arbitrary code. Use safer serialization like JSON.",
                category="deserialization",
                language_specific={
                    "python": r"pickle\.(load|loads|dump|dumps)",
                    "javascript": r"JSON\.parse|JSON\.stringify",
                }
            ),
            
            SecurityRule(
                pattern=r"hashlib\.(md5|sha1)",
                severity="MEDIUM",
                description="Weak cryptographic hash detected",
                recommendation="Use stronger hash functions like SHA-256 or SHA-3 instead of MD5/SHA1.",
                category="cryptography",
                language_specific={
                    "python": r"hashlib\.(md5|sha1)",
                    "javascript": r"crypto\.createHash\(['\"]?(md5|sha1)['\"]?\)",
                }
            ),
            
            # ===== LOW SEVERITY RULES =====
            SecurityRule(
                pattern=r"print\s*\(|console\.log",
                severity="LOW",
                description="Debug output detected",
                recommendation="Consider removing debug output in production code.",
                category="debugging",
                language_specific={
                    "python": r"print\s*\(",
                    "javascript": r"console\.(log|debug|info)",
                }
            ),
            
            SecurityRule(
                pattern=r"import\s+random|from\s+random",
                severity="LOW",
                description="Random module usage",
                recommendation="Use secrets module for cryptographic randomness instead of random.",
                category="cryptography",
                language_specific={
                    "python": r"import\s+random|from\s+random",
                }
            ),
            
            # ===== LANGUAGE-SPECIFIC RULES =====
            
            # Python specific
            SecurityRule(
                pattern=r"globals\(\)|locals\(\)",
                severity="MEDIUM",
                description="Reflection detected",
                recommendation="Avoid reflection when possible. Use explicit variable names.",
                category="reflection",
                language_specific={"python": r"globals\(\)|locals\(\)"}
            ),
            
            SecurityRule(
                pattern=r"setattr|getattr|hasattr",
                severity="MEDIUM",
                description="Dynamic attribute access",
                recommendation="Avoid dynamic attribute access. Use explicit attribute names.",
                category="reflection",
                language_specific={"python": r"setattr|getattr|hasattr"}
            ),
            
            # JavaScript specific
            SecurityRule(
                pattern=r"document\.write|innerHTML|outerHTML",
                severity="HIGH",
                description="DOM manipulation detected",
                recommendation="Avoid direct DOM manipulation. Use safe methods like textContent.",
                category="dom_manipulation",
                language_specific={"javascript": r"document\.write|innerHTML|outerHTML"}
            ),
            
            SecurityRule(
                pattern=r"setTimeout\s*\(|setInterval\s*\(",
                severity="MEDIUM",
                description="Timer functions detected",
                recommendation="Be cautious with timers. Ensure proper cleanup to prevent memory leaks.",
                category="timing",
                language_specific={"javascript": r"setTimeout\s*\(|setInterval\s*\("}
            ),
            
            # Bash specific
            SecurityRule(
                pattern=r"rm\s+-rf|rmdir",
                severity="CRITICAL",
                description="Dangerous file deletion command",
                recommendation="Avoid recursive deletion. Use specific file paths and confirm operations.",
                category="filesystem",
                language_specific={"bash": r"rm\s+-rf|rmdir"}
            ),
            
            SecurityRule(
                pattern=r"mv\s+.*\/|cp\s+.*\/",
                severity="MEDIUM",
                description="File move/copy to system directories",
                recommendation="Be cautious with file operations in system directories.",
                category="filesystem",
                language_specific={"bash": r"mv\s+.*\/|cp\s+.*\/"}
            ),
            
            # C++ specific
            SecurityRule(
                pattern=r"system\s*\(|popen\s*\(",
                severity="CRITICAL",
                description="System command execution in C++",
                recommendation="Avoid system() calls. Use safer alternatives for command execution.",
                category="command_injection",
                language_specific={"cpp": r"system\s*\(|popen\s*\("}
            ),
            
            SecurityRule(
                pattern=r"#include\s+<[^>]*\.(h|hpp)>",
                severity="LOW",
                description="Header file inclusion",
                recommendation="Review included headers for security implications.",
                category="inclusion",
                language_specific={"cpp": r"#include\s+<[^>]*\.(h|hpp)>"}
            ),
            
            # Rust specific
            SecurityRule(
                pattern=r"unsafe\s*{",
                severity="HIGH",
                description="Unsafe code block detected",
                recommendation="Minimize use of unsafe code. Ensure proper bounds checking.",
                category="memory_safety",
                language_specific={"rust": r"unsafe\s*{"}
            ),
            
            SecurityRule(
                pattern=r"std::process::Command",
                severity="MEDIUM",
                description="Process spawning detected",
                recommendation="Be cautious with process spawning. Validate inputs thoroughly.",
                category="process_management",
                language_specific={"rust": r"std::process::Command"}
            ),
        ]
    
    def analyze_code(self, code: str, language: str) -> Dict:
        """Analyze code using static rules"""
        violations = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for rule in self.rules:
                # Get language-specific pattern if available
                pattern = rule.pattern
                if language in rule.language_specific:
                    pattern = rule.language_specific[language]
                
                # Check for pattern match
                if re.search(pattern, line, re.IGNORECASE | re.MULTILINE):
                    violations.append({
                        "rule_id": len(violations) + 1,
                        "pattern": rule.pattern,
                        "severity": rule.severity,
                        "description": rule.description,
                        "recommendation": rule.recommendation,
                        "category": rule.category,
                        "line_number": line_num,
                        "line_content": line.strip(),
                        "language": language
                    })
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(violations)
        
        return {
            "violations": violations,
            "total_violations": len(violations),
            "risk_score": risk_score,
            "severity_breakdown": self._get_severity_breakdown(violations),
            "category_breakdown": self._get_category_breakdown(violations),
            "analysis_timestamp": None,  # Will be set by caller
            "language_analyzed": language,
            "recommendations": self._get_general_recommendations(violations)
        }
    
    def _calculate_risk_score(self, violations: List[Dict]) -> int:
        """Calculate overall risk score based on violations"""
        severity_weights = {
            "CRITICAL": 10,
            "HIGH": 5,
            "MEDIUM": 2,
            "LOW": 1
        }
        
        total_score = sum(
            severity_weights.get(v["severity"], 1) for v in violations
        )
        
        # Normalize to 0-100 scale
        max_possible_score = 100  # Assume worst case
        risk_score = min(100, (total_score / max_possible_score) * 100)
        
        return int(risk_score)
    
    def _get_severity_breakdown(self, violations: List[Dict]) -> Dict:
        """Get breakdown by severity"""
        breakdown = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for violation in violations:
            breakdown[violation["severity"]] += 1
        return breakdown
    
    def _get_category_breakdown(self, violations: List[Dict]) -> Dict:
        """Get breakdown by category"""
        breakdown = {}
        for violation in violations:
            category = violation["category"]
            breakdown[category] = breakdown.get(category, 0) + 1
        return breakdown
    
    def _get_general_recommendations(self, violations: List[Dict]) -> List[str]:
        """Get general recommendations based on violations"""
        recommendations = []
        
        categories = set(v["category"] for v in violations)
        
        if "code_injection" in categories:
            recommendations.append("Review all dynamic code execution patterns")
        
        if "command_injection" in categories:
            recommendations.append("Validate and sanitize all command inputs")
        
        if "filesystem" in categories:
            recommendations.append("Restrict file system access to application directories")
        
        if "network" in categories:
            recommendations.append("Implement network access controls and validation")
        
        if "privilege_escalation" in categories:
            recommendations.append("Review permission requirements and reduce privileges")
        
        if not recommendations:
            recommendations.append("Code appears to follow security best practices")
        
        return recommendations


# Create global instance
static_rules = StaticAnalysisRules()

# Export for easy import
__all__ = ['StaticAnalysisRules', 'SecurityRule', 'static_rules']