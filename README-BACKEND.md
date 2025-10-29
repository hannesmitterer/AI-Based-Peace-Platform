# Sentimento Live WebSocket API

This Node.js/TypeScript backend implements the Sentimento Live WebSocket API with Seed-003 metrics integration and ALO-001 authentication protections.

## Features

- **WebSocket Broadcasting**: Real-time sentiment data broadcast at `/api/v2/sentimento/live`
- **Seed-003 KPI Metrics**: Tracks hope/sorrow ratio with sample history
- **ALO-001 Authorization**: Google OAuth-based role protection (Council/Seedbringer)
- **Backpressure Control**: WebSocket send throttling based on buffer size
- **RESTful Endpoints**: System health, metrics, and data ingestion

## Quick Start

### Installation

```bash
npm install
```

### Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Key environment variables:
- `PORT`: Server port (default: 8080)
- `COUNCIL_EMAILS`: Comma-separated list of Council member emails
- `SEEDBRINGER_EMAILS`: Comma-separated list of Seedbringer emails
- `SENTIMENTO_BROADCAST_HZ`: Broadcast rate limit (default: 10 Hz)
- `SENTIMENTO_BUFFER_MAX_KB`: Max WebSocket buffer size in KB (default: 512)

### Build

```bash
npm run build
```

### Run

```bash
npm start
```

For development with auto-reload:

```bash
npm run dev
```

## API Endpoints

### Public Endpoints

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-29T22:00:00.000Z",
  "uptime": 123.456
}
```

#### GET /sfi
System Functionality Index.

**Response:**
```json
{
  "status": "operational",
  "version": "1.0.0",
  "timestamp": "2025-10-29T22:00:00.000Z",
  "components": {
    "websocket": "active",
    "metrics": "operational"
  }
}
```

#### GET /mcl/live
Mission Control Live status.

**Response:**
```json
{
  "status": "live",
  "timestamp": "2025-10-29T22:00:00.000Z",
  "websocketClients": 5,
  "metrics": {
    "hopeRatio": 0.75,
    "sampleCount": 100,
    "avgHope": 0.6,
    "avgSorrow": 0.2
  }
}
```

#### POST /allocations
Resource allocation endpoint (scaffold).

**Request:**
```json
{
  "resource": "water",
  "amount": 500
}
```

**Response:**
```json
{
  "success": true,
  "message": "Allocation recorded",
  "timestamp": "2025-10-29T22:00:00.000Z",
  "allocation": { "resource": "water", "amount": 500 }
}
```

#### POST /ingest/sentimento
Ingest sentiment data and broadcast to WebSocket clients.

**Request:**
```json
{
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

**Response:**
```json
{
  "success": true,
  "message": "Event ingested and broadcast",
  "clientCount": 5,
  "timestamp": "2025-10-29T22:00:00.000Z"
}
```

### Protected Endpoints

#### GET /kpi/hope-ratio
Get current hope ratio metric.

**Requires**: Council role (via `x-user-email` header)

**Response:**
```json
{
  "hopeRatio": 0.75,
  "sampleCount": 100,
  "avgHope": 0.6,
  "avgSorrow": 0.2,
  "timestamp": "2025-10-29T22:00:00.000Z"
}
```

### WebSocket Endpoint

#### ws://[host]:[port]/api/v2/sentimento/live

Connect to receive real-time sentiment broadcasts.

**Welcome Message:**
```json
{
  "type": "welcome",
  "message": "Connected to Sentimento Live feed",
  "timestamp": "2025-10-29T22:00:00.000Z"
}
```

**Broadcast Event:**
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

## Architecture

### Components

- **src/server.ts**: Main Express server with HTTP/WebSocket setup
- **src/ws/sentimento.ts**: WebSocket hub for client management and broadcasting
- **src/types/sentimento.ts**: TypeScript type definitions
- **src/metrics/seed003.ts**: Seed-003 KPI tracking module
- **src/middleware/auth.ts**: ALO-001 authentication middleware

### Key Features

1. **Single HTTP Server**: Express app attached to single HTTP server
2. **WebSocket Upgrade**: Server handles upgrade requests for `/api/v2/sentimento/live`
3. **Backpressure Control**: Drops sends when client buffer exceeds `SENTIMENTO_BUFFER_MAX_KB`
4. **Metrics Integration**: Each broadcast feeds Seed-003 via `pushSample(sorrow, hope)`
5. **Role-Based Access**: Council protection for KPI endpoints

## Testing

Run the integration test:

```bash
# Start server
npm start

# In another terminal, run test
curl http://localhost:8080/health
```

WebSocket test example:

```javascript
const WebSocket = require('ws');
const ws = new WebSocket('ws://localhost:8080/api/v2/sentimento/live');

ws.on('message', (data) => {
  console.log('Received:', data.toString());
});
```

## Security Notes

- Current implementation uses simple header-based auth (`x-user-email`) for scaffolding
- **Production**: Implement proper Google OAuth token validation in `src/middleware/auth.ts`
- POST /ingest/sentimento is currently unauthenticated (can be gated in future PR)
- All Council/Seedbringer emails must be configured in environment variables
- **CORS Configuration**: The default CORS setting (`*`) allows any origin for development
  - **Production**: Set `CORS_ALLOW_ORIGIN` to specific domain(s) in production environment
  - Example: `CORS_ALLOW_ORIGIN=https://hannesmitterer.github.io`
  - Multiple origins can be handled with custom CORS middleware logic if needed

## Development

### TypeScript Build

The project uses TypeScript with strict mode enabled. Build outputs to `dist/`:

```bash
npm run build
```

### File Structure

```
src/
├── server.ts              # Main server
├── types/
│   └── sentimento.ts      # Type definitions
├── ws/
│   └── sentimento.ts      # WebSocket hub
├── metrics/
│   └── seed003.ts         # KPI tracking
└── middleware/
    └── auth.ts            # Authentication
```

## License

ISC
