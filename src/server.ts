/**
 * Seed-003: Hope Transduction Layer (ARSP-001)
 * Express server with ALO-001 authentication and Seed-003 endpoints
 */

import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { OAuth2Client } from 'google-auth-library';
import { pushSample, getRollingKpi } from './kpi/hope';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 8080;

// Google OAuth client
const client = new OAuth2Client(process.env.GOOGLE_CLIENT_ID);

// Extend Express Request interface
interface AuthenticatedRequest extends Request {
  user?: {
    email: string;
    role: string;
  };
}

// Middleware
app.use(cors({ origin: process.env.CORS_ALLOW_ORIGIN || '*' }));
app.use(express.json());

// Static files (serve public directory)
app.use(express.static('public'));

// ALO-001: Role allowlists
const SEEDBRINGER_EMAILS = (process.env.SEEDBRINGER_EMAILS || '')
  .split(',')
  .map(e => e.trim())
  .filter(e => e);

const COUNCIL_EMAILS = (process.env.COUNCIL_EMAILS || '')
  .split(',')
  .map(e => e.trim())
  .filter(e => e);

/**
 * ALO-001: Verify Google ID token and check role
 */
async function verifyToken(
  token: string,
  requiredRole?: 'seedbringer' | 'council'
): Promise<{ email: string; role: string }> {
  try {
    const ticket = await client.verifyIdToken({
      idToken: token,
      audience: process.env.GOOGLE_CLIENT_ID,
    });
    const payload = ticket.getPayload();
    
    if (!payload || !payload.email) {
      throw new Error('Invalid token payload');
    }

    const email = payload.email;
    let role = 'none';

    if (SEEDBRINGER_EMAILS.includes(email)) {
      role = 'seedbringer';
    } else if (COUNCIL_EMAILS.includes(email)) {
      role = 'council';
    }

    // Check required role
    if (requiredRole && role !== requiredRole && role !== 'seedbringer') {
      throw new Error(`Required role: ${requiredRole}, user has: ${role}`);
    }

    return { email, role };
  } catch (error) {
    throw new Error(`Token verification failed: ${(error as Error).message}`);
  }
}

/**
 * Middleware: Require Council role (ALO-001)
 */
async function requireCouncil(req: Request, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing or invalid Authorization header' });
  }

  const token = authHeader.substring(7);

  try {
    const { email, role } = await verifyToken(token, 'council');
    (req as AuthenticatedRequest).user = { email, role };
    next();
  } catch (error) {
    res.status(403).json({ error: (error as Error).message });
  }
}

// ============================================
// ALO-001 Endpoints (existing)
// ============================================

/**
 * GET /sfi - System Fairness Indicator (requires Council)
 */
app.get('/sfi', requireCouncil, (req: Request, res: Response) => {
  res.json({
    sfi: 0.72,
    message: 'Placeholder: System Fairness Indicator',
    user: (req as AuthenticatedRequest).user,
  });
});

/**
 * GET /mcl/live - Mission Control Live (requires Council)
 */
app.get('/mcl/live', requireCouncil, (req: Request, res: Response) => {
  res.json({
    status: 'operational',
    message: 'Placeholder: Mission Control Live',
    user: (req as AuthenticatedRequest).user,
  });
});

/**
 * POST /allocations - Resource allocations (requires Council)
 */
app.post('/allocations', requireCouncil, (req: Request, res: Response) => {
  res.json({
    success: true,
    message: 'Placeholder: Allocations endpoint',
    data: req.body,
    user: (req as AuthenticatedRequest).user,
  });
});

// ============================================
// Seed-003 Endpoints
// ============================================

/**
 * GET /kpi/hope-ratio - Get rolling hope KPI (requires Council)
 */
app.get('/kpi/hope-ratio', requireCouncil, (req: Request, res: Response) => {
  try {
    const kpi = getRollingKpi();
    res.json({ kpi });
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

/**
 * POST /ingest/sentimento - Push sorrow/hope samples (unauthenticated for this PR)
 */
app.post('/ingest/sentimento', (req: Request, res: Response) => {
  try {
    const { sorrow, hope } = req.body;

    // Validate inputs
    if (typeof sorrow !== 'number' || typeof hope !== 'number') {
      return res.status(400).json({ error: 'sorrow and hope must be numbers' });
    }

    if (sorrow < 0 || sorrow > 1 || hope < 0 || hope > 1) {
      return res.status(400).json({ 
        error: 'sorrow and hope must be in range [0,1]' 
      });
    }

    pushSample(sorrow, hope);

    res.json({ 
      success: true, 
      message: 'Sample ingested',
      sample: { sorrow, hope }
    });
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

// ============================================
// Health check
// ============================================

app.get('/health', (req: Request, res: Response) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// Start server
app.listen(PORT, () => {
  console.log(`🌍 Peace Platform API listening on port ${PORT}`);
  console.log(`🔒 ALO-001 authentication enabled`);
  console.log(`💚 Seed-003 Hope Transduction Layer active`);
});
