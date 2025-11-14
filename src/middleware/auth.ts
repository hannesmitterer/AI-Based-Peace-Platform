import { Request, Response, NextFunction } from 'express';

/**
 * ALO-001 Authentication Middleware
 * Implements Google OAuth-based authorization with role-based access control
 */

interface AuthConfig {
  seedbringerEmails: string[];
  councilEmails: string[];
}

// Load configuration from environment variables (lazy-loaded to ensure .env is loaded first)
function getConfig(): AuthConfig {
  return {
    seedbringerEmails: (process.env.SEEDBRINGER_EMAILS || '')
      .split(',')
      .map(e => e.trim())
      .filter(e => e.length > 0),
    councilEmails: (process.env.COUNCIL_EMAILS || '')
      .split(',')
      .map(e => e.trim())
      .filter(e => e.length > 0),
  };
}

/**
 * Extract email from request headers or authorization token
 * In production, this would validate Google OAuth tokens
 * For this scaffold, we'll use a simple header-based approach
 */
function extractUserEmail(req: Request): string | null {
  // Check for email in custom header (scaffold implementation)
  const email = req.headers['x-user-email'] as string;
  
  // In production, implement proper Google OAuth token validation here
  // using Google's OAuth2 client library
  
  return email || null;
}

/**
 * Check if email is in Seedbringer role
 */
function isSeedbringer(email: string): boolean {
  return getConfig().seedbringerEmails.includes(email);
}

/**
 * Check if email is in Council role
 */
function isCouncil(email: string): boolean {
  return getConfig().councilEmails.includes(email);
}

/**
 * Middleware to require Seedbringer role
 */
export function requireSeedbringer(req: Request, res: Response, next: NextFunction): void {
  const email = extractUserEmail(req);
  
  if (!email) {
    res.status(401).json({ error: 'Authentication required' });
    return;
  }

  if (!isSeedbringer(email)) {
    res.status(403).json({ error: 'Seedbringer role required' });
    return;
  }

  next();
}

/**
 * Middleware to require Council role
 */
export function requireCouncil(req: Request, res: Response, next: NextFunction): void {
  const email = extractUserEmail(req);
  
  if (!email) {
    res.status(401).json({ error: 'Authentication required' });
    return;
  }

  if (!isCouncil(email)) {
    res.status(403).json({ error: 'Council role required' });
    return;
  }

  next();
}

/**
 * Middleware to require either Seedbringer or Council role
 */
export function requireAuthorized(req: Request, res: Response, next: NextFunction): void {
  const email = extractUserEmail(req);
  
  if (!email) {
    res.status(401).json({ error: 'Authentication required' });
    return;
  }

  if (!isSeedbringer(email) && !isCouncil(email)) {
    res.status(403).json({ error: 'Authorization required (Seedbringer or Council)' });
    return;
  }

  next();
}
