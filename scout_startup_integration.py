#!/usr/bin/env python3
"""
Scout CLI Startup Integration
Automatically initializes error tracking when Scout CLI starts.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def initialize_scout_tracking():
    """Initialize Scout CLI error tracking system."""
    
    try:
        # Import and start real-time monitoring
        from scout_realtime_monitor import realtime_monitor
        from scout_issue_tracker import scout_tracker
        
        # Start monitoring
        realtime_monitor.start_monitoring()
        
        # Log startup
        scout_tracker.log_info("Scout CLI error tracking initialized")
        
        print("🔍 Scout CLI error tracking: ACTIVE")
        return True
        
    except ImportError as e:
        print(f"⚠️  Scout CLI error tracking: UNAVAILABLE ({e})")
        return False
    except Exception as e:
        print(f"❌ Scout CLI error tracking: FAILED ({e})")
        return False

def shutdown_scout_tracking():
    """Shutdown Scout CLI error tracking system."""
    
    try:
        from scout_realtime_monitor import realtime_monitor
        from scout_issue_tracker import scout_tracker
        
        # Generate final report
        scout_tracker.export_report('json')
        
        # Stop monitoring
        realtime_monitor.stop_monitoring()
        
        # Log shutdown
        scout_tracker.log_info("Scout CLI error tracking shutdown")
        
        print("🔍 Scout CLI error tracking: STOPPED")
        
    except Exception as e:
        print(f"Error during tracking shutdown: {e}")

# Auto-initialize when imported
if __name__ == "__main__":
    initialize_scout_tracking()
else:
    # Auto-initialize when imported by other modules
    initialize_scout_tracking()
