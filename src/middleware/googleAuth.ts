import { Request, Response, NextFunction } from 'express';
import { OAuth2Client } from 'google-auth-library';
import { config } from '../config';

const client = new OAuth2Client(config.googleClientId);

export interface AuthenticatedRequest extends Request {
  user?: {
    email: string;
    sub: string;
    name?: string;
  };
}

/**
 * Middleware to verify Google ID token from Authorization header
 */
export async function verifyGoogleToken(
  req: AuthenticatedRequest,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      res.status(401).json({ error: 'Missing or invalid Authorization header' });
      return;
    }

    const idToken = authHeader.substring(7); // Remove 'Bearer ' prefix

    // Verify the ID token
    const ticket = await client.verifyIdToken({
      idToken,
      audience: config.googleClientId,
    });

    const payload = ticket.getPayload();
    
    if (!payload) {
      res.status(401).json({ error: 'Invalid token payload' });
      return;
    }

    // Verify issuer
    if (!config.googleIssuers.includes(payload.iss)) {
      res.status(401).json({ error: 'Invalid token issuer' });
      return;
    }

    // Attach user info to request
    req.user = {
      email: payload.email || '',
      sub: payload.sub,
      name: payload.name,
    };

    next();
  } catch (error) {
    console.error('Token verification error:', error);
    res.status(401).json({ error: 'Token verification failed' });
  }
}

/**
 * Middleware to check if user is a Seedbringer
 */
export function requireSeedbringer(
  req: AuthenticatedRequest,
  res: Response,
  next: NextFunction
): void {
  if (!req.user) {
    res.status(401).json({ error: 'Authentication required' });
    return;
  }

  const userEmail = req.user.email.toLowerCase();
  const allowedEmails = config.seedbringerEmails.map(e => e.toLowerCase());

  if (!allowedEmails.includes(userEmail)) {
    res.status(403).json({ 
      error: 'Forbidden: Seedbringer access required',
      user: req.user.email 
    });
    return;
  }

  next();
}

/**
 * Middleware to check if user is a Council member
 */
export function requireCouncil(
  req: AuthenticatedRequest,
  res: Response,
  next: NextFunction
): void {
  if (!req.user) {
    res.status(401).json({ error: 'Authentication required' });
    return;
  }

  const userEmail = req.user.email.toLowerCase();
  const allowedEmails = config.councilEmails.map(e => e.toLowerCase());

  if (!allowedEmails.includes(userEmail)) {
    res.status(403).json({ 
      error: 'Forbidden: Council access required',
      user: req.user.email 
    });
    return;
  }

  next();
}

/**
 * Middleware to check if user is either a Seedbringer or Council member
 */
export function requireSeedbringerOrCouncil(
  req: AuthenticatedRequest,
  res: Response,
  next: NextFunction
): void {
  if (!req.user) {
    res.status(401).json({ error: 'Authentication required' });
    return;
  }

  const userEmail = req.user.email.toLowerCase();
  const seedbringerEmails = config.seedbringerEmails.map(e => e.toLowerCase());
  const councilEmails = config.councilEmails.map(e => e.toLowerCase());

  if (!seedbringerEmails.includes(userEmail) && !councilEmails.includes(userEmail)) {
    res.status(403).json({ 
      error: 'Forbidden: Seedbringer or Council access required',
      user: req.user.email 
    });
    return;
  }

  next();
}
