import { Request, Response, NextFunction } from 'express';
import { OAuth2Client } from 'google-auth-library';
import config from '../config';

const client = new OAuth2Client(config.googleClientId);

export enum Role {
  SEEDBRINGER = 'seedbringer',
  COUNCIL = 'council',
}

export interface AuthenticatedRequest extends Request {
  user?: {
    email: string;
    role: Role;
    name?: string;
  };
}

/**
 * Verify Google ID token and attach user information to request
 */
async function verifyGoogleToken(token: string): Promise<{ email: string; name?: string } | null> {
  try {
    const ticket = await client.verifyIdToken({
      idToken: token,
      audience: config.googleClientId,
    });
    const payload = ticket.getPayload();
    
    if (!payload || !payload.email) {
      return null;
    }

    // Verify issuer
    if (payload.iss && !config.googleIssuers.includes(payload.iss)) {
      console.error(`Invalid issuer: ${payload.iss}`);
      return null;
    }

    return {
      email: payload.email,
      name: payload.name,
    };
  } catch (error) {
    console.error('Token verification error:', error);
    return null;
  }
}

/**
 * Determine user role based on email
 */
function getUserRole(email: string): Role | null {
  if (config.seedbringerEmails.includes(email)) {
    return Role.SEEDBRINGER;
  }
  if (config.councilEmails.includes(email)) {
    return Role.COUNCIL;
  }
  return null;
}

/**
 * Middleware to authenticate Google ID token and enforce role-based access
 */
export function requireAuth(allowedRoles: Role[]) {
  return async (req: AuthenticatedRequest, res: Response, next: NextFunction): Promise<void> => {
    try {
      // Extract token from Authorization header
      const authHeader = req.headers.authorization;
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        res.status(401).json({ error: 'Missing or invalid Authorization header' });
        return;
      }

      const token = authHeader.substring(7); // Remove 'Bearer ' prefix

      // Verify the token
      const user = await verifyGoogleToken(token);
      if (!user) {
        res.status(401).json({ error: 'Invalid or expired token' });
        return;
      }

      // Check if user has a recognized role
      const role = getUserRole(user.email);
      if (!role) {
        res.status(403).json({ error: 'User not authorized for this platform' });
        return;
      }

      // Check if user's role is allowed for this endpoint
      if (!allowedRoles.includes(role)) {
        res.status(403).json({ 
          error: 'Insufficient permissions',
          requiredRoles: allowedRoles,
          userRole: role,
        });
        return;
      }

      // Attach user info to request
      req.user = {
        email: user.email,
        role,
        name: user.name,
      };

      next();
    } catch (error) {
      console.error('Authentication error:', error);
      res.status(500).json({ error: 'Authentication failed' });
    }
  };
}
