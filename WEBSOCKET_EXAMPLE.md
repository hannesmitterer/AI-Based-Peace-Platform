# WebSocket Example - Bidirectional Messaging

Complete examples for implementing WebSocket bidirectional messaging with the Nexus API Platform using Node.js.

## Table of Contents

1. [Overview](#overview)
2. [Server Implementation](#server-implementation)
3. [Client Implementation](#client-implementation)
4. [Message Protocol](#message-protocol)
5. [Authentication](#authentication)
6. [Connection Management](#connection-management)
7. [Event Handling](#event-handling)
8. [Error Handling](#error-handling)
9. [Production Deployment](#production-deployment)

---

## Overview

WebSocket provides full-duplex communication channels over a single TCP connection, enabling real-time bidirectional data flow between clients and the Nexus API server.

### Use Cases

- **Real-time Telemetry**: Stream agent metrics and status updates
- **Event Notifications**: Push task updates, alerts, and system events
- **Command Execution**: Send commands and receive immediate responses
- **Multi-Agent Coordination**: Enable real-time collaboration between agents

### Architecture

```
┌─────────────┐         WebSocket          ┌─────────────┐
│   Client    │ ◄─────────────────────────► │   Server    │
│  (Browser,  │    Bidirectional Channel    │   (Node.js) │
│   Agent)    │                             │             │
└─────────────┘                             └─────────────┘
                                                    │
                                            ┌───────▼────────┐
                                            │  Event Bus     │
                                            │  (Redis Pub/   │
                                            │   Sub)         │
                                            └────────────────┘
```

---

## Server Implementation

### Step 1: Install Dependencies

```bash
npm install ws redis express
```

### Step 2: Basic WebSocket Server

**server.js**

```javascript
const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const redis = require('redis');

// Create Express app and HTTP server
const app = express();
const server = http.createServer(app);

// Create WebSocket server
const wss = new WebSocket.Server({ 
  server,
  path: '/api/v1/events'
});

// Redis client for pub/sub
const redisClient = redis.createClient({
  url: process.env.REDIS_URL || 'redis://localhost:6379'
});

const redisSubscriber = redisClient.duplicate();

// Connect to Redis
(async () => {
  await redisClient.connect();
  await redisSubscriber.connect();
  console.log('Connected to Redis');
})();

// Store active connections
const clients = new Map();

// WebSocket connection handler
wss.on('connection', async (ws, req) => {
  const clientId = generateClientId();
  
  // Authenticate client
  const token = extractToken(req);
  const user = await authenticateToken(token);
  
  if (!user) {
    ws.close(1008, 'Unauthorized');
    return;
  }

  console.log(`Client connected: ${clientId} (User: ${user.id})`);

  // Store client info
  clients.set(clientId, {
    ws,
    user,
    subscriptions: new Set(),
    lastHeartbeat: Date.now()
  });

  // Send welcome message
  ws.send(JSON.stringify({
    type: 'connected',
    clientId,
    timestamp: new Date().toISOString(),
    message: 'Connected to Nexus API WebSocket'
  }));

  // Handle incoming messages
  ws.on('message', (message) => {
    handleMessage(clientId, message);
  });

  // Handle disconnection
  ws.on('close', () => {
    console.log(`Client disconnected: ${clientId}`);
    const client = clients.get(clientId);
    if (client) {
      // Unsubscribe from all events
      client.subscriptions.forEach(eventType => {
        unsubscribeFromEvent(clientId, eventType);
      });
      clients.delete(clientId);
    }
  });

  // Handle errors
  ws.on('error', (error) => {
    console.error(`WebSocket error for client ${clientId}:`, error);
  });

  // Start heartbeat
  startHeartbeat(clientId);
});

// Message handler
function handleMessage(clientId, message) {
  const client = clients.get(clientId);
  if (!client) return;

  try {
    const data = JSON.parse(message);
    
    switch (data.type) {
      case 'subscribe':
        handleSubscribe(clientId, data);
        break;
      case 'unsubscribe':
        handleUnsubscribe(clientId, data);
        break;
      case 'ping':
        handlePing(clientId);
        break;
      case 'command':
        handleCommand(clientId, data);
        break;
      case 'telemetry':
        handleTelemetry(clientId, data);
        break;
      default:
        sendError(clientId, `Unknown message type: ${data.type}`);
    }
  } catch (error) {
    console.error(`Error parsing message from ${clientId}:`, error);
    sendError(clientId, 'Invalid JSON message');
  }
}

// Subscribe to events
function handleSubscribe(clientId, data) {
  const client = clients.get(clientId);
  if (!client) return;

  const { events, filters } = data;

  events.forEach(eventType => {
    client.subscriptions.add(eventType);
    
    // Subscribe to Redis channel
    const channel = `nexus:events:${eventType}`;
    redisSubscriber.subscribe(channel, (message) => {
      const event = JSON.parse(message);
      
      // Apply filters if provided
      if (filters && !matchesFilters(event, filters)) {
        return;
      }

      // Send to client
      if (client.ws.readyState === WebSocket.OPEN) {
        client.ws.send(JSON.stringify({
          type: 'event',
          eventType,
          data: event
        }));
      }
    });
  });

  // Acknowledge subscription
  client.ws.send(JSON.stringify({
    type: 'subscribed',
    events,
    timestamp: new Date().toISOString()
  }));

  console.log(`Client ${clientId} subscribed to:`, events);
}

// Unsubscribe from events
function handleUnsubscribe(clientId, data) {
  const client = clients.get(clientId);
  if (!client) return;

  const { events } = data;

  events.forEach(eventType => {
    client.subscriptions.delete(eventType);
    
    const channel = `nexus:events:${eventType}`;
    redisSubscriber.unsubscribe(channel);
  });

  client.ws.send(JSON.stringify({
    type: 'unsubscribed',
    events,
    timestamp: new Date().toISOString()
  }));

  console.log(`Client ${clientId} unsubscribed from:`, events);
}

// Handle ping for heartbeat
function handlePing(clientId) {
  const client = clients.get(clientId);
  if (!client) return;

  client.lastHeartbeat = Date.now();
  client.ws.send(JSON.stringify({
    type: 'pong',
    timestamp: new Date().toISOString()
  }));
}

// Handle command execution
async function handleCommand(clientId, data) {
  const client = clients.get(clientId);
  if (!client) return;

  try {
    const { command, parameters } = data;
    
    // Execute command (implement your logic)
    const result = await executeCommand(command, parameters, client.user);
    
    // Send result
    client.ws.send(JSON.stringify({
      type: 'command_result',
      commandId: result.commandId,
      status: 'success',
      data: result
    }));
  } catch (error) {
    sendError(clientId, `Command execution failed: ${error.message}`);
  }
}

// Handle telemetry submission
async function handleTelemetry(clientId, data) {
  const client = clients.get(clientId);
  if (!client) return;

  try {
    const { metrics, agentId } = data;
    
    // Store telemetry (implement your logic)
    await storeTelemetry(agentId, metrics);
    
    // Acknowledge receipt
    client.ws.send(JSON.stringify({
      type: 'telemetry_ack',
      timestamp: new Date().toISOString()
    }));

    // Publish to other subscribers
    await publishEvent('telemetry.received', {
      agentId,
      metrics,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    sendError(clientId, `Telemetry submission failed: ${error.message}`);
  }
}

// Heartbeat mechanism
function startHeartbeat(clientId) {
  const interval = setInterval(() => {
    const client = clients.get(clientId);
    if (!client) {
      clearInterval(interval);
      return;
    }

    // Check if client is still alive
    const timeSinceLastHeartbeat = Date.now() - client.lastHeartbeat;
    if (timeSinceLastHeartbeat > 60000) { // 60 seconds timeout
      console.log(`Client ${clientId} timeout, closing connection`);
      client.ws.close(1000, 'Heartbeat timeout');
      clearInterval(interval);
      return;
    }

    // Send ping
    if (client.ws.readyState === WebSocket.OPEN) {
      client.ws.send(JSON.stringify({
        type: 'ping'
      }));
    }
  }, 30000); // Ping every 30 seconds
}

// Publish event to all subscribers
async function publishEvent(eventType, data) {
  const channel = `nexus:events:${eventType}`;
  await redisClient.publish(channel, JSON.stringify(data));
}

// Broadcast to all connected clients
function broadcast(message) {
  clients.forEach((client) => {
    if (client.ws.readyState === WebSocket.OPEN) {
      client.ws.send(JSON.stringify(message));
    }
  });
}

// Helper functions
function generateClientId() {
  return `client-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

function extractToken(req) {
  const url = new URL(req.url, `http://${req.headers.host}`);
  return url.searchParams.get('token');
}

async function authenticateToken(token) {
  // Implement your authentication logic
  if (!token) return null;
  
  // Example: Verify JWT or API key
  // const user = await verifyToken(token);
  // return user;
  
  // Placeholder
  return { id: 'user-123', name: 'Test User' };
}

function matchesFilters(event, filters) {
  return Object.keys(filters).every(key => {
    return event[key] === filters[key];
  });
}

function sendError(clientId, message) {
  const client = clients.get(clientId);
  if (!client) return;

  client.ws.send(JSON.stringify({
    type: 'error',
    message,
    timestamp: new Date().toISOString()
  }));
}

async function executeCommand(command, parameters, user) {
  // Implement your command execution logic
  return {
    commandId: `cmd-${Date.now()}`,
    command,
    status: 'executed',
    result: 'Success'
  };
}

async function storeTelemetry(agentId, metrics) {
  // Implement your telemetry storage logic
  console.log(`Storing telemetry for agent ${agentId}:`, metrics);
}

// Start server
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
  console.log(`WebSocket endpoint: ws://localhost:${PORT}/api/v1/events`);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('SIGTERM received, closing server...');
  
  // Close all WebSocket connections
  clients.forEach((client, clientId) => {
    client.ws.close(1000, 'Server shutting down');
  });
  
  // Close server
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});
```

---

## Client Implementation

### Node.js Client

**client.js**

```javascript
const WebSocket = require('ws');

class NexusWebSocketClient {
  constructor(url, token) {
    this.url = url;
    this.token = token;
    this.ws = null;
    this.subscriptions = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
  }

  connect() {
    return new Promise((resolve, reject) => {
      const wsUrl = `${this.url}?token=${this.token}`;
      this.ws = new WebSocket(wsUrl);

      this.ws.on('open', () => {
        console.log('Connected to Nexus API WebSocket');
        this.reconnectAttempts = 0;
        resolve();
      });

      this.ws.on('message', (data) => {
        this.handleMessage(data);
      });

      this.ws.on('close', (code, reason) => {
        console.log(`WebSocket closed: ${code} - ${reason}`);
        this.handleReconnect();
      });

      this.ws.on('error', (error) => {
        console.error('WebSocket error:', error);
        reject(error);
      });
    });
  }

  handleMessage(data) {
    try {
      const message = JSON.parse(data);

      switch (message.type) {
        case 'connected':
          console.log('Connection established:', message);
          break;
        case 'event':
          this.handleEvent(message);
          break;
        case 'subscribed':
          console.log('Subscribed to events:', message.events);
          break;
        case 'unsubscribed':
          console.log('Unsubscribed from events:', message.events);
          break;
        case 'ping':
          this.send({ type: 'pong' });
          break;
        case 'pong':
          // Heartbeat received
          break;
        case 'command_result':
          console.log('Command result:', message);
          break;
        case 'telemetry_ack':
          console.log('Telemetry acknowledged');
          break;
        case 'error':
          console.error('Server error:', message.message);
          break;
        default:
          console.log('Unknown message type:', message.type);
      }
    } catch (error) {
      console.error('Error parsing message:', error);
    }
  }

  handleEvent(message) {
    const { eventType, data } = message;
    const handlers = this.subscriptions.get(eventType);
    
    if (handlers) {
      handlers.forEach(handler => handler(data));
    }
  }

  subscribe(events, handler) {
    events.forEach(eventType => {
      if (!this.subscriptions.has(eventType)) {
        this.subscriptions.set(eventType, new Set());
      }
      this.subscriptions.get(eventType).add(handler);
    });

    this.send({
      type: 'subscribe',
      events
    });
  }

  unsubscribe(events) {
    events.forEach(eventType => {
      this.subscriptions.delete(eventType);
    });

    this.send({
      type: 'unsubscribe',
      events
    });
  }

  sendCommand(command, parameters) {
    this.send({
      type: 'command',
      command,
      parameters
    });
  }

  sendTelemetry(agentId, metrics) {
    this.send({
      type: 'telemetry',
      agentId,
      metrics,
      timestamp: new Date().toISOString()
    });
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.error('WebSocket is not connected');
    }
  }

  handleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
    
    setTimeout(() => {
      this.connect().catch(err => {
        console.error('Reconnection failed:', err);
      });
    }, delay);
  }

  close() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

// Usage example
async function main() {
  const client = new NexusWebSocketClient(
    'ws://localhost:3000/api/v1/events',
    'your_api_token_here'
  );

  try {
    await client.connect();

    // Subscribe to events
    client.subscribe(['task.updated', 'agent.status'], (event) => {
      console.log('Event received:', event);
    });

    // Send telemetry
    setInterval(() => {
      client.sendTelemetry('agent-001', {
        cpu: Math.random() * 100,
        memory: Math.random() * 100,
        taskCount: Math.floor(Math.random() * 10)
      });
    }, 5000);

    // Send command
    client.sendCommand('deploy', {
      version: '1.2.3',
      target: 'production'
    });

  } catch (error) {
    console.error('Failed to connect:', error);
  }
}

// Run if executed directly
if (require.main === module) {
  main();
}

module.exports = NexusWebSocketClient;
```

### Browser Client

**client-browser.js**

```javascript
class NexusWebSocketClient {
  constructor(url, token) {
    this.url = url;
    this.token = token;
    this.ws = null;
    this.eventHandlers = new Map();
  }

  connect() {
    return new Promise((resolve, reject) => {
      const wsUrl = `${this.url}?token=${this.token}`;
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('Connected to Nexus API');
        resolve();
      };

      this.ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        this.handleMessage(message);
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        reject(error);
      };

      this.ws.onclose = () => {
        console.log('Disconnected from Nexus API');
      };
    });
  }

  handleMessage(message) {
    if (message.type === 'event') {
      const handlers = this.eventHandlers.get(message.eventType);
      if (handlers) {
        handlers.forEach(handler => handler(message.data));
      }
    }
  }

  on(eventType, handler) {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, new Set());
    }
    this.eventHandlers.get(eventType).add(handler);

    // Subscribe to event
    this.send({
      type: 'subscribe',
      events: [eventType]
    });
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  close() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

// Usage in browser
const client = new NexusWebSocketClient(
  'wss://your-api.example.com/api/v1/events',
  'your_api_token'
);

client.connect().then(() => {
  // Listen for task updates
  client.on('task.updated', (data) => {
    console.log('Task updated:', data);
    updateUI(data);
  });

  // Listen for agent status
  client.on('agent.status', (data) => {
    console.log('Agent status:', data);
  });
});
```

---

## Message Protocol

### Message Format

All messages are JSON-encoded with this structure:

```json
{
  "type": "message_type",
  "data": { /* type-specific data */ },
  "timestamp": "2025-11-03T01:54:42.407Z"
}
```

### Message Types

#### Client → Server

**Subscribe**
```json
{
  "type": "subscribe",
  "events": ["task.updated", "agent.status"],
  "filters": {
    "agentId": "agent-001"
  }
}
```

**Unsubscribe**
```json
{
  "type": "unsubscribe",
  "events": ["task.updated"]
}
```

**Ping**
```json
{
  "type": "ping"
}
```

**Command**
```json
{
  "type": "command",
  "command": "deploy",
  "parameters": {
    "version": "1.2.3"
  }
}
```

**Telemetry**
```json
{
  "type": "telemetry",
  "agentId": "agent-001",
  "metrics": {
    "cpu": 45.2,
    "memory": 62.8
  }
}
```

#### Server → Client

**Connected**
```json
{
  "type": "connected",
  "clientId": "client-123",
  "timestamp": "2025-11-03T01:54:42.407Z"
}
```

**Event**
```json
{
  "type": "event",
  "eventType": "task.updated",
  "data": {
    "taskId": "task-789",
    "status": "completed"
  }
}
```

**Error**
```json
{
  "type": "error",
  "message": "Invalid message format",
  "timestamp": "2025-11-03T01:54:42.407Z"
}
```

---

## Authentication

### Token-based Authentication

```javascript
// Include token in connection URL
const ws = new WebSocket('ws://localhost:3000/api/v1/events?token=YOUR_API_KEY');

// Or in headers (if supported by client)
const ws = new WebSocket('ws://localhost:3000/api/v1/events', {
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY'
  }
});
```

---

## Production Deployment

### NGINX Configuration for WebSocket

```nginx
http {
  map $http_upgrade $connection_upgrade {
    default upgrade;
    '' close;
  }

  upstream websocket {
    server localhost:3000;
  }

  server {
    listen 443 ssl;
    server_name api.nexus.example.com;

    ssl_certificate /etc/ssl/certs/nexus.crt;
    ssl_certificate_key /etc/ssl/private/nexus.key;

    location /api/v1/events {
      proxy_pass http://websocket;
      proxy_http_version 1.1;
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection $connection_upgrade;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
      
      # Timeouts
      proxy_connect_timeout 7d;
      proxy_send_timeout 7d;
      proxy_read_timeout 7d;
    }
  }
}
```

---

**WebSocket Example Guide v1.0.0**  
Last Updated: 2025-11-03
