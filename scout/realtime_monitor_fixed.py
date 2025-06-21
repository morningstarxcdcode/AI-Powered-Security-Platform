"""
Real-time monitoring dashboard with WebSocket support.
Provides live security metrics, threat feeds, and interactive visualizations.
"""

import asyncio
import logging
import time
import uuid
import weakref
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from scout.logging import log_info, log_error, log_warning

try:
    import redis
    import uvicorn
    from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
    from fastapi.responses import HTMLResponse
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel, Field
except ImportError:
    redis = uvicorn = FastAPI = WebSocket = HTMLResponse = StaticFiles = BaseModel = Field = None
    WebSocketDisconnect = HTTPException = Depends = None

# Constants
DEFAULT_REDIS_URL = "redis://localhost:6379"

logger = logging.getLogger(__name__)


class SecurityEventType(Enum):
    """Types of security events for real-time monitoring."""
    VULNERABILITY_DETECTED = "vulnerability_detected"
    SCAN_STARTED = "scan_started"
    SCAN_COMPLETED = "scan_completed"
    THREAT_DETECTED = "threat_detected"
    ANOMALY_DETECTED = "anomaly_detected"
    COMPLIANCE_VIOLATION = "compliance_violation"
    SYSTEM_ALERT = "system_alert"
    USER_ACTION = "user_action"


class AlertSeverity(Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class SecurityEvent:
    """Real-time security event."""
    id: str
    event_type: SecurityEventType
    severity: AlertSeverity
    timestamp: float
    source: str
    title: str
    description: str
    metadata: Dict[str, Any]
    resolved: bool = False
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class SecurityMetrics:
    """Current security metrics for dashboard."""
    total_scans: int = 0
    active_scans: int = 0
    vulnerabilities_found: int = 0
    critical_issues: int = 0
    high_issues: int = 0
    medium_issues: int = 0
    low_issues: int = 0
    last_scan_time: Optional[float] = None
    uptime: float = 0.0
    scan_success_rate: float = 0.0


@dataclass
class ThreatIntelligence:
    """Real-time threat intelligence feed."""
    threat_id: str
    threat_type: str
    severity: AlertSeverity
    source: str
    indicators: List[str]
    description: str
    mitigation: str
    timestamp: float
    active: bool = True


class ConnectionManager:
    """WebSocket connection manager for real-time updates."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_metadata: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()

    async def connect(self, websocket: WebSocket, client_id: str = None):
        """Accept new WebSocket connection."""
        try:
            await websocket.accept()
            self.active_connections.append(websocket)
            
            metadata = {
                'client_id': client_id or str(uuid.uuid4()),
                'connected_at': time.time(),
                'subscriptions': set()
            }
            self.connection_metadata[websocket] = metadata
            
            log_info(f"WebSocket client connected: {metadata['client_id']}")
            
            # Send initial connection confirmation
            await self.send_personal_message({
                'type': 'connection_established',
                'client_id': metadata['client_id'],
                'timestamp': time.time()
            }, websocket)
            
        except Exception as e:
            log_error(f"Error accepting WebSocket connection: {e}")

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection."""
        try:
            if websocket in self.active_connections:
                metadata = self.connection_metadata.get(websocket, {})
                client_id = metadata.get('client_id', 'unknown')
                
                self.active_connections.remove(websocket)
                log_info(f"WebSocket client disconnected: {client_id}")
                
        except Exception as e:
            log_error(f"Error during WebSocket disconnect: {e}")

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send message to specific WebSocket connection."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            log_error(f"Error sending personal message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: Dict[str, Any], event_type: str = None):
        """Broadcast message to all connected clients."""
        if not self.active_connections:
            return

        message_data = {
            'timestamp': time.time(),
            'type': event_type or 'broadcast',
            **message
        }

        disconnected_clients = []
        
        for connection in self.active_connections:
            try:
                # Check if client is subscribed to this event type
                metadata = self.connection_metadata.get(connection, {})
                subscriptions = metadata.get('subscriptions', set())
                
                if not subscriptions or event_type in subscriptions or event_type is None:
                    await connection.send_json(message_data)
                    
            except Exception as e:
                log_error(f"Error broadcasting to client: {e}")
                disconnected_clients.append(connection)

        # Clean up disconnected clients
        for client in disconnected_clients:
            self.disconnect(client)

    async def subscribe_client(self, websocket: WebSocket, event_types: List[str]):
        """Subscribe client to specific event types."""
        try:
            metadata = self.connection_metadata.get(websocket, {})
            if 'subscriptions' not in metadata:
                metadata['subscriptions'] = set()
            
            metadata['subscriptions'].update(event_types)
            log_info(f"Client subscribed to events: {event_types}")
            
        except Exception as e:
            log_error(f"Error subscribing client: {e}")


class SecurityEventStore:
    """Store and retrieve security events with Redis backend."""

    def __init__(self, redis_url: str = DEFAULT_REDIS_URL):
        self.redis_url = redis_url
        self.redis_client = None
        self.local_events: List[SecurityEvent] = []
        self.max_local_events = 1000

    async def initialize(self):
        """Initialize Redis connection."""
        try:
            if redis:
                self.redis_client = redis.Redis.from_url(self.redis_url, decode_responses=True)
                await self.redis_client.ping()
                log_info("Connected to Redis for event storage")
            else:
                log_warning("Redis not available, using local storage only")
        except Exception as e:
            log_error(f"Failed to connect to Redis: {e}")
            log_info("Falling back to local storage")

    async def store_event(self, event: SecurityEvent):
        """Store security event."""
        try:
            # Store in local cache
            self.local_events.append(event)
            if len(self.local_events) > self.max_local_events:
                self.local_events.pop(0)

            # Store in Redis if available
            if self.redis_client:
                event_data = asdict(event)
                await self.redis_client.lpush('security_events', str(event_data))
                await self.redis_client.ltrim('security_events', 0, 9999)  # Keep last 10k events

            log_info(f"Stored security event: {event.id}")

        except Exception as e:
            log_error(f"Error storing event {event.id}: {e}")

    async def get_recent_events(self, limit: int = 100) -> List[SecurityEvent]:
        """Get recent security events."""
        try:
            if self.redis_client:
                # Get from Redis
                events_data = await self.redis_client.lrange('security_events', 0, limit - 1)
                events = []
                for event_str in events_data:
                    try:
                        event_dict = eval(event_str)  # In production, use json.loads
                        event = SecurityEvent(**event_dict)
                        events.append(event)
                    except Exception as e:
                        log_error(f"Error parsing event from Redis: {e}")
                return events
            else:
                # Get from local storage
                return self.local_events[-limit:] if self.local_events else []

        except Exception as e:
            log_error(f"Error retrieving events: {e}")
            return []

    async def get_events_by_type(self, event_type: SecurityEventType, 
                                limit: int = 100) -> List[SecurityEvent]:
        """Get events filtered by type."""
        try:
            all_events = await self.get_recent_events(limit * 2)  # Get more to filter
            filtered_events = [e for e in all_events if e.event_type == event_type]
            return filtered_events[:limit]

        except Exception as e:
            log_error(f"Error filtering events by type: {e}")
            return []


class RealTimeSecurityMonitor:
    """Main real-time security monitoring class."""

    def __init__(self, redis_url: str = DEFAULT_REDIS_URL):
        self.event_store = SecurityEventStore(redis_url)
        self.connection_manager = ConnectionManager()
        self.metrics = SecurityMetrics()
        self.app = FastAPI(title="Scout Security Monitor", version="1.0.0")
        self.threat_feeds: List[ThreatIntelligence] = []
        self.monitoring_tasks: Set[asyncio.Task] = set()
        
        self._setup_routes()

    def _setup_routes(self):
        """Setup FastAPI routes."""
        
        @self.app.websocket("/ws/{client_id}")
        async def websocket_endpoint(websocket: WebSocket, client_id: str):
            await self.connection_manager.connect(websocket, client_id)
            try:
                while True:
                    # Handle incoming messages
                    data = await websocket.receive_json()
                    await self._handle_websocket_message(websocket, data)
                    
            except WebSocketDisconnect:
                self.connection_manager.disconnect(websocket)

        @self.app.get("/api/metrics")
        async def get_metrics():
            """Get current security metrics."""
            return asdict(self.metrics)

        @self.app.get("/api/events")
        async def get_events(limit: int = 100):
            """Get recent security events."""
            events = await self.event_store.get_recent_events(limit)
            return [asdict(event) for event in events]

        @self.app.get("/api/events/{event_type}")
        async def get_events_by_type(event_type: str, limit: int = 100):
            """Get events by type."""
            try:
                event_enum = SecurityEventType(event_type)
                events = await self.event_store.get_events_by_type(event_enum, limit)
                return [asdict(event) for event in events]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid event type")

        @self.app.get("/api/threats")
        async def get_threat_intelligence():
            """Get current threat intelligence."""
            return [asdict(threat) for threat in self.threat_feeds if threat.active]

        @self.app.get("/dashboard")
        async def get_dashboard():
            """Serve monitoring dashboard."""
            return HTMLResponse(self._get_dashboard_html())

    async def _handle_websocket_message(self, websocket: WebSocket, data: Dict[str, Any]):
        """Handle incoming WebSocket messages."""
        try:
            message_type = data.get('type')
            
            if message_type == 'subscribe':
                event_types = data.get('event_types', [])
                await self.connection_manager.subscribe_client(websocket, event_types)
                
            elif message_type == 'get_metrics':
                await self.connection_manager.send_personal_message(
                    {'type': 'metrics', 'data': asdict(self.metrics)}, 
                    websocket
                )
                
        except Exception as e:
            log_error(f"Error handling WebSocket message: {e}")

    async def initialize(self):
        """Initialize the monitoring system."""
        await self.event_store.initialize()
        log_info("Real-time security monitor initialized")

    async def emit_event(self, event: SecurityEvent):
        """Emit new security event."""
        try:
            # Store event
            await self.event_store.store_event(event)
            
            # Update metrics
            self._update_metrics(event)
            
            # Broadcast to connected clients
            await self.connection_manager.broadcast(
                {
                    'event': asdict(event),
                    'metrics': asdict(self.metrics)
                },
                event_type=event.event_type.value
            )
            
            log_info(f"Emitted security event: {event.id}")

        except Exception as e:
            log_error(f"Error emitting event {event.id}: {e}")

    def _update_metrics(self, event: SecurityEvent):
        """Update security metrics based on new event."""
        if event.event_type == SecurityEventType.SCAN_STARTED:
            self.metrics.active_scans += 1
            self.metrics.total_scans += 1
            
        elif event.event_type == SecurityEventType.SCAN_COMPLETED:
            self.metrics.active_scans = max(0, self.metrics.active_scans - 1)
            self.metrics.last_scan_time = event.timestamp
            
        elif event.event_type == SecurityEventType.VULNERABILITY_DETECTED:
            self.metrics.vulnerabilities_found += 1
            
            if event.severity == AlertSeverity.CRITICAL:
                self.metrics.critical_issues += 1
            elif event.severity == AlertSeverity.HIGH:
                self.metrics.high_issues += 1
            elif event.severity == AlertSeverity.MEDIUM:
                self.metrics.medium_issues += 1
            elif event.severity == AlertSeverity.LOW:
                self.metrics.low_issues += 1

    async def add_threat_intelligence(self, threat: ThreatIntelligence):
        """Add threat intelligence to feed."""
        self.threat_feeds.append(threat)
        
        # Broadcast threat update
        await self.connection_manager.broadcast(
            {'threat': asdict(threat)},
            event_type='threat_intelligence'
        )

    def _get_dashboard_html(self) -> str:
        """Generate HTML dashboard."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Scout Security Monitor</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
                .metric-card { background: #f5f5f5; padding: 15px; border-radius: 5px; }
                .events { margin-top: 30px; }
                .event { background: #fff; border: 1px solid #ddd; padding: 10px; margin: 5px 0; }
                .critical { border-left: 5px solid #dc3545; }
                .high { border-left: 5px solid #fd7e14; }
                .medium { border-left: 5px solid #ffc107; }
                .low { border-left: 5px solid #28a745; }
            </style>
        </head>
        <body>
            <h1>Scout Security Monitor</h1>
            <div id="metrics" class="metrics"></div>
            <div class="events">
                <h2>Recent Events</h2>
                <div id="events-list"></div>
            </div>
            <script>
                const ws = new WebSocket(`ws://localhost:8000/ws/dashboard-${Date.now()}`);
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    if (data.type === 'connection_established') {
                        // Subscribe to all events
                        ws.send(JSON.stringify({
                            type: 'subscribe',
                            event_types: ['vulnerability_detected', 'scan_completed', 'threat_detected']
                        }));
                        // Request initial metrics
                        ws.send(JSON.stringify({type: 'get_metrics'}));
                    } else if (data.metrics) {
                        updateMetrics(data.metrics);
                    }
                    if (data.event) {
                        addEvent(data.event);
                    }
                };
                
                function updateMetrics(metrics) {
                    document.getElementById('metrics').innerHTML = `
                        <div class="metric-card">
                            <h3>Total Scans</h3>
                            <div>${metrics.total_scans}</div>
                        </div>
                        <div class="metric-card">
                            <h3>Active Scans</h3>
                            <div>${metrics.active_scans}</div>
                        </div>
                        <div class="metric-card">
                            <h3>Vulnerabilities Found</h3>
                            <div>${metrics.vulnerabilities_found}</div>
                        </div>
                        <div class="metric-card">
                            <h3>Critical Issues</h3>
                            <div>${metrics.critical_issues}</div>
                        </div>
                    `;
                }
                
                function addEvent(event) {
                    const eventsList = document.getElementById('events-list');
                    const eventDiv = document.createElement('div');
                    eventDiv.className = `event ${event.severity}`;
                    eventDiv.innerHTML = `
                        <strong>${event.title}</strong><br>
                        <small>${new Date(event.timestamp * 1000).toLocaleString()}</small><br>
                        ${event.description}
                    `;
                    eventsList.insertBefore(eventDiv, eventsList.firstChild);
                    
                    // Keep only last 50 events
                    while (eventsList.children.length > 50) {
                        eventsList.removeChild(eventsList.lastChild);
                    }
                }
            </script>
        </body>
        </html>
        """

    async def start_server(self, host: str = "0.0.0.0", port: int = 8000):
        """Start the monitoring server."""
        await self.initialize()
        
        config = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        
        log_info(f"Starting real-time monitor server on {host}:{port}")
        await server.serve()


# Global monitor instance
monitor = RealTimeSecurityMonitor()


async def start_monitoring_server():
    """Start the real-time security monitoring server."""
    await monitor.start_server()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--port":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    else:
        port = 8000
    
    asyncio.run(monitor.start_server(port=port))
