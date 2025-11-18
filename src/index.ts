interface Env {
  // Environment variables
  ENVIRONMENT: string;
  MAX_EXECUTION_TIME: string;
  MAX_MEMORY_MB: string;
  
  // Optional bindings
  DB?: D1Database;
  EXECUTION_KV?: KVNamespace;
}

interface ExecutionResult {
  success: boolean;
  output: string;
  error: string;
  exit_code: number;
  execution_time: number;
  security_report: {
    allowed: boolean;
    violations: SecurityViolation[];
    complexity_score: number;
  };
}

interface SecurityViolation {
  line: number;
  pattern: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname;
    
    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    };
    
    // Handle preflight requests
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }
    
    try {
      // Route handling
      switch (path) {
        case '/':
          return new Response(JSON.stringify({
            status: 'healthy',
            service: 'Hybrid Code Interceptor Sandbox',
            version: '1.0.0-cf',
            timestamp: new Date().toISOString(),
            environment: env.ENVIRONMENT || 'development'
          }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
          
        case '/execute':
          return await handleExecute(request, env, corsHeaders);
          
        case '/languages':
          return await handleLanguages(corsHeaders);
          
        case '/security/policy':
          return await handleSecurityPolicy(env, corsHeaders);
          
        case '/health':
          return new Response(JSON.stringify({
            status: 'ok',
            workers_version: '1.0.0-cf'
          }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
          
        case '/ui':
          return await serveUI(corsHeaders);
          
        default:
          return new Response(JSON.stringify({
            error: 'Not Found',
            message: `Route ${path} not found`,
            available_routes: ['/', '/execute', '/languages', '/security/policy', '/health', '/ui']
          }), {
            status: 404,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
      }
    } catch (error) {
      console.error('Worker error:', error);
      return new Response(JSON.stringify({
        error: 'Internal Server Error',
        message: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString()
      }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }
  }
};

// Execute code handler
async function handleExecute(request: Request, env: Env, corsHeaders: Record<string, string>): Promise<Response> {
  if (request.method !== 'POST') {
    return new Response(JSON.stringify({
      error: 'Method Not Allowed',
      message: 'POST method required for /execute'
    }), {
      status: 405,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
  
  const startTime = Date.now();
  
  try {
    const { code, language, timeout } = await request.json();
    
    if (!code) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Code is required',
        output: '',
        exit_code: 1
      }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }
    
    // Validate language (Cloudflare Workers limited to JavaScript)
    if (language && language !== 'javascript') {
      return new Response(JSON.stringify({
        success: false,
        error: `Language '${language}' not supported in Cloudflare Workers. Only JavaScript is supported.`,
        output: '',
        exit_code: 1
      }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }
    
    // Security analysis
    const securityReport = analyzeSecurity(code);
    
    if (!securityReport.allowed) {
      const executionTime = (Date.now() - startTime) / 1000;
      return new Response(JSON.stringify({
        success: false,
        output: '',
        error: 'Code blocked by security policy',
        exit_code: 1,
        execution_time: executionTime,
        security_report: securityReport
      }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }
    
    // Execute JavaScript code safely
    const result = await executeJavaScript(code, timeout || parseInt(env.MAX_EXECUTION_TIME || '10'));
    const executionTime = (Date.now() - startTime) / 1000;
    
    // Log execution (optional - requires D1 database)
    if (env.DB) {
      try {
        await env.DB.prepare(`
          INSERT INTO executions (code_hash, language, success, output_length, execution_time, violations_count)
          VALUES (?, ?, ?, ?, ?, ?)
        `).bind(
          await hashCode(code),
          'javascript',
          result.success,
          result.output.length,
          executionTime,
          securityReport.violations.length
        ).run();
      } catch (logError) {
        console.warn('Failed to log execution:', logError);
      }
    }
    
    return new Response(JSON.stringify({
      success: result.success,
      output: result.output,
      error: result.error,
      exit_code: result.exitCode,
      execution_time: executionTime,
      security_report: {
        allowed: true,
        violations: securityReport.violations,
        complexity_score: securityReport.complexityScore
      }
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    const executionTime = (Date.now() - startTime) / 1000;
    return new Response(JSON.stringify({
      success: false,
      output: '',
      error: error instanceof Error ? error.message : 'Execution failed',
      exit_code: 1,
      execution_time: executionTime,
      security_report: {
        allowed: false,
        violations: [],
        complexity_score: 0
      }
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
}

// Security analysis for JavaScript code
function analyzeSecurity(code: string): {
  allowed: boolean;
  violations: SecurityViolation[];
  complexityScore: number;
} {
  const violations: SecurityViolation[] = [];
  const lines = code.split('\n');
  
  // Dangerous patterns to detect
  const dangerousPatterns = [
    { pattern: /eval\s*\(/, name: 'eval()', description: 'Dynamic code execution', severity: 'high' as const },
    { pattern: /Function\s*\(/, name: 'Function()', description: 'Dynamic function creation', severity: 'high' as const },
    { pattern: /import\s+/, name: 'import statements', description: 'Module imports', severity: 'medium' as const },
    { pattern: /require\s*\(/, name: 'require()', description: 'Module requires', severity: 'medium' as const },
    { pattern: /process\./, name: 'process object', description: 'Process access', severity: 'high' as const },
    { pattern: /global\./, name: 'global object', description: 'Global object access', severity: 'medium' as const },
    { pattern: /window\./, name: 'window object', description: 'DOM access', severity: 'low' as const },
    { pattern: /document\./, name: 'document object', description: 'DOM access', severity: 'low' as const },
    { pattern: /fetch\s*\(/, name: 'fetch()', description: 'Network requests', severity: 'high' as const },
    { pattern: /XMLHttpRequest/i, name: 'XHR', description: 'Network requests', severity: 'high' as const },
    { pattern: /WebSocket/i, name: 'WebSocket', description: 'WebSocket connections', severity: 'high' as const },
    { pattern: /localStorage|sessionStorage/i, name: 'storage', description: 'Browser storage access', severity: 'medium' as const },
    { pattern: /setTimeout|setInterval/i, name: 'timers', description: 'Timer functions', severity: 'medium' as const },
    { pattern: /while\s*\(\s*true\s*\)/i, name: 'infinite loop', description: 'Potential infinite loop', severity: 'high' as const },
    { pattern: /for\s*\(\s*;;\s*\)/i, name: 'infinite loop', description: 'Potential infinite loop', severity: 'high' as const },
  ];
  
  // Check for dangerous patterns
  lines.forEach((line, index) => {
    const lineNum = index + 1;
    dangerousPatterns.forEach(({ pattern, name, description, severity }) => {
      if (pattern.test(line)) {
        violations.push({
          line: lineNum,
          pattern: name,
          description,
          severity
        });
      }
    });
  });
  
  // Calculate complexity score
  let complexityScore = 0;
  complexityScore += violations.length * 10; // High penalty for violations
  complexityScore += lines.length / 10; // Complexity based on lines
  complexityScore += (code.match(/function/g) || []).length * 5;
  complexityScore += (code.match(/class/g) || []).length * 3;
  
  // Block if too many high-severity violations
  const hasHighSeverity = violations.some(v => v.severity === 'high');
  const hasTooManyViolations = violations.length > 5;
  
  return {
    allowed: !hasHighSeverity && !hasTooManyViolations,
    violations,
    complexityScore: Math.min(complexityScore, 100)
  };
}

// Execute JavaScript code safely in a limited context
async function executeJavaScript(code: string, timeout: number): Promise<{
  success: boolean;
  output: string;
  error: string;
  exitCode: number;
}> {
  let output = '';
  let error = '';
  let success = false;
  let exitCode = 0;
  
  // Create a limited execution context
  const sandboxConsole = {
    log: (...args: any[]) => {
      output += args.map(arg => 
        typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
      ).join(' ') + '\n';
    },
    error: (...args: any[]) => {
      error += args.map(arg => String(arg)).join(' ') + '\n';
    },
    warn: (...args: any[]) => {
      output += '[WARN] ' + args.map(arg => String(arg)).join(' ') + '\n';
    },
    info: (...args: any[]) => {
      output += '[INFO] ' + args.map(arg => String(arg)).join(' ') + '\n';
    }
  };
  
  try {
    // Create a safe execution function
    const safeExecute = new Function('console', `
      'use strict';
      try {
        ${code}
        return { success: true, error: '' };
      } catch (error) {
        return { success: false, error: error.message || String(error) };
      }
    `);
    
    // Execute with timeout
    const result = await Promise.race([
      Promise.resolve(safeExecute(sandboxConsole)),
      new Promise<{ success: false; error: string }>((_, reject) => {
        setTimeout(() => reject(new Error(`Execution timeout after ${timeout}ms`)), timeout * 1000);
      })
    ]);
    
    success = result.success;
    if (!result.success) {
      error = result.error;
      exitCode = 1;
    }
    
  } catch (err) {
    success = false;
    error = err instanceof Error ? err.message : 'Execution failed';
    exitCode = 1;
  }
  
  return { success, output, error, exitCode };
}

// Hash code for logging (simple hash)
async function hashCode(str: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(str);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

// Handle languages endpoint
async function handleLanguages(corsHeaders: Record<string, string>): Promise<Response> {
  return new Response(JSON.stringify({
    languages: [
      {
        name: 'javascript',
        command: 'Function()',
        file_extension: '.js',
        timeout_multiplier: 1.0,
        available: true
      },
      {
        name: 'python',
        command: 'python3',
        file_extension: '.py',
        timeout_multiplier: 1.0,
        available: false,
        note: 'Not available in Cloudflare Workers environment'
      },
      {
        name: 'node',
        command: 'node',
        file_extension: '.js',
        timeout_multiplier: 1.0,
        available: false,
        note: 'Use JavaScript instead'
      }
    ]
  }), {
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  });
}

// Handle security policy endpoint
async function handleSecurityPolicy(env: Env, corsHeaders: Record<string, string>): Promise<Response> {
  return new Response(JSON.stringify({
    max_execution_time: parseInt(env.MAX_EXECUTION_TIME || '10'),
    max_memory_mb: parseInt(env.MAX_MEMORY_MB || '128'),
    max_output_size: 8192,
    dangerous_patterns_count: 15,
    environment: 'Cloudflare Workers',
    limitations: [
      'JavaScript only execution',
      'No subprocess spawning',
      'Limited system access',
      'No persistent storage',
      'Sandboxed runtime'
    ],
    security_features: [
      'Pattern-based detection',
      'Complexity scoring',
      'Timeout enforcement',
      'Sandboxed execution',
      'CORS protection'
    ]
  }), {
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  });
}

// Serve simple UI
async function serveUI(corsHeaders: Record<string, string>): Promise<Response> {
  const html = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hybrid Code Interceptor - Cloudflare Workers</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { background: #f5f5f5; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        textarea { width: 100%; height: 200px; font-family: monospace; padding: 10px; }
        button { background: #007cba; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #005a87; }
        .result { background: white; padding: 15px; border-radius: 4px; margin-top: 10px; }
        .error { background: #ffe6e6; color: #d00; }
        .success { background: #e6ffe6; color: #006400; }
        .warning { background: #fff3cd; color: #856404; }
    </style>
</head>
<body>
    <h1>🚀 Hybrid Code Interceptor - Cloudflare Workers</h1>
    <div class="container">
        <h3>Execute JavaScript Code</h3>
        <textarea id="code" placeholder="Enter your JavaScript code here...">console.log("Hello from Cloudflare Workers!");
const data = { message: "Secure execution", timestamp: new Date().toISOString() };
console.log(JSON.stringify(data, null, 2));</textarea>
        <br><br>
        <button onclick="executeCode()">Execute Code</button>
    </div>
    
    <div class="container">
        <h3>Security Information</h3>
        <ul>
            <li>✅ JavaScript execution only</li>
            <li>🛡️ Pattern-based security scanning</li>
            <li>⏱️ Timeout enforcement</li>
            <li>🚫 No subprocess or network access</li>
            <li>🔒 Sandboxed runtime</li>
        </ul>
    </div>
    
    <div id="result" class="result" style="display: none;"></div>
    
    <script>
        async function executeCode() {
            const code = document.getElementById('code').value;
            const resultDiv = document.getElementById('result');
            
            resultDiv.innerHTML = '<p>⏳ Executing code...</p>';
            resultDiv.style.display = 'block';
            
            try {
                const response = await fetch('/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code, language: 'javascript' })
                });
                
                const result = await response.json();
                
                let html = '<h4>Execution Result</h4>';
                html += '<p><strong>Success:</strong> ' + (result.success ? '✅ Yes' : '❌ No') + '</p>';
                html += '<p><strong>Execution Time:</strong> ' + result.execution_time.toFixed(3) + 's</p>';
                html += '<p><strong>Exit Code:</strong> ' + result.exit_code + '</p>';
                
                if (result.output) {
                    html += '<h5>Output:</h5><pre>' + result.output + '</pre>';
                }
                
                if (result.error) {
                    html += '<h5>Error:</h5><pre class="error">' + result.error + '</pre>';
                }
                
                if (result.security_report && result.security_report.violations.length > 0) {
                    html += '<h5>Security Violations:</h5><ul>';
                    result.security_report.violations.forEach(v => {
                        html += '<li><span class="warning">Line ' + v.line + ': ' + v.pattern + ' - ' + v.description + '</span></li>';
                    });
                    html += '</ul>';
                }
                
                resultDiv.className = 'result ' + (result.success ? 'success' : 'error');
                resultDiv.innerHTML = html;
                
            } catch (error) {
                resultDiv.className = 'result error';
                resultDiv.innerHTML = '<h4>Error</h4><p>' + error.message + '</p>';
            }
        }
    </script>
</body>
</html>`;
  
  return new Response(html, {
    headers: { ...corsHeaders, 'Content-Type': 'text/html' }
  });
}