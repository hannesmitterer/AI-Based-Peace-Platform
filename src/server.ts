import express, { Request, Response } from 'express';
import cors from 'cors';
import { createServer } from 'http';
import dotenv from 'dotenv';
import { SentimentoWSHub } from './ws/sentimento';
import { SentimentoIngestPayload, SentimentoLiveEvent } from './types/sentimento';
import { requireCouncil } from './middleware/auth';
import { seed003Metrics } from './metrics/seed003';

// Load environment variables
dotenv.config();

// Configuration
const config = {
  port: parseInt(process.env.PORT || '8080', 10),
  corsOrigin: process.env.CORS_ALLOW_ORIGIN || '*',
  sentimentoBroadcastHz: parseInt(process.env.SENTIMENTO_BROADCAST_HZ || '10', 10),
};

// Create Express app
const app = express();

// Middleware
app.use(cors({ origin: config.corsOrigin }));
app.use(express.json());

// Request logging middleware
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} ${req.method} ${req.path}`);
  next();
});

// Create HTTP server from Express app
const server = createServer(app);

// Initialize WebSocket Hub
const sentimentoHub = new SentimentoWSHub(
  server,
  parseInt(process.env.SENTIMENTO_BUFFER_MAX_KB || '512', 10)
);

// ============================================================================
// ALO-001 Protected Routes (scaffolded - require auth in production)
// ============================================================================

/**
 * GET /sfi
 * System Functionality Index endpoint
 */
app.get('/sfi', (req: Request, res: Response) => {
  res.json({
    status: 'operational',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
    components: {
      websocket: sentimentoHub.getClientCount() > 0 ? 'active' : 'idle',
      metrics: 'operational',
    },
  });
});

/**
 * GET /mcl/live
 * Mission Control Live endpoint
 */
app.get('/mcl/live', (req: Request, res: Response) => {
  const stats = seed003Metrics.getStats();
  
  res.json({
    status: 'live',
    timestamp: new Date().toISOString(),
    websocketClients: sentimentoHub.getClientCount(),
    metrics: stats,
  });
});

/**
 * POST /allocations
 * Resource allocations endpoint (scaffold)
 */
app.post('/allocations', (req: Request, res: Response) => {
  // Scaffold implementation
  const allocation = req.body;
  
  res.json({
    success: true,
    message: 'Allocation recorded',
    timestamp: new Date().toISOString(),
    allocation,
  });
});

// ============================================================================
// Health Check
// ============================================================================

/**
 * GET /health
 * Health check endpoint
 */
app.get('/health', (req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
  });
});

// ============================================================================
// Seed-003 KPI Endpoint (Council-protected)
// ============================================================================

/**
 * GET /kpi/hope-ratio
 * Get current hope ratio metric (requires Council authorization)
 */
app.get('/kpi/hope-ratio', requireCouncil, (req: Request, res: Response) => {
  const stats = seed003Metrics.getStats();
  
  res.json({
    hopeRatio: stats.hopeRatio,
    sampleCount: stats.sampleCount,
    avgHope: stats.avgHope,
    avgSorrow: stats.avgSorrow,
    timestamp: new Date().toISOString(),
  });
});

// ============================================================================
// Sentimento Ingest Endpoint
// ============================================================================

/**
 * POST /ingest/sentimento
 * Ingest sentiment data and broadcast to WebSocket clients
 * Currently unauthenticated (can be gated in future PR)
 */
app.post('/ingest/sentimento', (req: Request, res: Response) => {
  try {
    const payload: SentimentoIngestPayload = req.body;

    // Validate payload
    if (!payload.composites || 
        typeof payload.composites.hope !== 'number' ||
        typeof payload.composites.sorrow !== 'number') {
      res.status(400).json({
        error: 'Invalid payload',
        message: 'composites.hope and composites.sorrow are required and must be numbers',
      });
      return;
    }

    // Validate ranges
    if (payload.composites.hope < 0 || payload.composites.hope > 1 ||
        payload.composites.sorrow < 0 || payload.composites.sorrow > 1) {
      res.status(400).json({
        error: 'Invalid values',
        message: 'hope and sorrow must be between 0 and 1',
      });
      return;
    }

    // Create event
    const event: SentimentoLiveEvent = {
      timestamp: new Date().toISOString(),
      composites: {
        hope: payload.composites.hope,
        sorrow: payload.composites.sorrow,
      },
      metadata: payload.metadata,
    };

    // Broadcast via WebSocket Hub
    sentimentoHub.broadcast(event);

    res.json({
      success: true,
      message: 'Event ingested and broadcast',
      clientCount: sentimentoHub.getClientCount(),
      timestamp: event.timestamp,
    });
  } catch (error) {
    console.error('Error processing ingest:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

// ============================================================================
// Error Handling
// ============================================================================

// 404 handler
app.use((req: Request, res: Response) => {
  res.status(404).json({
    error: 'Not found',
    path: req.path,
  });
});

// Global error handler
app.use((err: Error, req: Request, res: Response, next: any) => {
  console.error('Unhandled error:', err);
  res.status(500).json({
    error: 'Internal server error',
    message: err.message,
  });
});

// ============================================================================
// Server Startup
// ============================================================================

server.listen(config.port, () => {
  console.log('='.repeat(60));
  console.log('AI-Based Peace Platform - Sentimento Live API');
  console.log('='.repeat(60));
  console.log(`Server running on port ${config.port}`);
  console.log(`WebSocket endpoint: ws://localhost:${config.port}/api/v2/sentimento/live`);
  console.log(`CORS origin: ${config.corsOrigin}`);
  console.log(`Broadcast rate: ${config.sentimentoBroadcastHz} Hz`);
  console.log('='.repeat(60));
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully...');
  sentimentoHub.shutdown();
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('SIGINT received, shutting down gracefully...');
  sentimentoHub.shutdown();
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});
