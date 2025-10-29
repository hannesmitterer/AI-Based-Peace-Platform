import express from 'express';
import cors from 'cors';
import { config } from './config';
import { 
  verifyGoogleToken, 
  requireSeedbringer, 
  requireCouncil,
  AuthenticatedRequest 
} from './middleware/googleAuth';

const app = express();

// Middleware
app.use(cors({ origin: config.corsAllowOrigin }));
app.use(express.json());

// Health check endpoint (public)
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// GET /sfi - Requires Council access
app.get('/sfi', verifyGoogleToken, requireCouncil, (req: AuthenticatedRequest, res) => {
  res.json({
    message: 'Systemic Fairness Index data',
    user: req.user?.email,
    data: {
      index: 'SFI',
      description: 'Systemic Fairness Monitor endpoint',
      access: 'Council',
      // Add actual SFI data here
      metrics: {
        giniCoefficient: 0.42,
        accessToOpportunity: 'moderate',
        lastUpdate: new Date().toISOString()
      }
    }
  });
});

// GET /mcl/live - Requires Council access
app.get('/mcl/live', verifyGoogleToken, requireCouncil, (req: AuthenticatedRequest, res) => {
  res.json({
    message: 'Mission-Critical Live data',
    user: req.user?.email,
    data: {
      endpoint: '/mcl/live',
      description: 'Mission-Critical Live endpoint',
      access: 'Council',
      // Add actual live data here
      status: {
        systemHealth: 'operational',
        activeMonitors: 4,
        lastUpdate: new Date().toISOString()
      }
    }
  });
});

// POST /allocations - Requires Seedbringer access
app.post('/allocations', verifyGoogleToken, requireSeedbringer, (req: AuthenticatedRequest, res) => {
  const allocationData = req.body;
  
  // Validate allocation data
  if (!allocationData || Object.keys(allocationData).length === 0) {
    res.status(400).json({ error: 'Allocation data required' });
    return;
  }

  res.json({
    message: 'Allocation request received',
    user: req.user?.email,
    allocation: allocationData,
    status: 'pending',
    timestamp: new Date().toISOString()
  });
});

// Error handling middleware
app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('Error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
const PORT = parseInt(config.port, 10);
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`CORS allowed origin: ${config.corsAllowOrigin}`);
  console.log(`Google Client ID configured: ${config.googleClientId ? 'Yes' : 'No'}`);
  console.log(`Seedbringer emails configured: ${config.seedbringerEmails.length}`);
  console.log(`Council emails configured: ${config.councilEmails.length}`);
});

export default app;
