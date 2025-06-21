# Scout CLI Error Tracking Guide

## Overview

Scout CLI includes a comprehensive error tracking and monitoring system that automatically captures, logs, and analyzes all errors, warnings, and issues throughout the application.

## Components

### 1. Core Tracking System
- `scout_issue_tracker.py` - Main tracking engine
- `scout_tracker_init.py` - Easy integration layer
- `scout_realtime_monitor.py` - Real-time monitoring
- `scout_dashboard.py` - Live dashboard interface

### 2. Integration Files
- `scout_startup_integration.py` - Auto-initialization
- `scout_error_integration.py` - Setup and integration
- `scout_error_examples.py` - Usage examples

## Quick Start

### Automatic Integration
The error tracking system is automatically integrated into Scout CLI. When you run any Scout command, error tracking is initialized automatically.

### Manual Integration
To manually integrate error tracking into your code:

```python
from scout_tracker_init import log_error, log_warning, track_issues, tracked_operation

# Log errors manually
log_error("Something went wrong", context={"user": "admin"})
log_warning("This might be a problem")

# Use decorators for automatic tracking
@track_issues()
def my_function():
    # Any exceptions will be automatically logged
    pass

# Use context managers for operation tracking
with tracked_operation("Database Backup"):
    # All issues during this operation will be tracked
    pass
```

## Features

### 1. Automatic Error Detection
- Syntax errors
- Runtime exceptions  
- Import failures
- Network timeouts
- File I/O errors
- Security vulnerabilities

### 2. Real-time Monitoring
- Live dashboard showing current issues
- Performance metrics
- Error rate tracking
- Alert system for critical issues

### 3. Comprehensive Logging
- JSON structured logs
- HTML reports
- Real-time log files
- Issue categorization

### 4. Advanced Analytics
- Issue pattern analysis
- Performance trend tracking
- File-level issue mapping
- Severity distribution

## Usage Examples

### Basic Error Logging
```python
from scout_tracker_init import log_error, log_warning, log_critical

# Log different severity levels
log_error("Database connection failed", context={"db": "users"})
log_warning("API rate limit approaching")
log_critical("Security breach detected")
```

### Function Decoration
```python
@track_issues()
def process_data(data):
    # Any exceptions automatically logged with context
    return analyze(data)

@track_issues(issue_type=IssueType.SECURITY, severity=IssueSeverity.HIGH)
def validate_input(user_input):
    # Specific issue type and severity
    return sanitize(user_input)
```

### Context Management
```python
with tracked_operation("User Authentication"):
    # Track entire authentication process
    user = authenticate(username, password)
    log_audit_event("User login", user_id=user.id)
```

### Custom Issue Types
```python
from scout_issue_tracker import scout_tracker, IssueType, IssueSeverity

scout_tracker.log_issue(
    "Performance degradation detected",
    issue_type=IssueType.PERFORMANCE,
    severity=IssueSeverity.MEDIUM,
    context={
        "response_time": 2.5,
        "threshold": 1.0,
        "endpoint": "/api/search"
    }
)
```

## Dashboard and Monitoring

### Live Dashboard
```bash
# Start interactive dashboard
python scout_dashboard.py dashboard

# Generate analysis report
python scout_dashboard.py analyze

# Export current state
python scout_dashboard.py export

# Start monitoring mode
python scout_dashboard.py monitor
```

### Real-time Monitoring
```python
from scout_realtime_monitor import live_monitoring

with live_monitoring() as monitor:
    # Your code here - all issues will be monitored
    run_scout_operations()
    
    # Get live statistics
    stats = monitor.get_live_dashboard_data()
    print(f"Issues detected: {stats['total_issues']}")
```

## Configuration

### Issue Filtering
```python
from scout_realtime_monitor import realtime_monitor

# Add filters to ignore certain issues
realtime_monitor.issue_filters.add("deprecation_warning")
realtime_monitor.issue_filters.add("debug_info")
```

### Alert Callbacks
```python
def critical_alert_handler(message, issue):
    # Send email, Slack notification, etc.
    send_alert(f"CRITICAL: {message}")

realtime_monitor.add_alert_callback(critical_alert_handler)
```

### Custom Severity Levels
```python
from scout_issue_tracker import IssueSeverity

# Use different severity levels
log_error("Minor issue", severity=IssueSeverity.LOW)
log_error("Major problem", severity=IssueSeverity.HIGH)  
log_error("System failure", severity=IssueSeverity.FATAL)
```

## Log Files and Reports

### Log Locations
- `logs/scout_issues_YYYYMMDD_HHMMSS.log` - Structured issue logs
- `logs/scout_realtime_YYYYMMDD_HHMMSS.log` - Real-time monitoring logs
- `logs/scout_session_YYYYMMDD_HHMMSS.json` - Session summaries

### Report Generation
```python
from scout_issue_tracker import scout_tracker

# Export comprehensive reports
json_report = scout_tracker.export_report("json")
html_report = scout_tracker.export_report("html")
```

### Automated Reports
The system automatically generates:
- Daily summary reports
- Critical issue alerts
- Performance trend analysis
- Security incident reports

## Best Practices

### 1. Use Appropriate Severity Levels
- `FATAL`: System cannot continue
- `CRITICAL`: Immediate attention required
- `HIGH`: Significant impact on functionality
- `MEDIUM`: Moderate impact
- `LOW`: Minor issues or informational

### 2. Provide Context
Always include relevant context in error logs:
```python
log_error(
    "Database query failed",
    context={
        "query": sql_query,
        "parameters": params,
        "execution_time": duration,
        "user_id": current_user.id
    }
)
```

### 3. Use Specific Issue Types
Choose the most appropriate issue type:
- `ERROR`: General errors
- `SECURITY`: Security-related issues
- `PERFORMANCE`: Performance problems
- `NETWORK`: Network connectivity issues
- `FILE_IO`: File operation problems
- `CONFIGURATION`: Configuration errors

### 4. Monitor Critical Paths
Add tracking to critical application paths:
```python
@track_issues(severity=IssueSeverity.HIGH)
def critical_business_logic():
    # Important business operations
    pass
```

## Troubleshooting

### Common Issues

#### Error tracking not working
1. Check if `scout_tracker_init.py` is importable
2. Verify Python path includes project root
3. Check for import conflicts

#### Dashboard not displaying data
1. Ensure real-time monitoring is started
2. Check log file permissions
3. Verify curses library availability

#### High memory usage
1. Adjust `max_live_issues` in `RealtimeIssueMonitor`
2. Enable periodic cleanup
3. Filter out low-priority issues

### Performance Tuning

#### Reduce Overhead
```python
# Disable tracking for high-frequency operations
@track_issues(enabled=False)
def high_frequency_function():
    pass

# Use sampling for performance-critical code
if random.random() < 0.1:  # 10% sampling
    log_performance_metric("operation_time", duration)
```

#### Optimize Log Storage
- Use log rotation for large deployments
- Compress old log files
- Archive historical data

## Integration with Scout CLI

The error tracking system is fully integrated with Scout CLI:

- All CLI commands automatically use error tracking
- Security scans log vulnerabilities as security issues
- Performance monitoring tracks scan execution times
- User authentication failures are logged as security events
- Configuration errors are categorized and tracked

### CLI Integration Points
- `scout/cli.py` - Main CLI error handling
- `scout/commands/*.py` - Command-specific error tracking
- `scout/checks/*.py` - Security check error logging
- `scout/ai_engine.py` - AI/ML operation tracking

## API Reference

See individual module documentation:
- `scout_issue_tracker.py` - Core tracking API
- `scout_realtime_monitor.py` - Real-time monitoring API
- `scout_dashboard.py` - Dashboard and reporting API

## Support

For issues with the error tracking system:
1. Check log files in `logs/` directory
2. Run `python scout_error_examples.py` to verify functionality
3. Use `python scout_dashboard.py analyze` for diagnostics
4. Review this guide for common solutions
