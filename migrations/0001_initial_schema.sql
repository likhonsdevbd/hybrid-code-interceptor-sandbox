-- Hybrid Code Interceptor Sandbox Database Schema
-- Run this in Cloudflare D1 to set up the database

-- Execution logs table
CREATE TABLE IF NOT EXISTS executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code_hash TEXT NOT NULL,
    language TEXT NOT NULL DEFAULT 'javascript',
    success INTEGER NOT NULL DEFAULT 0,
    output_length INTEGER NOT NULL DEFAULT 0,
    execution_time REAL NOT NULL DEFAULT 0.0,
    violations_count INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_agent TEXT,
    ip_address TEXT,
    execution_context JSON
);

-- Security violations tracking
CREATE TABLE IF NOT EXISTS security_violations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id INTEGER,
    violation_type TEXT NOT NULL,
    line_number INTEGER,
    pattern_matched TEXT,
    severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high')),
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (execution_id) REFERENCES executions(id) ON DELETE CASCADE
);

-- Rate limiting table
CREATE TABLE IF NOT EXISTS rate_limits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    requests_count INTEGER NOT NULL DEFAULT 1,
    window_start DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ip_address, endpoint, window_start)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_executions_hash ON executions(code_hash);
CREATE INDEX IF NOT EXISTS idx_executions_created ON executions(created_at);
CREATE INDEX IF NOT EXISTS idx_violations_execution ON security_violations(execution_id);
CREATE INDEX IF NOT EXISTS idx_rate_limits_ip ON rate_limits(ip_address);
CREATE INDEX IF NOT EXISTS idx_rate_limits_window ON rate_limits(window_start);

-- Insert some sample data for testing
INSERT INTO executions (code_hash, language, success, output_length, execution_time, violations_count)
VALUES 
    ('abc123def456', 'javascript', 1, 45, 0.125, 0),
    ('def456ghi789', 'javascript', 0, 0, 0.050, 1),
    ('ghi789jkl012', 'javascript', 1, 128, 0.200, 2);

-- View to get execution statistics
CREATE VIEW IF NOT EXISTS execution_stats AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_executions,
    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_executions,
    AVG(execution_time) as avg_execution_time,
    SUM(violations_count) as total_violations,
    SUM(output_length) as total_output_size
FROM executions 
GROUP BY DATE(created_at)
ORDER BY date DESC;