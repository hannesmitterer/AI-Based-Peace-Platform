# GGI Broadcast Integration Guide

Guide for integrating with the Global Good Initiative (GGI) Broadcast interface for worldwide peace initiative coordination and event distribution.

## Table of Contents

1. [Overview](#overview)
2. [GGI Broadcast API](#ggi-broadcast-api)
3. [Authentication](#authentication)
4. [Publishing Events](#publishing-events)
5. [Webhook Integration](#webhook-integration)
6. [Event Types](#event-types)
7. [Message Formats](#message-formats)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)

---

## Overview

The GGI (Global Good Initiative) Broadcast interface enables the Nexus API Platform to:
- Publish peace initiative updates to a global audience
- Receive real-time notifications from other peace platforms
- Coordinate multi-organization humanitarian efforts
- Share conflict resolution analytics and insights

### Architecture

```
┌──────────────┐         HTTPS          ┌──────────────┐
│  Nexus API   │ ───────────────────────► │  GGI Broadcast│
│  Platform    │ ◄─────────────────────── │  Service     │
└──────────────┘      Webhooks           └──────────────┘
       │                                         │
       │                                         │
       ▼                                         ▼
┌──────────────┐                         ┌──────────────┐
│   Internal   │                         │   Global     │
│   Events     │                         │   Network    │
└──────────────┘                         └──────────────┘
```

---

## GGI Broadcast API

### Base URL

```
Production: https://broadcast.ggi.example.com/api/v1
Staging: https://broadcast-staging.ggi.example.com/api/v1
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/broadcast` | POST | Publish a broadcast message |
| `/subscribe` | POST | Subscribe to event types |
| `/unsubscribe` | POST | Unsubscribe from events |
| `/webhooks` | GET | List configured webhooks |
| `/webhooks` | POST | Register a webhook |
| `/webhooks/{id}` | DELETE | Remove a webhook |
| `/broadcasts` | GET | List recent broadcasts |
| `/broadcasts/{id}` | GET | Get broadcast details |

---

## Authentication

### API Key Authentication

All requests require an API key in the header:

```http
Authorization: Bearer GGI_API_KEY
Content-Type: application/json
```

### Environment Configuration

```bash
# .env file
GGI_BROADCAST_URL=https://broadcast.ggi.example.com/api/v1
GGI_API_KEY=your_ggi_api_key_here
GGI_WEBHOOK_SECRET=your_webhook_secret_here
```

### Obtaining API Key

1. Register at https://broadcast.ggi.example.com/register
2. Complete organization verification
3. Request API access for peace initiatives
4. Receive API key via email
5. Store securely in environment variables

---

## Publishing Events

### Example: Node.js Implementation

```javascript
const axios = require('axios');

class GGIBroadcastClient {
  constructor(apiKey, baseUrl) {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl;
    this.client = axios.create({
      baseURL: baseUrl,
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      }
    });
  }

  async publishBroadcast(message) {
    try {
      const response = await this.client.post('/broadcast', {
        type: message.type,
        priority: message.priority || 'normal',
        data: message.data,
        tags: message.tags || [],
        metadata: {
          source: 'nexus-api-platform',
          timestamp: new Date().toISOString(),
          ...message.metadata
        }
      });

      return response.data;
    } catch (error) {
      console.error('Failed to publish broadcast:', error);
      throw error;
    }
  }

  async subscribe(eventTypes, webhookUrl) {
    try {
      const response = await this.client.post('/subscribe', {
        eventTypes,
        webhookUrl,
        webhookSecret: process.env.GGI_WEBHOOK_SECRET
      });

      return response.data;
    } catch (error) {
      console.error('Failed to subscribe:', error);
      throw error;
    }
  }

  async listBroadcasts(filters = {}) {
    try {
      const response = await this.client.get('/broadcasts', {
        params: filters
      });

      return response.data;
    } catch (error) {
      console.error('Failed to list broadcasts:', error);
      throw error;
    }
  }
}

// Initialize client
const ggiClient = new GGIBroadcastClient(
  process.env.GGI_API_KEY,
  process.env.GGI_BROADCAST_URL
);

// Publish a broadcast
async function publishPeaceInitiative() {
  const broadcast = await ggiClient.publishBroadcast({
    type: 'peace_initiative',
    priority: 'high',
    data: {
      title: 'Conflict Resolution in Region Alpha',
      description: 'AI-mediated peace talks concluded successfully',
      region: 'middle-east',
      participants: ['Country A', 'Country B'],
      outcome: 'ceasefire_agreement',
      confidence: 0.92
    },
    tags: ['peace', 'conflict-resolution', 'ai-mediation'],
    metadata: {
      initiator: 'nexus-api',
      coordinators: ['agent-001', 'agent-002']
    }
  });

  console.log('Broadcast published:', broadcast);
}

// Subscribe to events
async function subscribeToBroadcasts() {
  const subscription = await ggiClient.subscribe(
    ['peace_initiative', 'humanitarian_alert', 'conflict_warning'],
    'https://your-nexus-api.example.com/webhooks/ggi'
  );

  console.log('Subscribed to GGI broadcasts:', subscription);
}

module.exports = GGIBroadcastClient;
```

### Example: Python Implementation

```python
import requests
import os
from datetime import datetime

class GGIBroadcastClient:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def publish_broadcast(self, message):
        """Publish a broadcast message to GGI network"""
        payload = {
            'type': message['type'],
            'priority': message.get('priority', 'normal'),
            'data': message['data'],
            'tags': message.get('tags', []),
            'metadata': {
                'source': 'nexus-api-platform',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                **message.get('metadata', {})
            }
        }
        
        response = requests.post(
            f'{self.base_url}/broadcast',
            json=payload,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def subscribe(self, event_types, webhook_url):
        """Subscribe to specific event types"""
        payload = {
            'eventTypes': event_types,
            'webhookUrl': webhook_url,
            'webhookSecret': os.environ['GGI_WEBHOOK_SECRET']
        }
        
        response = requests.post(
            f'{self.base_url}/subscribe',
            json=payload,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

# Usage
client = GGIBroadcastClient(
    api_key=os.environ['GGI_API_KEY'],
    base_url=os.environ['GGI_BROADCAST_URL']
)

# Publish broadcast
broadcast = client.publish_broadcast({
    'type': 'peace_initiative',
    'priority': 'high',
    'data': {
        'title': 'AI-Coordinated Humanitarian Relief',
        'region': 'sub-saharan-africa',
        'impact': 'high'
    },
    'tags': ['humanitarian', 'relief', 'ai-coordination']
})

print(f"Broadcast published: {broadcast['broadcastId']}")
```

---

## Webhook Integration

### Setting Up Webhook Endpoint

**Express.js Example:**

```javascript
const express = require('express');
const crypto = require('crypto');

const app = express();
app.use(express.json());

// Webhook endpoint
app.post('/webhooks/ggi', (req, res) => {
  // Verify webhook signature
  const signature = req.headers['x-ggi-signature'];
  const webhookSecret = process.env.GGI_WEBHOOK_SECRET;
  
  const expectedSignature = crypto
    .createHmac('sha256', webhookSecret)
    .update(JSON.stringify(req.body))
    .digest('hex');
  
  if (signature !== expectedSignature) {
    console.error('Invalid webhook signature');
    return res.status(401).send('Unauthorized');
  }

  // Process webhook
  const event = req.body;
  console.log('GGI webhook received:', event.type);

  switch (event.type) {
    case 'peace_initiative':
      handlePeaceInitiative(event.data);
      break;
    case 'humanitarian_alert':
      handleHumanitarianAlert(event.data);
      break;
    case 'conflict_warning':
      handleConflictWarning(event.data);
      break;
    default:
      console.log('Unknown event type:', event.type);
  }

  // Acknowledge receipt
  res.status(200).json({ received: true });
});

// Event handlers
async function handlePeaceInitiative(data) {
  console.log('Peace initiative received:', data);
  
  // Store in database
  await storePeaceInitiative(data);
  
  // Notify relevant agents
  await notifyAgents('peace_initiative', data);
  
  // Trigger analysis
  await analyzeInitiative(data);
}

async function handleHumanitarianAlert(data) {
  console.log('Humanitarian alert:', data);
  
  // High priority - immediate action
  await triggerEmergencyResponse(data);
  
  // Coordinate with local agents
  await coordinateResponse(data);
}

async function handleConflictWarning(data) {
  console.log('Conflict warning:', data);
  
  // Analyze threat level
  const assessment = await assessConflictRisk(data);
  
  // Escalate if necessary
  if (assessment.threatLevel === 'high') {
    await escalateToHumanOperators(data, assessment);
  }
}

app.listen(3000, () => {
  console.log('Webhook server running on port 3000');
});
```

### Registering Webhook

```javascript
// Register webhook with GGI
async function registerWebhook() {
  const response = await ggiClient.client.post('/webhooks', {
    url: 'https://your-nexus-api.example.com/webhooks/ggi',
    secret: process.env.GGI_WEBHOOK_SECRET,
    events: [
      'peace_initiative',
      'humanitarian_alert',
      'conflict_warning'
    ],
    active: true
  });

  console.log('Webhook registered:', response.data);
}
```

### Webhook Security

**1. Signature Verification:**

```javascript
function verifyWebhookSignature(payload, signature, secret) {
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(JSON.stringify(payload))
    .digest('hex');
  
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSignature)
  );
}
```

**2. IP Whitelisting:**

```javascript
const GGI_IP_RANGES = [
  '203.0.113.0/24',
  '198.51.100.0/24'
];

function isGGIIPAddress(ip) {
  // Implement IP range checking
  return GGI_IP_RANGES.some(range => ipInRange(ip, range));
}

app.post('/webhooks/ggi', (req, res) => {
  const clientIP = req.ip;
  
  if (!isGGIIPAddress(clientIP)) {
    return res.status(403).send('Forbidden');
  }
  
  // Process webhook...
});
```

**3. Replay Attack Prevention:**

```javascript
const processedWebhooks = new Set();

app.post('/webhooks/ggi', (req, res) => {
  const webhookId = req.headers['x-ggi-webhook-id'];
  const timestamp = req.headers['x-ggi-timestamp'];
  
  // Check for replay
  if (processedWebhooks.has(webhookId)) {
    return res.status(200).json({ received: true, duplicate: true });
  }
  
  // Check timestamp (reject if older than 5 minutes)
  const age = Date.now() - new Date(timestamp).getTime();
  if (age > 5 * 60 * 1000) {
    return res.status(400).send('Webhook too old');
  }
  
  processedWebhooks.add(webhookId);
  
  // Process webhook...
});
```

---

## Event Types

### Peace Initiative Events

```json
{
  "type": "peace_initiative",
  "priority": "high",
  "data": {
    "initiativeId": "pi-123",
    "title": "Regional Peace Summit",
    "region": "south-asia",
    "participants": ["Country X", "Country Y"],
    "status": "in_progress",
    "startDate": "2025-11-10",
    "mediators": ["UN", "Regional Alliance"]
  }
}
```

### Humanitarian Alert Events

```json
{
  "type": "humanitarian_alert",
  "priority": "critical",
  "data": {
    "alertId": "ha-456",
    "crisis": "natural_disaster",
    "location": {
      "region": "pacific-islands",
      "coordinates": [-15.376706, 167.954712]
    },
    "severity": "critical",
    "affectedPopulation": 50000,
    "requiredResources": ["medical", "shelter", "food"]
  }
}
```

### Conflict Warning Events

```json
{
  "type": "conflict_warning",
  "priority": "high",
  "data": {
    "warningId": "cw-789",
    "region": "eastern-europe",
    "threatLevel": "elevated",
    "indicators": ["troop_movement", "diplomatic_tension"],
    "probability": 0.75,
    "timeframe": "72_hours"
  }
}
```

### Success Story Events

```json
{
  "type": "success_story",
  "priority": "normal",
  "data": {
    "storyId": "ss-321",
    "title": "AI-Mediated Ceasefire Success",
    "region": "middle-east",
    "impact": {
      "livesSaved": 1000,
      "displacementPrevented": 5000,
      "economicBenefit": "$10M"
    },
    "methodology": "ai_analysis_and_mediation"
  }
}
```

---

## Message Formats

### Standard Broadcast Format

```json
{
  "broadcastId": "bc-123456",
  "type": "event_type",
  "priority": "normal|high|critical",
  "timestamp": "2025-11-03T01:54:42.407Z",
  "source": {
    "organization": "Nexus API Platform",
    "agent": "agent-001",
    "verified": true
  },
  "data": {
    /* Event-specific data */
  },
  "tags": ["tag1", "tag2"],
  "metadata": {
    "region": "global",
    "language": "en",
    "version": "1.0"
  }
}
```

### Response Format

```json
{
  "success": true,
  "broadcastId": "bc-123456",
  "status": "published",
  "reach": {
    "subscribers": 150,
    "regions": ["global"],
    "estimatedImpact": "high"
  },
  "publishedAt": "2025-11-03T01:54:42.407Z"
}
```

---

## Error Handling

### Common Errors

| Status Code | Error Code | Description |
|-------------|------------|-------------|
| 400 | INVALID_PAYLOAD | Malformed request body |
| 401 | UNAUTHORIZED | Invalid or missing API key |
| 403 | FORBIDDEN | Insufficient permissions |
| 404 | NOT_FOUND | Resource not found |
| 429 | RATE_LIMIT_EXCEEDED | Too many requests |
| 500 | INTERNAL_ERROR | Server error |

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "INVALID_PAYLOAD",
    "message": "Missing required field: type",
    "details": {
      "field": "type",
      "constraint": "required"
    }
  },
  "timestamp": "2025-11-03T01:54:42.407Z"
}
```

### Retry Logic

```javascript
async function publishWithRetry(message, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const result = await ggiClient.publishBroadcast(message);
      return result;
    } catch (error) {
      if (error.response?.status === 429) {
        // Rate limited - wait and retry
        const retryAfter = error.response.headers['retry-after'] || 60;
        console.log(`Rate limited. Retrying after ${retryAfter}s`);
        await sleep(retryAfter * 1000);
      } else if (error.response?.status >= 500 && attempt < maxRetries) {
        // Server error - exponential backoff
        const delay = Math.pow(2, attempt) * 1000;
        console.log(`Server error. Retrying in ${delay}ms`);
        await sleep(delay);
      } else {
        // Non-retriable error
        throw error;
      }
    }
  }
  throw new Error('Max retries exceeded');
}
```

---

## Best Practices

### 1. Rate Limiting

```javascript
const Bottleneck = require('bottleneck');

// Limit to 100 requests per minute
const limiter = new Bottleneck({
  maxConcurrent: 1,
  minTime: 600 // 600ms between requests = 100/min
});

const publishBroadcast = limiter.wrap(async (message) => {
  return await ggiClient.publishBroadcast(message);
});
```

### 2. Message Deduplication

```javascript
const publishedMessages = new Map();

async function publishUnique(message) {
  const hash = crypto
    .createHash('sha256')
    .update(JSON.stringify(message))
    .digest('hex');
  
  if (publishedMessages.has(hash)) {
    console.log('Duplicate message, skipping');
    return publishedMessages.get(hash);
  }
  
  const result = await ggiClient.publishBroadcast(message);
  publishedMessages.set(hash, result);
  
  // Clean up old entries after 1 hour
  setTimeout(() => publishedMessages.delete(hash), 3600000);
  
  return result;
}
```

### 3. Batch Publishing

```javascript
async function publishBatch(messages) {
  const results = await Promise.allSettled(
    messages.map(msg => publishWithRetry(msg))
  );
  
  const successful = results.filter(r => r.status === 'fulfilled');
  const failed = results.filter(r => r.status === 'rejected');
  
  console.log(`Published ${successful.length}/${messages.length} messages`);
  
  if (failed.length > 0) {
    console.error('Failed messages:', failed.map(f => f.reason));
  }
  
  return { successful, failed };
}
```

### 4. Monitoring & Logging

```javascript
async function publishWithTelemetry(message) {
  const startTime = Date.now();
  
  try {
    const result = await ggiClient.publishBroadcast(message);
    
    // Log success
    logger.info('GGI broadcast published', {
      broadcastId: result.broadcastId,
      type: message.type,
      duration: Date.now() - startTime
    });
    
    // Send telemetry
    await nexusAPI.telemetry.submit({
      metric: 'ggi_broadcast_success',
      value: 1,
      tags: { type: message.type }
    });
    
    return result;
  } catch (error) {
    // Log error
    logger.error('GGI broadcast failed', {
      error: error.message,
      type: message.type,
      duration: Date.now() - startTime
    });
    
    // Send error telemetry
    await nexusAPI.telemetry.submit({
      metric: 'ggi_broadcast_error',
      value: 1,
      tags: { type: message.type, error: error.code }
    });
    
    throw error;
  }
}
```

---

## Testing

### Mock GGI Server for Development

```javascript
const express = require('express');
const app = express();
app.use(express.json());

// Mock broadcast endpoint
app.post('/api/v1/broadcast', (req, res) => {
  console.log('Mock broadcast received:', req.body);
  
  res.json({
    success: true,
    broadcastId: `bc-mock-${Date.now()}`,
    status: 'published',
    publishedAt: new Date().toISOString()
  });
});

// Mock webhook trigger (for testing)
app.post('/api/v1/test/trigger-webhook', async (req, res) => {
  const webhookUrl = req.body.webhookUrl;
  const event = req.body.event;
  
  // Send webhook to your application
  await axios.post(webhookUrl, event, {
    headers: {
      'X-GGI-Signature': 'mock-signature',
      'X-GGI-Webhook-ID': `wh-${Date.now()}`,
      'X-GGI-Timestamp': new Date().toISOString()
    }
  });
  
  res.json({ triggered: true });
});

app.listen(4000, () => {
  console.log('Mock GGI server running on port 4000');
});
```

---

## Support

For GGI Broadcast integration assistance:
- **GGI Documentation**: https://docs.ggi.example.com
- **API Support**: api-support@ggi.example.com
- **Nexus Integration**: support@nexus-api.example.com

---

**GGI Broadcast Integration Guide v1.0.0**  
Last Updated: 2025-11-03
