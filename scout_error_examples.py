#!/usr/bin/env python3
"""
Scout CLI Error Handling Examples
Comprehensive examples of how to use Scout CLI error tracking.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scout_tracker_init import (
    log_error, log_warning, log_critical, log_syntax_error, 
    track_issues, tracked_operation, IssueType, IssueSeverity
)


# Example 1: Function with automatic error tracking
@track_issues()
def risky_operation():
    """Example function that might fail."""
    # This will automatically log any exceptions
    raise ValueError("Something went wrong!")


# Example 2: Manual error logging
def manual_error_example():
    """Example of manual error logging."""
    
    try:
        # Some operation that might fail
        result = 10 / 0
        return result
        
    except ZeroDivisionError as e:
        log_error(
            "Division by zero error",
            context={'operation': 'division', 'values': [10, 0]},
            function_name='manual_error_example'
        )
        return None
    except Exception as e:
        log_critical(
            f"Unexpected error: {e}",
            context={'operation': 'division'},
            exception=e
        )
        return None


# Example 3: Using context manager for operation tracking
def context_manager_example():
    """Example using context manager for tracking operations."""
    
    with tracked_operation("Data Processing"):
        # Simulate some work
        import time
        time.sleep(1)
        
        # Log a warning during the operation
        log_warning("Processing taking longer than expected")
        
        # Complete successfully
        print("Operation completed")


# Example 4: Security issue logging
def security_logging_example():
    """Example of logging security-related issues."""
    
    user_input = "<script>alert('xss')</script>"
    
    if '<script>' in user_input:
        log_security_issue(
            "Potential XSS attack detected",
            context={
                'input': user_input,
                'source': 'user_form',
                'ip': '192.168.1.100'
            },
            severity=IssueSeverity.HIGH
        )


# Example 5: File operation error handling
@track_issues(issue_type=IssueType.FILE_IO, severity=IssueSeverity.MEDIUM)
def file_operation_example():
    """Example of file operation with error tracking."""
    
    try:
        with open('/nonexistent/file.txt', 'r') as f:
            return f.read()
            
    except FileNotFoundError:
        log_error(
            "Configuration file not found",
            file_path='/nonexistent/file.txt',
            context={'operation': 'read_config'}
        )
        return None


# Example 6: Network operation tracking
def network_operation_example():
    """Example of network operation error handling."""
    
    with tracked_operation("API Request"):
        try:
            # Simulate network request
            import requests
            response = requests.get('https://httpbin.org/status/500')
            response.raise_for_status()
            
        except requests.exceptions.RequestException as e:
            log_error(
                "API request failed",
                context={
                    'url': 'https://httpbin.org/status/500',
                    'status_code': getattr(e.response, 'status_code', None)
                },
                exception=e
            )


# Example 7: Custom issue type logging
def custom_issue_example():
    """Example of logging custom issue types."""
    
    from scout_issue_tracker import scout_tracker
    
    # Log a performance issue
    scout_tracker.log_issue(
        "Database query taking too long",
        issue_type=IssueType.PERFORMANCE,
        severity=IssueSeverity.MEDIUM,
        context={
            'query_time': 5.2,
            'query': 'SELECT * FROM large_table',
            'threshold': 2.0
        }
    )
    
    # Log a configuration issue
    scout_tracker.log_issue(
        "Invalid configuration value",
        issue_type=IssueType.CONFIGURATION,
        severity=IssueSeverity.LOW,
        context={
            'config_key': 'max_connections',
            'config_value': -1,
            'expected_range': '1-1000'
        }
    )


def run_all_examples():
    """Run all error handling examples."""
    
    print("🧪 Running Scout CLI Error Handling Examples\n")
    
    examples = [
        ("Manual Error Logging", manual_error_example),
        ("Context Manager", context_manager_example),
        ("Security Logging", security_logging_example),
        ("File Operations", file_operation_example),
        ("Network Operations", network_operation_example),
        ("Custom Issues", custom_issue_example),
    ]
    
    for name, func in examples:
        print(f"Running: {name}")
        try:
            func()
            print(f"  ✅ {name} completed\n")
        except Exception as e:
            print(f"  ❌ {name} failed: {e}\n")
    
    # Try risky operation (will fail)
    print("Running: Risky Operation (expected to fail)")
    try:
        risky_operation()
    except Exception as e:
        print(f"  ❌ Risky Operation failed as expected: {e}\n")
    
    print("🎯 All examples completed!")
    
    # Show tracking summary
    try:
        from scout_realtime_monitor import realtime_monitor
        dashboard_data = realtime_monitor.get_live_dashboard_data()
        print(f"\n📊 Issues logged during examples: {dashboard_data['total_issues']}")
        
    except Exception:
        print("\n📊 Error tracking summary not available")


if __name__ == "__main__":
    run_all_examples()
