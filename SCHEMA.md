# Sentimento Live WebSocket API - JSON Schema Documentation

## WebSocket Endpoint

**URL**: `wss://<host>:<port>/api/v2/sentimento/live`

## Message Schemas

### 1. Welcome Message (Server → Client)

Sent immediately upon successful WebSocket connection.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["type", "message", "timestamp"],
  "properties": {
    "type": {
      "type": "string",
      "const": "welcome"
    },
    "message": {
      "type": "string",
      "description": "Welcome message for the client"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp"
    }
  }
}
```

**Example**:
```json
{
  "type": "welcome",
  "message": "Connected to Sentimento Live feed",
  "timestamp": "2025-10-29T22:00:00.000Z"
}
```

### 2. Sentimento Live Event (Server → Client)

Broadcast to all connected clients when sentiment data is ingested.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["timestamp", "composites"],
  "properties": {
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp when the event was generated"
    },
    "composites": {
      "type": "object",
      "required": ["hope", "sorrow"],
      "properties": {
        "hope": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "Hope metric value (0.0 to 1.0)"
        },
        "sorrow": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "Sorrow metric value (0.0 to 1.0)"
        }
      }
    },
    "metadata": {
      "type": "object",
      "description": "Optional metadata about the event",
      "properties": {
        "source": {
          "type": "string",
          "description": "Source identifier for the sentiment data"
        },
        "region": {
          "type": "string",
          "description": "Geographic region if applicable"
        }
      },
      "additionalProperties": true
    }
  }
}
```

**Example**:
```json
{
  "timestamp": "2025-10-29T22:00:00.000Z",
  "composites": {
    "hope": 0.75,
    "sorrow": 0.25
  },
  "metadata": {
    "source": "analyzer-1",
    "region": "EU"
  }
}
```

## REST API Schemas

### POST /ingest/sentimento

Request body schema for ingesting sentiment data.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["composites"],
  "properties": {
    "composites": {
      "type": "object",
      "required": ["hope", "sorrow"],
      "properties": {
        "hope": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "Hope metric value (0.0 to 1.0)"
        },
        "sorrow": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "Sorrow metric value (0.0 to 1.0)"
        }
      }
    },
    "metadata": {
      "type": "object",
      "description": "Optional metadata about the sentiment data",
      "properties": {
        "source": {
          "type": "string",
          "description": "Source identifier for the sentiment data"
        },
        "region": {
          "type": "string",
          "description": "Geographic region if applicable"
        }
      },
      "additionalProperties": true
    }
  }
}
```

**Request Example**:
```bash
curl -X POST http://localhost:8080/ingest/sentimento \
  -H "Content-Type: application/json" \
  -d '{
    "composites": {
      "hope": 0.75,
      "sorrow": 0.25
    },
    "metadata": {
      "source": "analyzer-1",
      "region": "EU"
    }
  }'
```

**Response Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["success", "message", "clientCount", "timestamp"],
  "properties": {
    "success": {
      "type": "boolean"
    },
    "message": {
      "type": "string"
    },
    "clientCount": {
      "type": "integer",
      "description": "Number of WebSocket clients that received the broadcast"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

**Response Example**:
```json
{
  "success": true,
  "message": "Event ingested and broadcast",
  "clientCount": 5,
  "timestamp": "2025-10-29T22:00:00.000Z"
}
```

## Error Schemas

### Validation Error (400)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["error", "message"],
  "properties": {
    "error": {
      "type": "string"
    },
    "message": {
      "type": "string",
      "description": "Detailed error message"
    }
  }
}
```

**Example**:
```json
{
  "error": "Invalid payload",
  "message": "composites.hope and composites.sorrow are required and must be numbers"
}
```

### Authentication Error (401)

```json
{
  "error": "Authentication required"
}
```

### Authorization Error (403)

```json
{
  "error": "Council role required"
}
```

## TypeScript Type Definitions

The canonical types are defined in `src/types/sentimento.ts`:

```typescript
interface SentimentoLiveEvent {
  timestamp: string;
  composites: {
    hope: number;
    sorrow: number;
  };
  metadata?: {
    source?: string;
    region?: string;
    [key: string]: any;
  };
}

interface SentimentoIngestPayload {
  composites: {
    hope: number;
    sorrow: number;
  };
  metadata?: {
    source?: string;
    region?: string;
    [key: string]: any;
  };
}
```

## Integration with Seed-003 Metrics

Every broadcast event automatically feeds into the Seed-003 KPI system via:

```typescript
seed003Metrics.pushSample(sorrow, hope);
```

The hope ratio can be retrieved via the protected endpoint:

```bash
curl http://localhost:8080/kpi/hope-ratio \
  -H "x-user-email: <council-member-email>"
```

**Response**:
```json
{
  "hopeRatio": 0.75,
  "sampleCount": 100,
  "avgHope": 0.6,
  "avgSorrow": 0.2,
  "timestamp": "2025-10-29T22:00:00.000Z"
}
```

Where `hopeRatio = avgHope / (avgHope + avgSorrow)`

## WebSocket Client Example

### JavaScript/Node.js

```javascript
const WebSocket = require('ws');

const ws = new WebSocket('ws://localhost:8080/api/v2/sentimento/live');

ws.on('open', function open() {
  console.log('Connected to Sentimento Live');
});

ws.on('message', function incoming(data) {
  const event = JSON.parse(data);
  
  if (event.type === 'welcome') {
    console.log('Welcome:', event.message);
  } else if (event.composites) {
    console.log('Sentiment Update:', {
      hope: event.composites.hope,
      sorrow: event.composites.sorrow,
      timestamp: event.timestamp
    });
  }
});

ws.on('error', function error(err) {
  console.error('WebSocket error:', err);
});

ws.on('close', function close() {
  console.log('Disconnected from Sentimento Live');
});
```

### Python

```python
import websocket
import json

def on_message(ws, message):
    event = json.loads(message)
    
    if event.get('type') == 'welcome':
        print(f"Welcome: {event['message']}")
    elif 'composites' in event:
        print(f"Sentiment Update: hope={event['composites']['hope']}, "
              f"sorrow={event['composites']['sorrow']}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Disconnected")

def on_open(ws):
    print("Connected to Sentimento Live")

ws = websocket.WebSocketApp(
    "ws://localhost:8080/api/v2/sentimento/live",
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

ws.run_forever()
```

## Backpressure Handling

The WebSocket hub implements backpressure control:

- Maximum buffer size: `SENTIMENTO_BUFFER_MAX_KB` (default: 512 KB)
- When a client's buffer exceeds this limit, sends are dropped
- This prevents slow clients from blocking the entire system
- Clients should consume messages promptly to avoid drops

## Rate Limiting

The `SENTIMENTO_BROADCAST_HZ` environment variable is reserved for future rate limiting implementation. Currently, broadcasts are event-driven (triggered by POST /ingest/sentimento), not time-based.
