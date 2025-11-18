// Test suite for Cloudflare Workers version
// Run with: npm test

interface Env {
  ENVIRONMENT: string;
  MAX_EXECUTION_TIME: string;
  MAX_MEMORY_MB: string;
  DB?: D1Database;
}

describe('Hybrid Code Interceptor - Cloudflare Workers', () => {
  const mockEnv: Env = {
    ENVIRONMENT: 'test',
    MAX_EXECUTION_TIME: '10',
    MAX_MEMORY_MB: '128'
  };

  describe('Security Analysis', () => {
    test('should detect eval() usage', () => {
      const code = 'eval("alert(1)");';
      // @ts-ignore - accessing private function for testing
      const result = analyzeSecurity(code);
      
      expect(result.allowed).toBe(false);
      expect(result.violations).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            pattern: 'eval()',
            severity: 'high'
          })
        ])
      );
    });

    test('should detect network requests', () => {
      const code = 'fetch("/api/data");';
      // @ts-ignore - accessing private function for testing
      const result = analyzeSecurity(code);
      
      expect(result.allowed).toBe(false);
      expect(result.violations).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            pattern: 'fetch()',
            severity: 'high'
          })
        ])
      );
    });

    test('should allow safe code', () => {
      const code = 'console.log("Hello World"); const x = 42;';
      // @ts-ignore - accessing private function for testing
      const result = analyzeSecurity(code);
      
      expect(result.allowed).toBe(true);
      expect(result.violations).toHaveLength(0);
    });

    test('should calculate complexity score', () => {
      const code = `
        function complexFunction() {
          for (let i = 0; i < 100; i++) {
            console.log(i);
          }
        }
        class MyClass {
          constructor() {
            this.property = "test";
          }
        }
      `;
      // @ts-ignore - accessing private function for testing
      const result = analyzeSecurity(code);
      
      expect(result.complexityScore).toBeGreaterThan(0);
      expect(result.allowed).toBe(true);
    });
  });

  describe('Code Execution', () => {
    test('should execute simple JavaScript', async () => {
      const code = 'console.log("test"); 2 + 2;';
      
      // @ts-ignore - accessing private function for testing
      const result = await executeJavaScript(code, 10);
      
      expect(result.success).toBe(true);
      expect(result.output).toContain('test');
      expect(result.exitCode).toBe(0);
    });

    test('should handle syntax errors', async () => {
      const code = 'console.log("unclosed string';
      
      // @ts-ignore - accessing private function for testing
      const result = await executeJavaScript(code, 10);
      
      expect(result.success).toBe(false);
      expect(result.error).toContain('SyntaxError');
    });

    test('should enforce timeout', async () => {
      const code = 'while(true) { console.log("infinite"); }';
      
      // @ts-ignore - accessing private function for testing
      const result = await executeJavaScript(code, 1);
      
      expect(result.success).toBe(false);
      expect(result.error).toContain('timeout');
    });
  });

  describe('API Endpoints', () => {
    test('should respond to health check', async () => {
      const response = await handleRequest(new Request('http://localhost/'), mockEnv);
      const data = await response.json();
      
      expect(response.status).toBe(200);
      expect(data.status).toBe('healthy');
      expect(data.service).toBe('Hybrid Code Interceptor Sandbox');
    });

    test('should handle POST /execute', async () => {
      const request = new Request('http://localhost/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code: 'console.log("test");',
          language: 'javascript'
        })
      });
      
      const response = await handleRequest(request, mockEnv);
      const data = await response.json();
      
      expect(response.status).toBe(200);
      expect(data.success).toBe(true);
      expect(data.output).toContain('test');
    });

    test('should validate language parameter', async () => {
      const request = new Request('http://localhost/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code: 'print("Hello")',
          language: 'python'
        })
      });
      
      const response = await handleRequest(request, mockEnv);
      const data = await response.json();
      
      expect(response.status).toBe(400);
      expect(data.error).toContain('not supported');
    });

    test('should return available languages', async () => {
      const response = await handleRequest(new Request('http://localhost/languages'), mockEnv);
      const data = await response.json();
      
      expect(response.status).toBe(200);
      expect(Array.isArray(data.languages)).toBe(true);
      expect(data.languages[0].name).toBe('javascript');
      expect(data.languages[0].available).toBe(true);
    });

    test('should return security policy', async () => {
      const response = await handleRequest(new Request('http://localhost/security/policy'), mockEnv);
      const data = await response.json();
      
      expect(response.status).toBe(200);
      expect(data.max_execution_time).toBe(10);
      expect(data.environment).toBe('Cloudflare Workers');
      expect(data.security_features).toBeDefined();
    });
  });

  describe('CORS', () => {
    test('should include CORS headers', async () => {
      const request = new Request('http://localhost/', {
        method: 'OPTIONS'
      });
      
      const response = await handleRequest(request, mockEnv);
      
      expect(response.headers.get('Access-Control-Allow-Origin')).toBe('*');
      expect(response.headers.get('Access-Control-Allow-Methods')).toContain('GET');
      expect(response.headers.get('Access-Control-Allow-Methods')).toContain('POST');
    });

    test('should include CORS headers on API responses', async () => {
      const request = new Request('http://localhost/languages');
      const response = await handleRequest(request, mockEnv);
      
      expect(response.headers.get('Access-Control-Allow-Origin')).toBe('*');
    });
  });

  describe('Error Handling', () => {
    test('should handle 404 for unknown routes', async () => {
      const response = await handleRequest(new Request('http://localhost/unknown'), mockEnv);
      const data = await response.json();
      
      expect(response.status).toBe(404);
      expect(data.error).toBe('Not Found');
    });

    test('should handle JSON parsing errors', async () => {
      const request = new Request('http://localhost/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: 'invalid json'
      });
      
      const response = await handleRequest(request, mockEnv);
      
      expect(response.status).toBe(500);
    });

    test('should handle missing required fields', async () => {
      const request = new Request('http://localhost/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      
      const response = await handleRequest(request, mockEnv);
      const data = await response.json();
      
      expect(response.status).toBe(400);
      expect(data.error).toContain('required');
    });
  });
});

// Mock request handler for testing
async function handleRequest(request: Request, env: Env): Promise<Response> {
  const url = new URL(request.url);
  const path = url.pathname;
  
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  };
  
  if (request.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }
  
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
      if (request.method === 'POST') {
        try {
          const { code } = await request.json();
          if (!code) {
            return new Response(JSON.stringify({
              success: false,
              error: 'Code is required'
            }), {
              status: 400,
              headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
          }
          
          // Mock execution result
          return new Response(JSON.stringify({
            success: true,
            output: 'Mock execution output',
            error: '',
            exit_code: 0,
            execution_time: 0.1,
            security_report: {
              allowed: true,
              violations: [],
              complexity_score: 1
            }
          }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
        } catch {
          return new Response(JSON.stringify({ error: 'Invalid JSON' }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
        }
      }
      break;
      
    case '/languages':
      return new Response(JSON.stringify({
        languages: [
          { name: 'javascript', available: true }
        ]
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
      
    case '/security/policy':
      return new Response(JSON.stringify({
        max_execution_time: parseInt(env.MAX_EXECUTION_TIME || '10'),
        environment: 'Cloudflare Workers'
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
      
    default:
      return new Response(JSON.stringify({
        error: 'Not Found',
        available_routes: ['/', '/execute', '/languages', '/security/policy']
      }), {
        status: 404,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
  }
  
  return new Response(null, { status: 405 });
}