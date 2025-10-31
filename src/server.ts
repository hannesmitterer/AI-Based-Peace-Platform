import express, { Request, Response, NextFunction } from 'express';
import { createServer } from 'http';
import * as dotenv from 'dotenv';
import { SentimentoWSHub } from './ws/sentimento';
import { SentimentoLiveEvent } from './types/sentimento';

// Load environment variables
dotenv.config();

const app = express();
const server = createServer(app);
const sentimentoHub = new SentimentoWSHub();

// Middleware
app.use(express.json());

// CORS configuration
const corsOrigin = process.env.CORS_ALLOW_ORIGIN || '*';
app.use((req: Request, res: Response, next: NextFunction): void => {
  res.header('Access-Control-Allow-Origin', corsOrigin);
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  if (req.method === 'OPTIONS') {
    res.sendStatus(200);
    return;
  }
  next();
});

// ALO-001: Role allowlists
const SEEDBRINGER_EMAILS = (process.env.SEEDBRINGER_EMAILS || 'hannes.mitterer@gmail.com')
  .split(',')
  .map(e => e.trim());

const COUNCIL_EMAILS = (process.env.COUNCIL_EMAILS || 'dietmar.zuegg@gmail.com, bioarchitettura.rivista@gmail.com, consultant.laquila@gmail.com')
  .split(',')
  .map(e => e.trim());

// Warn if using default allowlists (not configured via env)
if (!process.env.SEEDBRINGER_EMAILS) {
  console.warn('[SECURITY WARNING] Using default SEEDBRINGER_EMAILS. Set environment variable in production.');
}
if (!process.env.COUNCIL_EMAILS) {
  console.warn('[SECURITY WARNING] Using default COUNCIL_EMAILS. Set environment variable in production.');
}

/**
 * ALO-001 Authentication Middleware
 * 
 * SECURITY WARNING: This implementation uses header-based authentication for scaffolding.
 * In production, this MUST be replaced with proper Google OAuth token validation.
 * Current header-based approach is INSECURE and can be easily spoofed.
 * 
 * TODO: Implement full Google OAuth verification as specified in ALO-001
 */
function requireSeedbringer(req: Request, res: Response, next: NextFunction): void {
  // INSECURE: Header-based auth for scaffolding only
  const userEmail = req.headers['x-user-email'] as string;
  
  if (userEmail && SEEDBRINGER_EMAILS.includes(userEmail)) {
    next();
  } else {
    res.status(403).json({ error: 'Forbidden: Seedbringer access required' });
  }
}

function requireCouncil(req: Request, res: Response, next: NextFunction): void {
  // INSECURE: Header-based auth for scaffolding only
  const userEmail = req.headers['x-user-email'] as string;
  
  if (userEmail && COUNCIL_EMAILS.includes(userEmail)) {
    next();
  } else {
    res.status(403).json({ error: 'Forbidden: Council access required' });
  }
}

// Health check endpoint
app.get('/health', (_req: Request, res: Response) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    service: 'sentimento-live'
  });
});

// ALO-001 Protected Routes

/**
 * GET /sfi - Seedbringer access only
 * Seed Foundational Integrity endpoint
 */
app.get('/sfi', requireSeedbringer, (_req: Request, res: Response) => {
  res.json({
    message: 'Seed Foundational Integrity',
    allowedEmails: SEEDBRINGER_EMAILS,
    timestamp: new Date().toISOString()
  });
});

/**
 * GET /mcl/live - Seedbringer access only
 * Mission Critical Live endpoint
 */
app.get('/mcl/live', requireSeedbringer, (_req: Request, res: Response) => {
  res.json({
    message: 'Mission Critical Live',
    hopeRatio: sentimentoHub.getHopeRatio(),
    timestamp: new Date().toISOString()
  });
});

/**
 * POST /allocations - Seedbringer access only
 * Resource allocations endpoint
 */
app.post('/allocations', requireSeedbringer, (req: Request, res: Response) => {
  const { allocations } = req.body;
  
  res.json({
    message: 'Allocations received',
    allocations,
    timestamp: new Date().toISOString()
  });
});

/**
 * GET /kpi/hope-ratio - Council readable
 * Returns the current hope ratio from Seed-003 metrics
 */
app.get('/kpi/hope-ratio', requireCouncil, (_req: Request, res: Response) => {
  const hopeRatio = sentimentoHub.getHopeRatio();
  
  res.json({
    hopeRatio,
    timestamp: new Date().toISOString()
  });
});

/**
 * POST /ingest/sentimento - Unauthenticated scaffold for this PR
 * Accepts Sentimento events and broadcasts them via WebSocket
 */
app.post('/ingest/sentimento', (req: Request, res: Response): void => {
  const { composites } = req.body;
  
  // Validate input
  if (!composites || typeof composites.hope !== 'number' || typeof composites.sorrow !== 'number') {
    res.status(400).json({ 
      error: 'Invalid input: composites.hope and composites.sorrow are required numbers' 
    });
    return;
  }

  // Validate ranges
  if (composites.hope < 0 || composites.hope > 1 || composites.sorrow < 0 || composites.sorrow > 1) {
    res.status(400).json({ 
      error: 'Invalid input: hope and sorrow must be between 0 and 1' 
    });
    return;
  }

  // Create event
  const event: Omit<SentimentoLiveEvent, 'sequence'> = {
    timestamp: new Date().toISOString(),
    composites: {
      hope: composites.hope,
      sorrow: composites.sorrow
    }
  };

  // Broadcast to WebSocket clients
  sentimentoHub.broadcast(event);

  res.json({
    message: 'Event broadcasted',
    timestamp: event.timestamp
  });
});

// Attach WebSocket hub to server
sentimentoHub.attach(server);

// Start server
const PORT = process.env.PORT || 8080;
server.listen(PORT, () => {
  console.log(`[Server] Listening on port ${PORT}`);
  console.log(`[Server] WebSocket endpoint: ws://localhost:${PORT}/api/v2/sentimento/live`);
  console.log('[Server] ALO-001 Allowlists:');
  console.log('  Seedbringer:', SEEDBRINGER_EMAILS);
  console.log('  Council:', COUNCIL_EMAILS);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('[Server] SIGTERM received, shutting down gracefully');
  sentimentoHub.close();
  server.close(() => {
    console.log('[Server] Server closed');
    process.exit(0);
  });
});
