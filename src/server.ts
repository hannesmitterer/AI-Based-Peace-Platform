import express from 'express';
import cors from 'cors';
import rateLimit from 'express-rate-limit';
import config from './config';
import { requireAuth, Role, AuthenticatedRequest } from './middleware/googleAuth';

const app = express();

// Rate limiting configuration
const limiter = rateLimit({
  windowMs: config.rateLimitWindowMs,
  max: config.rateLimitMaxRequests,
  standardHeaders: true, // Return rate limit info in the `RateLimit-*` headers
  legacyHeaders: false, // Disable the `X-RateLimit-*` headers
  message: 'Too many requests from this IP, please try again later.',
});

// Apply rate limiting to all requests
app.use(limiter);

// Middleware
// NOTE: CORS origin is configurable via environment variable
// For production, set CORS_ALLOW_ORIGIN to your specific domain instead of '*'
// See BACKEND_SETUP.md for security recommendations
app.use(cors({
  origin: config.corsAllowOrigin,
}));
app.use(express.json());

// Health check endpoint (public)
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

/**
 * GET /sfi - Systemic Fairness Index
 * Accessible by Council or Seedbringer (read-only)
 */
app.get('/sfi', requireAuth([Role.COUNCIL, Role.SEEDBRINGER]), (req: AuthenticatedRequest, res) => {
  const sfiData = {
    index: 'Systemic Fairness Index',
    description: 'Global inequality and access to opportunity metrics',
    currentValue: 7.2,
    status: 'Persistent Disparity',
    lastUpdated: new Date().toISOString(),
    requestedBy: {
      email: req.user?.email,
      role: req.user?.role,
    },
  };
  res.json(sfiData);
});

/**
 * GET /mcl/live - Mission Critical Live data
 * Accessible by Council or Seedbringer (read-only)
 */
app.get('/mcl/live', requireAuth([Role.COUNCIL, Role.SEEDBRINGER]), (req: AuthenticatedRequest, res) => {
  const mclData = {
    endpoint: 'Mission Critical Live',
    description: 'Real-time monitoring of critical system parameters',
    metrics: {
      globalScarcityIndex: 6.8,
      regionalStability: 'Elevated Risk',
      dasProtocolImpact: 'Initial Growth Phase',
    },
    lastUpdated: new Date().toISOString(),
    requestedBy: {
      email: req.user?.email,
      role: req.user?.role,
    },
  };
  res.json(mclData);
});

/**
 * POST /allocations - Create new resource allocation
 * Accessible by Seedbringer only (write access)
 */
app.post('/allocations', requireAuth([Role.SEEDBRINGER]), (req: AuthenticatedRequest, res) => {
  const { amount, target, purpose } = req.body;

  // Validate input
  if (!amount || !target || !purpose) {
    return res.status(400).json({ 
      error: 'Missing required fields',
      required: ['amount', 'target', 'purpose'],
    });
  }

  // In a real implementation, this would persist to a database
  const allocation = {
    id: `alloc-${Date.now()}`,
    amount,
    target,
    purpose,
    status: 'pending',
    createdBy: req.user?.email,
    createdAt: new Date().toISOString(),
  };

  console.log('New allocation created:', allocation);

  res.status(201).json({
    message: 'Allocation created successfully',
    allocation,
  });
});

// Error handling middleware
app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('Unhandled error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Endpoint not found' });
});

// Start server
const PORT = config.port;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`CORS origin: ${config.corsAllowOrigin}`);
  console.log(`Google Client ID: ${config.googleClientId ? 'Configured' : 'NOT CONFIGURED'}`);
  console.log(`Seedbringer emails: ${config.seedbringerEmails.join(', ')}`);
  console.log(`Council emails: ${config.councilEmails.join(', ')}`);
});

export default app;
