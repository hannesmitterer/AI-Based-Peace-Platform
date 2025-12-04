# NEXUS API Specification

**Version:** 1.0.0  
**Status:** Draft  
**Last Updated:** 2025-11-03

## Overview

The Nexus API is a comprehensive interface for AI-based peace platform coordination, enabling telemetry collection, command execution, task management, AI agent coordination, and secure event streaming. This specification defines the core endpoints, data models, security requirements, and integration patterns for the Nexus system.

## Table of Contents

1. [Architecture](#architecture)
2. [Authentication & Security](#authentication--security)
3. [Core Endpoints](#core-endpoints)
4. [Telemetry System](#telemetry-system)
5. [Command & Control](#command--control)
6. [Task Management](#task-management)
7. [AI Coordination](#ai-coordination)
8. [Event Streaming](#event-streaming)
9. [Data Models](#data-models)
10. [Example Workflows](#example-workflows)
11. [Error Handling](#error-handling)
12. [Rate Limiting](#rate-limiting)

---

## Architecture

### System Components

The Nexus API consists of the following key components:

- **REST API Layer**: HTTP/HTTPS endpoints for synchronous operations
- **WebSocket Gateway**: Real-time bidirectional communication
- **Telemetry Collector**: Aggregates metrics and status data
- **Command Processor**: Executes and tracks commands across agents
- **Task Orchestrator**: Manages task lifecycle and dependencies
- **Event Bus**: Publishes system events to subscribers
- **Security Module**: Handles authentication, authorization, and audit logging

### Communication Patterns

1. **Request/Response**: Standard REST operations
2. **Publish/Subscribe**: Event-driven updates via WebSocket
3. **Command/Reply**: Asynchronous command execution with callbacks
4. **Streaming**: Continuous data flow for telemetry and logs

---

## Authentication & Security

### Authentication Methods

#### 1. API Key Authentication
```http
Authorization: Bearer <API_KEY>
```

#### 2. OAuth 2.0 (Gmail Integration)
```http
Authorization: Bearer <OAUTH_TOKEN>
```

#### 3. Session Tokens
```http
X-Session-Token: <SESSION_TOKEN>
```

### Security Requirements

- All endpoints require HTTPS in production
- API keys must be rotated every 90 days
- Session tokens expire after 24 hours of inactivity
- Rate limiting: 1000 requests/hour per API key
- Audit logging for all authenticated requests
- IP whitelisting available for sensitive operations

### Environment Variables

```bash
# Authentication
NEXUS_API_KEY=your_api_key_here
NEXUS_SECRET_KEY=your_secret_key_here
OAUTH_CLIENT_ID=your_oauth_client_id
OAUTH_CLIENT_SECRET=your_oauth_secret
SESSION_SECRET=your_session_secret

# Security
ALLOWED_ORIGINS=https://your-domain.com
RATE_LIMIT_WINDOW=3600
RATE_LIMIT_MAX_REQUESTS=1000
```

---

## Core Endpoints

### Health Check

**Endpoint:** `GET /api/v1/health`

**Description:** Returns system health status

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-03T01:54:42.407Z",
  "services": {
    "database": "up",
    "redis": "up",
    "websocket": "up"
  }
}
```

### System Status

**Endpoint:** `GET /api/v1/status`

**Description:** Detailed system status including resource usage

**Response:**
```json
{
  "uptime": 86400,
  "activeAgents": 12,
  "pendingTasks": 5,
  "completedTasksToday": 47,
  "cpu": 45.2,
  "memory": 62.8,
  "diskUsage": 38.5
}
```

---

## Telemetry System

### Submit Telemetry

**Endpoint:** `POST /api/v1/telemetry`

**Description:** Submit telemetry data from agents

**Request Body:**
```json
{
  "agentId": "agent-001",
  "timestamp": "2025-11-03T01:54:42.407Z",
  "metrics": {
    "cpu": 45.2,
    "memory": 62.8,
    "taskCount": 3,
    "errorRate": 0.02
  },
  "status": "active",
  "location": {
    "region": "us-east-1",
    "availability": "99.9"
  }
}
```

**Response:**
```json
{
  "telemetryId": "telem-abc123",
  "received": "2025-11-03T01:54:42.407Z",
  "status": "accepted"
}
```

### Query Telemetry

**Endpoint:** `GET /api/v1/telemetry`

**Query Parameters:**
- `agentId` (optional): Filter by agent ID
- `from` (optional): Start timestamp
- `to` (optional): End timestamp
- `limit` (optional): Max results (default: 100)

**Response:**
```json
{
  "telemetry": [
    {
      "agentId": "agent-001",
      "timestamp": "2025-11-03T01:54:42.407Z",
      "metrics": { /* ... */ }
    }
  ],
  "total": 150,
  "page": 1
}
```

### Telemetry Aggregation

**Endpoint:** `GET /api/v1/telemetry/aggregate`

**Description:** Get aggregated telemetry metrics

**Query Parameters:**
- `metric`: Metric name (cpu, memory, taskCount, etc.)
- `aggregation`: Type (avg, min, max, sum)
- `interval`: Time interval (1h, 1d, 7d, 30d)
- `agentId` (optional): Filter by agent

**Response:**
```json
{
  "metric": "cpu",
  "aggregation": "avg",
  "interval": "1h",
  "data": [
    {
      "timestamp": "2025-11-03T01:00:00Z",
      "value": 42.5
    },
    {
      "timestamp": "2025-11-03T02:00:00Z",
      "value": 45.2
    }
  ]
}
```

---

## Command & Control

### Execute Command

**Endpoint:** `POST /api/v1/commands`

**Description:** Execute a command on one or more agents

**Request Body:**
```json
{
  "command": "deploy",
  "targets": ["agent-001", "agent-002"],
  "parameters": {
    "version": "1.2.3",
    "rollback": true
  },
  "timeout": 300,
  "async": true
}
```

**Response:**
```json
{
  "commandId": "cmd-xyz789",
  "status": "pending",
  "targets": ["agent-001", "agent-002"],
  "createdAt": "2025-11-03T01:54:42.407Z",
  "estimatedCompletion": "2025-11-03T02:00:00Z"
}
```

### Get Command Status

**Endpoint:** `GET /api/v1/commands/{commandId}`

**Response:**
```json
{
  "commandId": "cmd-xyz789",
  "command": "deploy",
  "status": "completed",
  "results": [
    {
      "agentId": "agent-001",
      "status": "success",
      "output": "Deployment successful",
      "completedAt": "2025-11-03T01:58:00Z"
    },
    {
      "agentId": "agent-002",
      "status": "success",
      "output": "Deployment successful",
      "completedAt": "2025-11-03T01:59:00Z"
    }
  ]
}
```

### Cancel Command

**Endpoint:** `DELETE /api/v1/commands/{commandId}`

**Description:** Cancel a pending or running command

**Response:**
```json
{
  "commandId": "cmd-xyz789",
  "status": "cancelled",
  "cancelledAt": "2025-11-03T01:56:00Z"
}
```

---

## Task Management

### Create Task

**Endpoint:** `POST /api/v1/tasks`

**Description:** Create a new task with optional dependencies

**Request Body:**
```json
{
  "name": "Process conflict report",
  "type": "analysis",
  "priority": "high",
  "assignedTo": "agent-001",
  "parameters": {
    "region": "middle-east",
    "conflictId": "conf-456"
  },
  "dependencies": ["task-123"],
  "deadline": "2025-11-04T01:54:42.407Z"
}
```

**Response:**
```json
{
  "taskId": "task-789",
  "status": "pending",
  "createdAt": "2025-11-03T01:54:42.407Z",
  "estimatedDuration": 1800
}
```

### Get Task Status

**Endpoint:** `GET /api/v1/tasks/{taskId}`

**Response:**
```json
{
  "taskId": "task-789",
  "name": "Process conflict report",
  "status": "in_progress",
  "progress": 45,
  "assignedTo": "agent-001",
  "startedAt": "2025-11-03T02:00:00Z",
  "estimatedCompletion": "2025-11-03T02:30:00Z"
}
```

### Update Task

**Endpoint:** `PATCH /api/v1/tasks/{taskId}`

**Description:** Update task properties or mark complete

**Request Body:**
```json
{
  "status": "completed",
  "result": {
    "analysis": "Low risk conflict",
    "recommendations": ["Monitor situation", "Deploy peacekeeping resources"]
  }
}
```

### List Tasks

**Endpoint:** `GET /api/v1/tasks`

**Query Parameters:**
- `status`: Filter by status (pending, in_progress, completed, failed)
- `assignedTo`: Filter by agent ID
- `priority`: Filter by priority (low, medium, high, critical)
- `limit`: Max results (default: 50)
- `offset`: Pagination offset

**Response:**
```json
{
  "tasks": [
    {
      "taskId": "task-789",
      "name": "Process conflict report",
      "status": "in_progress",
      "priority": "high"
    }
  ],
  "total": 47,
  "limit": 50,
  "offset": 0
}
```

---

## AI Coordination

### Register Agent

**Endpoint:** `POST /api/v1/agents`

**Description:** Register a new AI agent in the coordination system

**Request Body:**
```json
{
  "agentId": "agent-003",
  "name": "Conflict Analyzer",
  "capabilities": ["analysis", "prediction", "reporting"],
  "version": "2.1.0",
  "endpoint": "https://agent-003.example.com/api",
  "metadata": {
    "region": "global",
    "specialization": "conflict-resolution"
  }
}
```

**Response:**
```json
{
  "agentId": "agent-003",
  "status": "registered",
  "apiKey": "generated_api_key_here",
  "registeredAt": "2025-11-03T01:54:42.407Z"
}
```

### List Agents

**Endpoint:** `GET /api/v1/agents`

**Query Parameters:**
- `status`: Filter by status (active, inactive, offline)
- `capability`: Filter by capability

**Response:**
```json
{
  "agents": [
    {
      "agentId": "agent-001",
      "name": "Peace Coordinator",
      "status": "active",
      "capabilities": ["coordination", "communication"],
      "lastSeen": "2025-11-03T01:54:00Z"
    }
  ],
  "total": 12
}
```

### Agent Heartbeat

**Endpoint:** `POST /api/v1/agents/{agentId}/heartbeat`

**Description:** Agent status update and keep-alive

**Request Body:**
```json
{
  "status": "active",
  "currentTasks": 3,
  "health": {
    "cpu": 45.2,
    "memory": 62.8
  }
}
```

**Response:**
```json
{
  "acknowledged": true,
  "timestamp": "2025-11-03T01:54:42.407Z",
  "nextHeartbeatIn": 60
}
```

### Agent Coordination Request

**Endpoint:** `POST /api/v1/agents/coordinate`

**Description:** Request coordination between multiple agents for complex tasks

**Request Body:**
```json
{
  "taskId": "task-multi-123",
  "participants": ["agent-001", "agent-002", "agent-003"],
  "coordinationType": "consensus",
  "objective": "Develop comprehensive peace strategy",
  "timeout": 3600
}
```

**Response:**
```json
{
  "coordinationId": "coord-456",
  "status": "initiated",
  "participants": ["agent-001", "agent-002", "agent-003"],
  "sessionUrl": "wss://nexus.example.com/coordination/coord-456"
}
```

---

## Event Streaming

### WebSocket Connection

**Endpoint:** `WS /api/v1/events`

**Description:** Establish WebSocket connection for real-time events

**Connection:**
```javascript
const ws = new WebSocket('wss://nexus.example.com/api/v1/events?token=<API_KEY>');
```

### Event Types

1. **agent.status**: Agent status changes
2. **task.created**: New task created
3. **task.updated**: Task status/progress updated
4. **task.completed**: Task completed
5. **command.executed**: Command execution
6. **telemetry.threshold**: Metric threshold exceeded
7. **alert.security**: Security event
8. **system.error**: System error

### Subscribe to Events

**Message:**
```json
{
  "type": "subscribe",
  "events": ["task.updated", "agent.status"],
  "filters": {
    "agentId": "agent-001"
  }
}
```

### Event Message Format

```json
{
  "eventId": "evt-123",
  "type": "task.updated",
  "timestamp": "2025-11-03T01:54:42.407Z",
  "data": {
    "taskId": "task-789",
    "status": "completed",
    "result": { /* ... */ }
  },
  "source": "agent-001"
}
```

### Unsubscribe from Events

**Message:**
```json
{
  "type": "unsubscribe",
  "events": ["task.updated"]
}
```

---

## Data Models

### Agent

```typescript
interface Agent {
  agentId: string;
  name: string;
  status: 'active' | 'inactive' | 'offline';
  capabilities: string[];
  version: string;
  endpoint: string;
  registeredAt: string;
  lastSeen: string;
  metadata?: Record<string, any>;
}
```

### Task

```typescript
interface Task {
  taskId: string;
  name: string;
  type: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'critical';
  assignedTo: string;
  createdAt: string;
  startedAt?: string;
  completedAt?: string;
  deadline?: string;
  progress?: number;
  parameters: Record<string, any>;
  dependencies?: string[];
  result?: Record<string, any>;
}
```

### Command

```typescript
interface Command {
  commandId: string;
  command: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  targets: string[];
  parameters: Record<string, any>;
  createdAt: string;
  completedAt?: string;
  timeout: number;
  async: boolean;
  results?: CommandResult[];
}

interface CommandResult {
  agentId: string;
  status: 'success' | 'failed' | 'timeout';
  output: string;
  completedAt: string;
  error?: string;
}
```

### Telemetry

```typescript
interface Telemetry {
  telemetryId: string;
  agentId: string;
  timestamp: string;
  metrics: Record<string, number>;
  status: string;
  location?: {
    region: string;
    availability: string;
  };
}
```

### Event

```typescript
interface Event {
  eventId: string;
  type: string;
  timestamp: string;
  data: Record<string, any>;
  source: string;
  severity?: 'info' | 'warning' | 'error' | 'critical';
}
```

---

## Example Workflows

### Workflow 1: Deploy Agent Update

```
1. POST /api/v1/commands
   {
     "command": "update",
     "targets": ["agent-001"],
     "parameters": { "version": "2.0.0" }
   }
   → Response: { "commandId": "cmd-123" }

2. GET /api/v1/commands/cmd-123
   → Poll until status is "completed"

3. GET /api/v1/agents/agent-001
   → Verify version is "2.0.0"
```

### Workflow 2: Multi-Agent Task Coordination

```
1. POST /api/v1/tasks
   {
     "name": "Comprehensive conflict analysis",
     "type": "multi-agent"
   }
   → Response: { "taskId": "task-456" }

2. POST /api/v1/agents/coordinate
   {
     "taskId": "task-456",
     "participants": ["agent-001", "agent-002", "agent-003"]
   }
   → Response: { "coordinationId": "coord-789" }

3. WebSocket /api/v1/events
   Subscribe to: ["task.updated", "coordination.message"]
   → Receive real-time updates

4. GET /api/v1/tasks/task-456
   → Check final result when complete
```

### Workflow 3: Telemetry Monitoring & Alerts

```
1. POST /api/v1/telemetry/thresholds
   {
     "metric": "cpu",
     "condition": "greater_than",
     "value": 80,
     "agentId": "agent-001"
   }

2. WebSocket /api/v1/events
   Subscribe to: ["telemetry.threshold"]

3. Receive alert when threshold exceeded:
   {
     "type": "telemetry.threshold",
     "data": {
       "metric": "cpu",
       "value": 85.2,
       "agentId": "agent-001"
     }
   }

4. POST /api/v1/commands
   {
     "command": "scale",
     "targets": ["agent-001"],
     "parameters": { "action": "add_resources" }
   }
```

### Workflow 4: Scheduled Task with Dependencies

```
1. POST /api/v1/tasks
   {
     "name": "Daily conflict report",
     "type": "scheduled",
     "schedule": "0 0 * * *"
   }
   → Response: { "taskId": "task-daily-001" }

2. POST /api/v1/tasks
   {
     "name": "Analyze daily report",
     "dependencies": ["task-daily-001"],
     "assignedTo": "agent-002"
   }
   → Response: { "taskId": "task-analysis-001" }

3. POST /api/v1/tasks
   {
     "name": "Distribute recommendations",
     "dependencies": ["task-analysis-001"],
     "assignedTo": "agent-003"
   }
   → Response: { "taskId": "task-distribute-001" }

4. GET /api/v1/tasks?status=completed&date=today
   → View all completed tasks in pipeline
```

---

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Invalid parameter: agentId is required",
    "details": {
      "field": "agentId",
      "constraint": "required"
    },
    "timestamp": "2025-11-03T01:54:42.407Z",
    "requestId": "req-abc123"
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| INVALID_REQUEST | 400 | Malformed request or invalid parameters |
| UNAUTHORIZED | 401 | Missing or invalid authentication |
| FORBIDDEN | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource not found |
| CONFLICT | 409 | Resource conflict (e.g., duplicate ID) |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests |
| INTERNAL_ERROR | 500 | Server error |
| SERVICE_UNAVAILABLE | 503 | Service temporarily unavailable |
| TIMEOUT | 504 | Request timeout |

### Retry Policy

For transient errors (5xx status codes):
- Use exponential backoff: 1s, 2s, 4s, 8s, 16s
- Maximum 5 retry attempts
- Include `X-Retry-Count` header

---

## Rate Limiting

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1699000000
```

### Rate Limit Tiers

| Tier | Requests/Hour | Burst Limit |
|------|---------------|-------------|
| Free | 1,000 | 100 |
| Standard | 10,000 | 500 |
| Premium | 100,000 | 2,000 |
| Enterprise | Unlimited | Custom |

### Rate Limit Bypass

Critical operations can request rate limit exemption:

```http
X-Priority: critical
X-Exemption-Token: <EXEMPTION_TOKEN>
```

---

## Versioning

API versions are specified in the URL path:
- Current: `/api/v1/`
- Beta features: `/api/v2-beta/`

Version deprecation policy:
- 6 months notice for breaking changes
- 12 months support for deprecated versions
- Migration guides provided

---

## Support & Documentation

- **API Documentation**: https://docs.nexus-api.example.com
- **Status Page**: https://status.nexus-api.example.com
- **Support Email**: support@nexus-api.example.com
- **GitHub Issues**: https://github.com/example/nexus-api/issues

---

## Changelog

### v1.0.0 (2025-11-03)
- Initial specification release
- Core endpoints for telemetry, commands, tasks
- AI coordination features
- WebSocket event streaming
- Security and authentication framework

---

**End of Specification**
