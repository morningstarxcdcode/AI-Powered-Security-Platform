"""
Real-time monitoring dashboard with WebSocket support.
Provides live security metrics, threat feeds, and interactive visualizations.
"""

import asyncio
import logging
import time
import uuid
import weakref
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, TYPE_CHECKING

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
    ATTACK_DETECTED = "attack_detected"
    REMEDIATION_APPLIED = "remediation_applied"


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
    timestamp: datetime
    source: str
    title: str
    description: str
    metadata: Dict[str, Any]
    affected_assets: List[str]
    remediation_status: str = "pending"
    correlation_id: Optional[str] = None


class SecurityMetrics(BaseModel):
    """Current security metrics for dashboard."""
    total_vulnerabilities: int = 0
    critical_vulnerabilities: int = 0
    high_vulnerabilities: int = 0
    medium_vulnerabilities: int = 0
    low_vulnerabilities: int = 0
    active_scans: int = 0
    threats_detected_24h: int = 0
    compliance_score: float = 0.0
    risk_score: float = 0.0
    uptime_percentage: float = 100.0
    last_scan_time: Optional[datetime] = None
    total_assets: int = 0
    protected_assets: int = 0


class ThreatFeed(BaseModel):
    """
    Real-time threat intelligence feed.
    """
    feed_id: str
    source: str
    threat_type: str
    indicators: List[str]
    severity: AlertSeverity
    confidence: float
    timestamp: datetime
    description: str
    mitigation: List[str]


class ConnectionManager:
    """
    Manages WebSocket connections for real-time updates.
    """
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        self.subscriptions: Dict[str, Set[str]] = {}  # connection_id -> event_types

    async def connect(self, websocket: WebSocket, client_id: str, user_info: Dict[str, Any] = None):
        """
        Accept new WebSocket connection.
        """
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.connection_metadata[client_id] = {
            "connected_at": datetime.now(),
            "user_info": user_info or {},
            "last_activity": datetime.now()
        }
        self.subscriptions[client_id] = set()
        logger.info(f"Client {client_id} connected to real-time dashboard")

    def disconnect(self, client_id: str):
        """Remove WebSocket connection."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            del self.connection_metadata[client_id]
            del self.subscriptions[client_id]
            logger.info(f"Client {client_id} disconnected from dashboard")

    async def send_personal_message(self, message: Dict[str, Any], client_id: str):
        """Send message to specific client."""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message))
                self.connection_metadata[client_id]["last_activity"] = datetime.now()
            except Exception as e:
                logger.error(f"Failed to send message to {client_id}: {e}")
                self.disconnect(client_id)

    async def broadcast(self, message: Dict[str, Any], event_type: str = None):
        """Broadcast message to all connected clients or filtered by subscription."""
        disconnected_clients = []

        for client_id, websocket in self.active_connections.items():
            # Check if client is subscribed to this event type
            if event_type and event_type not in self.subscriptions[client_id]:
                continue

            try:
                await websocket.send_text(json.dumps(message))
                self.connection_metadata[client_id]["last_activity"] = datetime.now()
            except Exception as e:
                logger.error(f"Failed to broadcast to {client_id}: {e}")
                disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)

    def subscribe_to_events(self, client_id: str, event_types: List[str]):
        """Subscribe client to specific event types."""
        if client_id in self.subscriptions:
            self.subscriptions[client_id].update(event_types)

    def get_connection_stats(self) -> Dict[str, Any]:
        """
Get statistics about active connections."""
        now = datetime.now()
        active_count = len(self.active_connections)

        # Calculate activity statistics
        recent_activity = sum(
            1 for metadata in self.connection_metadata.values()
            if (now-metadata["last_activity"]).seconds < 300  # Active in last 5 minutes
        )

        return {
            "total_connections": active_count,
            "recently_active": recent_activity,
            "average_connection_time": sum(
                (now-metadata["connected_at"]).seconds
                for metadata in self.connection_metadata.values()
            ) / active_count if active_count > 0 else 0
        }

class SecurityEventStore:
    """Store and manage security events for real-time access."""

    def __init__(self, redis_url: str = DEFAULT_REDIS_URL):
        try:
            self.redis_client = redis.from_url(redis_url)
            self.use_redis = True
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory store: {e}")
            self.use_redis = False
            self.events: List[SecurityEvent] = []
            self.metrics = SecurityMetrics()

    async def store_event(self, event: SecurityEvent):
        """Store security event."""
        if self.use_redis:
            try:
                event_data = {
                    "id": event.id,
                    "event_type": event.event_type.value,
                    "severity": event.severity.value,
                    "timestamp": event.timestamp.isoformat(),
                    "source": event.source,
                    "title": event.title,
                    "description": event.description,
                    "metadata": json.dumps(event.metadata),
                    "affected_assets": json.dumps(event.affected_assets),
                    "remediation_status": event.remediation_status,
                    "correlation_id": event.correlation_id
                }

                # Store in Redis with TTL
                await self.redis_client.hset(f"event:{event.id}", mapping=event_data)
                await self.redis_client.expire(f"event:{event.id}", 86400 * 7)  # 7 days

                # Add to timeline
                await self.redis_client.zadd("event_timeline", {event.id: event.timestamp.timestamp()})

                # Update counters
                await self.redis_client.incr(f"events:{event.event_type.value}:count")
                await self.redis_client.incr(f"events:{event.severity.value}:count")

            except Exception as e:
                logger.error(f"Failed to store event in Redis: {e}")
                # Fallback to in-memory
                self.events.append(event)
        else:
            self.events.append(event)
            # Keep only last 1000 events in memory
            if len(self.events) > 1000:
                self.events = self.events[-1000:]

    async def get_recent_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent security events."""
        if self.use_redis:
            try:
                # Get recent event IDs from timeline
                event_ids = await self.redis_client.zrevrange("event_timeline", 0, limit-1)
                events = []

                for event_id in event_ids:
                    event_data = await self.redis_client.hgetall(f"event:{event_id}")
                    if event_data:
                        events.append({
                            "id": event_data.get("id"),
                            "event_type": event_data.get("event_type"),
                            "severity": event_data.get("severity"),
                            "timestamp": event_data.get("timestamp"),
                            "source": event_data.get("source"),
                            "title": event_data.get("title"),
                            "description": event_data.get("description"),
                            "metadata": json.loads(event_data.get("metadata", "{}")),
                            "affected_assets": json.loads(event_data.get("affected_assets", "[]")),
                            "remediation_status": event_data.get("remediation_status"),
                            "correlation_id": event_data.get("correlation_id")
                        })

                return events
            except Exception as e:
                logger.error(f"Failed to get events from Redis: {e}")
                return []
        else:
            return [asdict(event) for event in self.events[-limit:]]

    async def update_metrics(self, metrics: SecurityMetrics):
        """Update security metrics."""
        if self.use_redis:
            try:
                metrics_data = metrics.dict()
                # Convert datetime to string
                if metrics_data.get("last_scan_time"):
                    metrics_data["last_scan_time"] = metrics_data["last_scan_time"].isoformat()

                await self.redis_client.hset("security_metrics", mapping=metrics_data)
            except Exception as e:
                logger.error(f"Failed to update metrics in Redis: {e}")
                self.metrics = metrics
        else:
            self.metrics = metrics

    async def get_metrics(self) -> SecurityMetrics:
        """Get current security metrics."""
        if self.use_redis:
            try:
                metrics_data = await self.redis_client.hgetall("security_metrics")
                if metrics_data:
                    # Convert string values back to appropriate types
                    for key, value in metrics_data.items():
                        if key in ['total_vulnerabilities', 'critical_vulnerabilities',
                                  'high_vulnerabilities', 'medium_vulnerabilities',
                                  'low_vulnerabilities', 'active_scans', 'threats_detected_24h',
                                  'total_assets', 'protected_assets']:
                            metrics_data[key] = int(value)
                        elif key in ['compliance_score', 'risk_score', 'uptime_percentage']:
                            metrics_data[key] = float(value)
                        elif key == 'last_scan_time' and value:
                            metrics_data[key] = datetime.fromisoformat(value)

                    return SecurityMetrics(**metrics_data)
            except Exception as e:
                logger.error(f"Failed to get metrics from Redis: {e}")

        return self.metrics or SecurityMetrics()

class RealTimeSecurityMonitor:
    """Main real-time security monitoring system."""

    def __init__(self, redis_url: str = DEFAULT_REDIS_URL):
        self.connection_manager = ConnectionManager()
        self.event_store = SecurityEventStore(redis_url)
        self.app = FastAPI(title="Scout Real-Time Security Monitor")
        self.threat_feeds: List[ThreatFeed] = []
        self.setup_routes()

        # Background tasks
        self.monitoring_tasks: List[asyncio.Task] = []
        self.is_running = False

    def setup_routes(self):
        """Setup FastAPI routes."""

        @self.app.websocket("/ws/{client_id}")
        async def websocket_endpoint(websocket: WebSocket, client_id: str):
            await self.connection_manager.connect(websocket, client_id)
            try:
                while True:
                    # Listen for client messages (subscriptions, filters, etc.)
                    data = await websocket.receive_text()
                    message = json.loads(data)

                    if message.get("type") == "subscribe":
                        event_types = message.get("event_types", [])
                        self.connection_manager.subscribe_to_events(client_id, event_types)
                        await self.connection_manager.send_personal_message({
                            "type": "subscription_confirmed",
                            "event_types": event_types
                        }, client_id)

                    elif message.get("type") == "get_metrics":
                        metrics = await self.event_store.get_metrics()
                        await self.connection_manager.send_personal_message({
                            "type": "metrics_update",
                            "data": metrics.dict()
                        }, client_id)

                    elif message.get("type") == "get_recent_events":
                        limit = message.get("limit", 50)
                        events = await self.event_store.get_recent_events(limit)
                        await self.connection_manager.send_personal_message({
                            "type": "events_history",
                            "data": events
                        }, client_id)

            except WebSocketDisconnect:
                self.connection_manager.disconnect(client_id)

        @self.app.get("/")
        async def dashboard():
            """Serve the dashboard HTML."""
            return HTMLResponse(content=self.get_dashboard_html())

        @self.app.get("/api / metrics")
        async def get_metrics():
            """Get current security metrics."""
            metrics = await self.event_store.get_metrics()
            return metrics.dict()

        @self.app.get("/api / events")
        async def get_events(limit: int = 100):
            """Get recent security events."""
            events = await self.event_store.get_recent_events(limit)
            return {"events": events}

        @self.app.get("/api / threats")
        async def get_threat_feeds():
            """Get current threat intelligence feeds."""
            return {"threats": [threat.dict() for threat in self.threat_feeds]}

        @self.app.get("/api / status")
        async def get_system_status():
            """Get monitoring system status."""
            connection_stats = self.connection_manager.get_connection_stats()
            return {
                "status": "running" if self.is_running else "stopped",
                "connections": connection_stats,
                "uptime": time.time()-self.start_time if hasattr(self, 'start_time') else 0
            }

    async def emit_event(self, event: SecurityEvent):
        """Emit a security event to all connected clients."""
        await self.event_store.store_event(event)

        # Broadcast to WebSocket clients
        message = {
            "type": "security_event",
            "data": {
                "id": event.id,
                "event_type": event.event_type.value,
                "severity": event.severity.value,
                "timestamp": event.timestamp.isoformat(),
                "source": event.source,
                "title": event.title,
                "description": event.description,
                "metadata": event.metadata,
                "affected_assets": event.affected_assets,
                "remediation_status": event.remediation_status,
                "correlation_id": event.correlation_id
            }
        }

        await self.connection_manager.broadcast(message, event.event_type.value)

    async def update_metrics(self, metrics: SecurityMetrics):
        """Update and broadcast security metrics."""
        await self.event_store.update_metrics(metrics)

        message = {
            "type": "metrics_update",
            "data": metrics.dict()
        }

        await self.connection_manager.broadcast(message, "metrics")

    async def add_threat_feed(self, threat: ThreatFeed):
        """Add new threat intelligence to feed."""
        self.threat_feeds.append(threat)

        # Keep only last 100 threats in memory
        if len(self.threat_feeds) > 100:
            self.threat_feeds = self.threat_feeds[-100:]

        message = {
            "type": "threat_update",
            "data": threat.dict()
        }

        await self.connection_manager.broadcast(message, "threats")

    async def start_monitoring(self):
        """Start background monitoring tasks."""
        self.is_running = True
        self.start_time = time.time()

        # Start background tasks
        self.monitoring_tasks = [
            asyncio.create_task(self.metrics_updater()),
            asyncio.create_task(self.threat_feed_updater()),
            asyncio.create_task(self.system_health_monitor())
        ]

        logger.info("Real-time security monitoring started")

    async def stop_monitoring(self):
        """Stop background monitoring tasks."""
        self.is_running = False

        for task in self.monitoring_tasks:
            task.cancel()

        await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
        logger.info("Real-time security monitoring stopped")

    async def metrics_updater(self):
        """Background task to update metrics periodically."""
        while self.is_running:
            try:
                # This would integrate with actual Scout CLI scanning results
                metrics = await self.calculate_current_metrics()
                await self.update_metrics(metrics)

                await asyncio.sleep(30)  # Update every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics updater error: {e}")
                await asyncio.sleep(60)

    async def threat_feed_updater(self):
        """Background task to fetch threat intelligence."""
        while self.is_running:
            try:
                # This would integrate with threat intelligence sources
                new_threats = await self.fetch_threat_intelligence()

                for threat in new_threats:
                    await self.add_threat_feed(threat)

                await asyncio.sleep(300)  # Update every 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Threat feed updater error: {e}")
                await asyncio.sleep(600)

    async def system_health_monitor(self):
        """Background task to monitor system health."""
        while self.is_running:
            try:
                # Monitor connection health
                now = datetime.now()
                stale_connections = []

                for client_id, metadata in self.connection_manager.connection_metadata.items():
                    if (now-metadata["last_activity"]).seconds > 600:  # 10 minutes
                        stale_connections.append(client_id)

                # Clean up stale connections
                for client_id in stale_connections:
                    self.connection_manager.disconnect(client_id)

                await asyncio.sleep(60)  # Check every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"System health monitor error: {e}")
                await asyncio.sleep(120)

    async def calculate_current_metrics(self) -> SecurityMetrics:
        """Calculate current security metrics from Scout CLI data."""
        # This would integrate with actual Scout CLI results
        # For now, return sample metrics

        current_time = datetime.now()

        return SecurityMetrics(
            total_vulnerabilities=42,
            critical_vulnerabilities=3,
            high_vulnerabilities=8,
            medium_vulnerabilities=15,
            low_vulnerabilities=16,
            active_scans=2,
            threats_detected_24h=7,
            compliance_score=85.5,
            risk_score=6.2,
            uptime_percentage=99.7,
            last_scan_time=current_time-timedelta(minutes=15),
            total_assets=156,
            protected_assets=142
        )

    async def fetch_threat_intelligence(self) -> List[ThreatFeed]:
        """
    Fetch threat intelligence from various sources."""
        # This would integrate with real threat intelligence feeds
        # For now, return sample data

        return [
            ThreatFeed(
                feed_id=str(uuid.uuid4()),
                source="MISP",
                threat_type="malware",
                indicators=["192.168.1.100", "evil.com"],
                severity=AlertSeverity.HIGH,
                confidence=0.85,
                timestamp=datetime.now(),
                description="New malware campaign detected",
                mitigation=["Block IP addresses", "Update endpoint protection"]
            )
        ]

    def get_dashboard_html(self) -> str:
        """Generate dashboard HTML with WebSocket integration."""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title > Scout Security Monitor-Real-Time Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0d1117;
            color: #c9d1d9;
            overflow-x: hidden;
        }
        .dashboard {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            grid-gap: 20px;
            padding: 20px;
            min-height: 100vh;
        }
        .card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .card h2 {
            color: #58a6ff;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 8px;
            background: #0d1117;
            border-radius: 4px;
        }
        .critical { color: #f85149; }
        .high { color: #ff8c00; }
        .medium { color: #d29922; }
        .low { color: #56d364; }
        .info { color: #58a6ff; }

        .events-feed {
            grid-column: span 2;
            max-height: 400px;
            overflow-y: auto;
        }
        .event {
            margin-bottom: 10px;
            padding: 10px;
            background: #0d1117;
            border-left: 4px solid #58a6ff;
            border-radius: 4px;
        }
        .event.critical { border-left-color: #f85149; }
        .event.high { border-left-color: #ff8c00; }
        .event.medium { border-left-color: #d29922; }
        .event.low { border-left-color: #56d364; }

        .connection-status {
            position: fixed;
            top: 10px;
            right: 10px;
            padding: 8px 12px;
            border-radius: 4px;
            background: #1f6feb;
            color: white;
            font-size: 0.9em;
        }
        .connection-status.disconnected { background: #da3633; }

        .threats-feed { max-height: 300px; overflow-y: auto; }
        .threat {
            margin-bottom: 8px;
            padding: 8px;
            background: #0d1117;
            border-radius: 4px;
            border-left: 3px solid #f85149;
        }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .live-indicator {
            animation: pulse 2s infinite;
            color: #56d364;
        }
    </style>
</head>
<body>
    <div class="connection-status" id="connectionStatus">🔴 Connecting...</div>

    <div class="dashboard">
        <!-- Security Metrics -->
        <div class="card">
            <h2>🛡️ Security Metrics <span class="live-indicator" id="liveIndicator">●</span></h2>
            <div id="metricsContainer">
                <div class="metric">
                    <span > Total Vulnerabilities:</span>
                    <span id="totalVulns">-</span>
                </div>
                <div class="metric">
                    <span class="critical">Critical:</span>
                    <span id="criticalVulns">-</span>
                </div>
                <div class="metric">
                    <span class="high">High:</span>
                    <span id="highVulns">-</span>
                </div>
                <div class="metric">
                    <span class="medium">Medium:</span>
                    <span id="mediumVulns">-</span>
                </div>
                <div class="metric">
                    <span class="low">Low:</span>
                    <span id="lowVulns">-</span>
                </div>
                <div class="metric">
                    <span > Risk Score:</span>
                    <span id="riskScore">-</span>
                </div>
                <div class="metric">
                    <span > Compliance Score:</span>
                    <span id="complianceScore">-</span>
                </div>
            </div>
        </div>

        <!-- Threat Intelligence -->
        <div class="card">
            <h2>🎯 Threat Intelligence</h2>
            <div class="threats-feed" id="threatsContainer">
                <div class="threat">No threats detected</div>
            </div>
        </div>

        <!-- Real-Time Events -->
        <div class="card events-feed">
            <h2>📡 Real-Time Security Events</h2>
            <div id="eventsContainer">
                <div class="event info">Monitoring system initialized</div>
            </div>
        </div>
    </div>

    <script>
        class SecurityDashboard {:
            constructor() {
                this.ws = null;
                this.clientId = 'dashboard_' + Date.now();
                this.reconnectAttempts = 0;
                this.maxReconnectAttempts = 5;
                this.connect();
            }

            connect() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws/${this.clientId}`;

                this.ws = new WebSocket(wsUrl);

                this.ws.onopen = () => {
                    console.log('Connected to Scout Security Monitor');
                    document.getElementById('connectionStatus').textContent = '🟢 Connected';
                    document.getElementById('connectionStatus').className = 'connection-status';
                    this.reconnectAttempts = 0;

                    // Subscribe to all event types
                    this.subscribe(['vulnerability_detected',
                        'threat_detected',
                        'scan_completed',
                        'metrics']);

                    // Request initial data
                    this.requestMetrics();
                    this.requestRecentEvents();
                };

                this.ws.onmessage = (event) => {
                    const message = JSON.parse(event.data);
                    this.handleMessage(message);
                };

                this.ws.onclose = () => {
                    console.log('Disconnected from Scout Security Monitor');
                    document.getElementById('connectionStatus').textContent = '🔴 Disconnected';
                    document.getElementById('connectionStatus').className = 'connection-status disconnected';

                    // Attempt to reconnect
                    if (this.reconnectAttempts < this.maxReconnectAttempts) {
                        this.reconnectAttempts++;
                        setTimeout(() => this.connect(), 5000);
                    }
                };

                this.ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                };
            }

            subscribe(eventTypes) {
                if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                    this.ws.send(JSON.stringify({
                        type: 'subscribe',
                        event_types: eventTypes
                    }));
                }
            }

            requestMetrics() {
                if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                    this.ws.send(JSON.stringify({type: 'get_metrics'}));
                }
            }

            requestRecentEvents() {
                if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                    this.ws.send(JSON.stringify({
                        type: 'get_recent_events',
                        limit: 20
                    }));
                }
            }

            handleMessage(message) {
                switch (message.type) {
                    case 'metrics_update':
                        this.updateMetrics(message.data);
                        break;
                    case 'security_event':
                        this.addEvent(message.data);
                        break;
                    case 'threat_update':
                        this.addThreat(message.data);
                        break;
                    case 'events_history':
                        this.loadEventHistory(message.data);
                        break;
                    default:
                        console.log('Unknown message type:', message.type);
                }
            }

            updateMetrics(metrics) {
                document.getElementById('totalVulns').textContent = metrics.total_vulnerabilities || 0;
                document.getElementById('criticalVulns').textContent = metrics.critical_vulnerabilities || 0;
                document.getElementById('highVulns').textContent = metrics.high_vulnerabilities || 0;
                document.getElementById('mediumVulns').textContent = metrics.medium_vulnerabilities || 0;
                document.getElementById('lowVulns').textContent = metrics.low_vulnerabilities || 0;
                document.getElementById('riskScore').textContent = (metrics.risk_score || 0).toFixed(1);
                document.getElementById('complianceScore').textContent = (metrics.compliance_score || 0).toFixed(1) + '%';
            }

            addEvent(event) {
                const container = document.getElementById('eventsContainer');
                const eventEl = document.createElement('div');
                eventEl.className = `event ${event.severity}`;

                const timestamp = new Date(event.timestamp).toLocaleTimeString();
                eventEl.innerHTML = `
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <strong>${event.title}</strong>
                        <span style="font-size: 0.8em; opacity: 0.7;">${timestamp}</span>
                    </div>
                    <div style="font-size: 0.9em;">${event.description}</div>
                    <div style="font-size: 0.8em; opacity: 0.6; margin-top: 5px;">
                        Source: ${event.source} | Type: ${event.event_type}
                    </div>
                `;

                container.insertBefore(eventEl, container.firstChild);

                // Keep only last 50 events visible
                while (container.children.length > 50) {
                    container.removeChild(container.lastChild);
                }
            }

            loadEventHistory(events) {
                const container = document.getElementById('eventsContainer');
                container.innerHTML = '';

                events.forEach(event => this.addEvent(event));
            }

            addThreat(threat) {
                const container = document.getElementById('threatsContainer');
                const threatEl = document.createElement('div');
                threatEl.className = 'threat';

                const timestamp = new Date(threat.timestamp).toLocaleTimeString();
                threatEl.innerHTML = `
                    <div style="font-weight: bold; margin-bottom: 3px;">${threat.threat_type}</div>
                    <div style="font-size: 0.9em;">${threat.description}</div>
                    <div style="font-size: 0.8em; opacity: 0.6; margin-top: 3px;">
                        Source: ${threat.source} | Confidence: ${(threat.confidence * 100).toFixed(0)}%
                    </div>
                `;

                container.insertBefore(threatEl, container.firstChild);

                // Keep only last 20 threats visible
                while (container.children.length > 20) {
                    container.removeChild(container.lastChild);
                }
            }
        }

        // Initialize dashboard when page loads
        document.addEventListener('DOMContentLoaded', () => {
            new SecurityDashboard();
        });
    </script>
</body>
</html>
        '''

# Integration functions for Scout CLI
def create_security_event(event_type: str, severity: str, title: str, description: str,
                         source: str = "scout-cli", metadata: Dict[str, Any] = None,
                         affected_assets: List[str] = None) -> SecurityEvent:
    """Create a security event for real-time monitoring."""

    return SecurityEvent(
        id=str(uuid.uuid4()),
        event_type=SecurityEventType(event_type),
        severity=AlertSeverity(severity),
        timestamp=datetime.now(),
        source=source,
        title=title,
        description=description,
        metadata=metadata or {},
        affected_assets=affected_assets or [],
        correlation_id=None
    )

async def start_realtime_monitor(host: str = "127.0.0.1",
port: int = 8000,
redis_url: str = DEFAULT_REDIS_URL):
    """Start the real-time security monitoring server."""

    monitor = RealTimeSecurityMonitor(redis_url)
    await monitor.start_monitoring()

    config = uvicorn.Config(app=monitor.app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)

    try:
        await server.serve()
    finally:
        await monitor.stop_monitoring()

# Example usage for integration
async def example_integration():
    """Example of how to integrate with Scout CLI scanning."""

    monitor = RealTimeSecurityMonitor()
    await monitor.start_monitoring()

    # Simulate vulnerability detection
    event = create_security_event(
        event_type="vulnerability_detected",
        severity="high",
        title="SQL Injection Detected",
        description="SQL injection vulnerability found in login form",
        source="scout-webscan",
        metadata={
            "url": "https://example.com / login",
            "parameter": "username",
            "method": "POST"
        },
        affected_assets=["example.com"]
    )

    await monitor.emit_event(event)

    # Update metrics
    metrics = SecurityMetrics(
        total_vulnerabilities=1,
        high_vulnerabilities=1,
        risk_score=7.5,
        compliance_score=88.0
    )

    await monitor.update_metrics(metrics)

def start_monitoring_server():
    """Start the real-time security monitoring server."""
    pass

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "server":
        asyncio.run(start_realtime_monitor())
    else:
        asyncio.run(example_integration())
