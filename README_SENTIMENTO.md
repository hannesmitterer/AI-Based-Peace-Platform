# Sentimento Live WebSocket API

This implementation provides a WebSocket-based real-time streaming API for Sentimento emotional composites, integrated with Seed-003 metrics tracking and ALO-001 access control.

## Features

- **WebSocket Streaming**: Real-time broadcast of Sentimento events on `/api/v2/sentimento/live`
- **Seed-003 Integration**: Automatic tracking of hope/sorrow metrics
- **ALO-001 Protection**: Role-based access control for sensitive endpoints
- **Backpressure Handling**: Intelligent message dropping when clients can't keep up
- **TypeScript**: Fully typed with strict mode enabled

## Quick Start

### Installation

```bash
npm install
```

### Build

```bash
npm run build
```

### Run

```bash
npm start
```

The server will start on port 8080 (or PORT from environment).

## Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Server Configuration
PORT=8080
CORS_ALLOW_ORIGIN=*

# ALO-001 Allowlists
SEEDBRINGER_EMAILS=hannes.mitterer@gmail.com
COUNCIL_EMAILS=dietmar.zuegg@gmail.com, bioarchitettura.rivista@gmail.com, consultant.laquila@gmail.com

# Sentimento Configuration
SENTIMENTO_BROADCAST_HZ=10
SENTIMENTO_BUFFER_MAX_KB=512
```

## API Endpoints

### Public Endpoints

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-10-31T00:00:00.000Z",
  "service": "sentimento-live"
}
```

#### `POST /ingest/sentimento`
Ingest and broadcast Sentimento events (unauthenticated in this PR).

**Request:**
```json
{
  "composites": {
    "hope": 0.7,
    "sorrow": 0.3
  }
}
```

**Response:**
```json
{
  "message": "Event broadcasted",
  "timestamp": "2025-10-31T00:00:00.000Z"
}
```

### ALO-001 Protected Endpoints (Seedbringer Only)

Require `x-user-email` header with allowed Seedbringer email.

#### `GET /sfi`
Seed Foundational Integrity endpoint.

#### `GET /mcl/live`
Mission Critical Live endpoint with current hope ratio.

#### `POST /allocations`
Resource allocations endpoint.

### Council Endpoints

Require `x-user-email` header with allowed Council email.

#### `GET /kpi/hope-ratio`
Returns the current hope ratio from Seed-003 metrics.

**Response:**
```json
{
  "hopeRatio": 0.7,
  "timestamp": "2025-10-31T00:00:00.000Z"
}
```

## WebSocket

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8080/api/v2/sentimento/live');

ws.on('message', (data) => {
  const event = JSON.parse(data);
  console.log(event);
});
```

### Message Format

```json
{
  "timestamp": "2025-10-31T00:00:00.000Z",
  "composites": {
    "hope": 0.7,
    "sorrow": 0.3
  },
  "sequence": 0
}
```

## Testing

### Test Health Endpoint
```bash
curl http://localhost:8080/health
```

### Test Event Ingestion
```bash
curl -X POST http://localhost:8080/ingest/sentimento \
  -H "Content-Type: application/json" \
  -d '{"composites":{"hope":0.7,"sorrow":0.3}}'
```

### Test Hope Ratio
```bash
curl http://localhost:8080/kpi/hope-ratio \
  -H "x-user-email: dietmar.zuegg@gmail.com"
```

### Test WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8080/api/v2/sentimento/live');
ws.on('message', (data) => console.log(JSON.parse(data)));
```

## Security Notes

⚠️ **IMPORTANT**: The current implementation uses header-based authentication (`x-user-email`) for scaffolding purposes only. This is **INSECURE** and must be replaced with proper Google OAuth token validation before production deployment.

The following security measures are in place:
- ✅ TypeScript strict mode
- ✅ Input validation for composites
- ✅ Backpressure handling
- ✅ No known vulnerabilities (CodeQL + GitHub Advisory Database)
- ⚠️ Authentication is scaffold only

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────┐     ┌──────────────────┐
│   Express   │────▶│ SentimentoWSHub  │
│   Server    │     └────────┬─────────┘
└─────────────┘              │
       │                     │ WebSocket
       │                     ▼
       │              ┌──────────────┐
       │              │   Clients    │
       │              └──────────────┘
       ▼
┌─────────────┐
│ Seed-003    │
│  Metrics    │
└─────────────┘
```

## License

See repository LICENSE file.
