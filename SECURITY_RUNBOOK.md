# Security Runbook

Comprehensive security guide for the Nexus API Platform covering best practices, security checklist, incident response, and operational security procedures.

## Table of Contents

1. [Security Overview](#security-overview)
2. [Security Checklist](#security-checklist)
3. [Authentication & Authorization](#authentication--authorization)
4. [Secret Management](#secret-management)
5. [Session Management](#session-management)
6. [Rate Limiting & DDoS Protection](#rate-limiting--ddos-protection)
7. [Data Protection](#data-protection)
8. [Audit Logging](#audit-logging)
9. [Vulnerability Management](#vulnerability-management)
10. [Incident Response](#incident-response)
11. [Security Monitoring](#security-monitoring)

---

## Security Overview

### Security Principles

1. **Defense in Depth**: Multiple layers of security controls
2. **Least Privilege**: Minimum necessary permissions
3. **Zero Trust**: Never trust, always verify
4. **Fail Secure**: Default to secure state on errors
5. **Audit Everything**: Comprehensive logging and monitoring

### Threat Model

**Threats:**
- Unauthorized API access
- Data breaches and leaks
- DDoS attacks
- Injection attacks (SQL, NoSQL, Command)
- Session hijacking
- Man-in-the-middle attacks
- Credential theft
- Insider threats

**Assets to Protect:**
- API credentials and tokens
- User data and PII
- Peace initiative intelligence
- Agent coordination data
- System configurations
- Audit logs

---

## Security Checklist

### Pre-Deployment Checklist

- [ ] All secrets stored in environment variables or secret manager
- [ ] HTTPS/TLS enabled for all endpoints
- [ ] API keys rotated and documented
- [ ] Database credentials secured and rotated
- [ ] OAuth credentials configured correctly
- [ ] CORS configured with specific origins (no wildcards in production)
- [ ] Rate limiting enabled
- [ ] Input validation implemented
- [ ] SQL injection prevention verified
- [ ] XSS protection enabled
- [ ] CSRF protection implemented
- [ ] Security headers configured
- [ ] Dependency vulnerabilities scanned
- [ ] Code security reviewed
- [ ] Audit logging enabled
- [ ] Monitoring and alerting configured
- [ ] Backup and recovery tested
- [ ] Incident response plan documented
- [ ] Security contact information updated
- [ ] Compliance requirements met

### Post-Deployment Checklist

- [ ] SSL/TLS certificate valid and auto-renewing
- [ ] Monitoring dashboards reviewed
- [ ] Log aggregation working
- [ ] Alert notifications received
- [ ] Backup schedule verified
- [ ] Access logs reviewed for anomalies
- [ ] Rate limiting tested
- [ ] Authentication working correctly
- [ ] API documentation updated
- [ ] Security scan performed
- [ ] Penetration testing completed (if required)

### Weekly Security Tasks

- [ ] Review access logs for suspicious activity
- [ ] Check for failed authentication attempts
- [ ] Review rate limiting metrics
- [ ] Verify backup completion
- [ ] Check SSL certificate expiration
- [ ] Review security alerts
- [ ] Update security documentation

### Monthly Security Tasks

- [ ] Rotate API keys
- [ ] Review and update access controls
- [ ] Scan dependencies for vulnerabilities
- [ ] Review audit logs
- [ ] Test incident response procedures
- [ ] Review and update security policies
- [ ] Conduct security training

### Quarterly Security Tasks

- [ ] Comprehensive security audit
- [ ] Penetration testing
- [ ] Disaster recovery drill
- [ ] Access review (revoke unused accounts)
- [ ] Update security runbook
- [ ] Review compliance status
- [ ] External security assessment

---

## Authentication & Authorization

### API Key Management

#### Generate Secure API Keys

```javascript
const crypto = require('crypto');

function generateAPIKey() {
  return crypto.randomBytes(32).toString('hex');
}

function generateSecretKey() {
  return crypto.randomBytes(64).toString('base64');
}

// Example
const apiKey = generateAPIKey();
const secretKey = generateSecretKey();

console.log('API Key:', apiKey);
console.log('Secret Key:', secretKey);
```

#### API Key Validation

```javascript
const crypto = require('crypto');

async function validateAPIKey(apiKey) {
  // Hash the API key
  const hashedKey = crypto
    .createHash('sha256')
    .update(apiKey)
    .digest('hex');
  
  // Look up in database (store hashed keys only)
  const storedKey = await db.apiKeys.findOne({ 
    hashedKey: hashedKey,
    active: true,
    expiresAt: { $gt: new Date() }
  });
  
  if (!storedKey) {
    throw new Error('Invalid or expired API key');
  }
  
  // Update last used timestamp
  await db.apiKeys.updateOne(
    { _id: storedKey._id },
    { $set: { lastUsedAt: new Date() } }
  );
  
  return storedKey;
}

// Middleware
async function authenticateAPIKey(req, res, next) {
  const authHeader = req.headers.authorization;
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing API key' });
  }
  
  const apiKey = authHeader.substring(7);
  
  try {
    const keyData = await validateAPIKey(apiKey);
    req.apiKey = keyData;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid API key' });
  }
}
```

#### API Key Rotation

```javascript
async function rotateAPIKey(oldApiKey) {
  // Validate old key
  const keyData = await validateAPIKey(oldApiKey);
  
  // Generate new key
  const newApiKey = generateAPIKey();
  const hashedNewKey = crypto
    .createHash('sha256')
    .update(newApiKey)
    .digest('hex');
  
  // Update in database
  await db.apiKeys.updateOne(
    { _id: keyData._id },
    { 
      $set: { 
        hashedKey: hashedNewKey,
        rotatedAt: new Date(),
        previousKey: keyData.hashedKey
      } 
    }
  );
  
  // Return new key (only time it's shown in plaintext)
  return {
    apiKey: newApiKey,
    message: 'API key rotated successfully. Save this key securely.',
    expiresAt: keyData.expiresAt
  };
}
```

### OAuth Token Security

```javascript
const jwt = require('jsonwebtoken');

// Generate JWT
function generateAccessToken(user) {
  return jwt.sign(
    { 
      userId: user.id,
      email: user.email,
      roles: user.roles
    },
    process.env.JWT_SECRET,
    { 
      expiresIn: '1h',
      issuer: 'nexus-api',
      audience: 'nexus-clients'
    }
  );
}

// Validate JWT
function validateAccessToken(token) {
  try {
    return jwt.verify(token, process.env.JWT_SECRET, {
      issuer: 'nexus-api',
      audience: 'nexus-clients'
    });
  } catch (error) {
    throw new Error('Invalid token');
  }
}

// Middleware
function authenticateJWT(req, res, next) {
  const authHeader = req.headers.authorization;
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing token' });
  }
  
  const token = authHeader.substring(7);
  
  try {
    const user = validateAccessToken(token);
    req.user = user;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid or expired token' });
  }
}
```

---

## Secret Management

### Environment Variables

**DO:**
- ✅ Store all secrets in environment variables
- ✅ Use `.env` files for local development (add to `.gitignore`)
- ✅ Use platform-specific secret managers in production
- ✅ Rotate secrets regularly
- ✅ Use different secrets for different environments

**DON'T:**
- ❌ Commit secrets to version control
- ❌ Hardcode secrets in source code
- ❌ Share secrets via email or chat
- ❌ Use weak or predictable secrets
- ❌ Reuse secrets across environments

### Secret Encryption

```javascript
const crypto = require('crypto');

class SecretManager {
  constructor(masterKey) {
    this.masterKey = masterKey;
    this.algorithm = 'aes-256-gcm';
  }

  encrypt(plaintext) {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv(
      this.algorithm,
      Buffer.from(this.masterKey, 'hex'),
      iv
    );
    
    let encrypted = cipher.update(plaintext, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    const authTag = cipher.getAuthTag();
    
    return {
      encrypted,
      iv: iv.toString('hex'),
      authTag: authTag.toString('hex')
    };
  }

  decrypt(encrypted, iv, authTag) {
    const decipher = crypto.createDecipheriv(
      this.algorithm,
      Buffer.from(this.masterKey, 'hex'),
      Buffer.from(iv, 'hex')
    );
    
    decipher.setAuthTag(Buffer.from(authTag, 'hex'));
    
    let decrypted = decipher.update(encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    
    return decrypted;
  }
}

// Usage
const secretManager = new SecretManager(process.env.MASTER_KEY);

// Encrypt secret before storing
const { encrypted, iv, authTag } = secretManager.encrypt('my-secret-value');
await db.secrets.save({ encrypted, iv, authTag });

// Decrypt when needed
const secret = secretManager.decrypt(encrypted, iv, authTag);
```

### AWS Secrets Manager Integration

```javascript
const AWS = require('aws-sdk');
const secretsManager = new AWS.SecretsManager({ region: 'us-east-1' });

async function getSecret(secretName) {
  try {
    const data = await secretsManager.getSecretValue({ 
      SecretId: secretName 
    }).promise();
    
    if (data.SecretString) {
      return JSON.parse(data.SecretString);
    }
    
    const buff = Buffer.from(data.SecretBinary, 'base64');
    return buff.toString('ascii');
  } catch (error) {
    console.error('Error retrieving secret:', error);
    throw error;
  }
}

// Usage
const dbCredentials = await getSecret('nexus/db/credentials');
const apiKeys = await getSecret('nexus/api/keys');
```

---

## Session Management

### Session Configuration

```javascript
const session = require('express-session');
const RedisStore = require('connect-redis')(session);
const redis = require('redis');

const redisClient = redis.createClient({
  url: process.env.REDIS_URL,
  password: process.env.REDIS_PASSWORD
});

app.use(session({
  store: new RedisStore({ client: redisClient }),
  secret: process.env.SESSION_SECRET,
  name: 'nexus.sid',
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: process.env.NODE_ENV === 'production', // HTTPS only
    httpOnly: true, // Not accessible via JavaScript
    maxAge: 24 * 60 * 60 * 1000, // 24 hours
    sameSite: 'strict' // CSRF protection
  }
}));
```

### Session Cleanup

```javascript
// Automated session cleanup script
async function cleanupExpiredSessions() {
  const now = Date.now();
  
  // Get all session keys
  const keys = await redisClient.keys('sess:*');
  
  let cleaned = 0;
  
  for (const key of keys) {
    const session = await redisClient.get(key);
    
    if (!session) continue;
    
    const sessionData = JSON.parse(session);
    const expiry = sessionData.cookie?.expires;
    
    if (expiry && new Date(expiry) < now) {
      await redisClient.del(key);
      cleaned++;
    }
  }
  
  console.log(`Cleaned ${cleaned} expired sessions`);
  return cleaned;
}

// Run every hour
setInterval(cleanupExpiredSessions, 60 * 60 * 1000);
```

### Session Invalidation

```javascript
// Logout endpoint
app.post('/api/v1/auth/logout', (req, res) => {
  req.session.destroy((err) => {
    if (err) {
      console.error('Session destruction error:', err);
      return res.status(500).json({ error: 'Logout failed' });
    }
    
    res.clearCookie('nexus.sid');
    res.json({ message: 'Logged out successfully' });
  });
});

// Revoke all sessions for a user
async function revokeAllUserSessions(userId) {
  const keys = await redisClient.keys('sess:*');
  
  let revoked = 0;
  
  for (const key of keys) {
    const session = await redisClient.get(key);
    if (!session) continue;
    
    const sessionData = JSON.parse(session);
    
    if (sessionData.userId === userId) {
      await redisClient.del(key);
      revoked++;
    }
  }
  
  console.log(`Revoked ${revoked} sessions for user ${userId}`);
  return revoked;
}
```

---

## Rate Limiting & DDoS Protection

### Express Rate Limiter

```javascript
const rateLimit = require('express-rate-limit');
const RedisStore = require('rate-limit-redis');
const redis = require('redis');

const redisClient = redis.createClient({
  url: process.env.REDIS_URL
});

// General API rate limiter
const apiLimiter = rateLimit({
  store: new RedisStore({ client: redisClient }),
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 1000, // 1000 requests per hour
  message: {
    error: 'Too many requests, please try again later',
    retryAfter: 3600
  },
  standardHeaders: true,
  legacyHeaders: false,
  keyGenerator: (req) => {
    // Use API key or IP address
    return req.apiKey?.id || req.ip;
  }
});

// Strict rate limiter for authentication endpoints
const authLimiter = rateLimit({
  store: new RedisStore({ client: redisClient }),
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 attempts
  skipSuccessfulRequests: true,
  message: {
    error: 'Too many authentication attempts',
    retryAfter: 900
  }
});

// Apply limiters
app.use('/api/v1/', apiLimiter);
app.use('/api/v1/auth/', authLimiter);
```

### Custom Rate Limiting Logic

```javascript
const RATE_LIMITS = {
  free: { requestsPerHour: 1000, burst: 100 },
  standard: { requestsPerHour: 10000, burst: 500 },
  premium: { requestsPerHour: 100000, burst: 2000 },
  enterprise: { requestsPerHour: Infinity, burst: 5000 }
};

async function checkRateLimit(apiKey) {
  const tier = apiKey.tier || 'free';
  const limits = RATE_LIMITS[tier];
  
  const key = `ratelimit:${apiKey.id}`;
  const now = Date.now();
  const windowStart = now - (60 * 60 * 1000);
  
  // Remove old entries
  await redisClient.zremrangebyscore(key, 0, windowStart);
  
  // Count requests in current window
  const count = await redisClient.zcard(key);
  
  if (count >= limits.requestsPerHour) {
    throw new Error('Rate limit exceeded');
  }
  
  // Add current request
  await redisClient.zadd(key, now, `${now}-${Math.random()}`);
  await redisClient.expire(key, 3600);
  
  return {
    allowed: true,
    remaining: limits.requestsPerHour - count - 1,
    reset: windowStart + (60 * 60 * 1000)
  };
}
```

### DDoS Protection

```javascript
// Implement connection throttling
const helmet = require('helmet');
const slowDown = require('express-slow-down');

app.use(helmet());

const speedLimiter = slowDown({
  windowMs: 15 * 60 * 1000, // 15 minutes
  delayAfter: 100, // Allow 100 requests per 15 minutes
  delayMs: 500 // Add 500ms delay per request above limit
});

app.use('/api/v1/', speedLimiter);

// IP blocking for repeated violations
const blockedIPs = new Set();

async function blockIP(ip, duration = 3600000) {
  blockedIPs.add(ip);
  setTimeout(() => blockedIPs.delete(ip), duration);
  
  // Also store in Redis for distributed systems
  await redisClient.setex(`blocked:${ip}`, duration / 1000, '1');
}

app.use((req, res, next) => {
  if (blockedIPs.has(req.ip)) {
    return res.status(403).json({ error: 'Access denied' });
  }
  next();
});
```

---

## Data Protection

### Input Validation

```javascript
const Joi = require('joi');

// Define schemas
const schemas = {
  createTask: Joi.object({
    name: Joi.string().min(1).max(200).required(),
    type: Joi.string().valid('analysis', 'coordination', 'monitoring').required(),
    priority: Joi.string().valid('low', 'medium', 'high', 'critical'),
    assignedTo: Joi.string().pattern(/^agent-[a-z0-9]+$/),
    parameters: Joi.object(),
    deadline: Joi.date().iso()
  }),
  
  submitTelemetry: Joi.object({
    agentId: Joi.string().pattern(/^agent-[a-z0-9]+$/).required(),
    timestamp: Joi.date().iso().required(),
    metrics: Joi.object().pattern(
      Joi.string(),
      Joi.number()
    ).required(),
    status: Joi.string().valid('active', 'inactive', 'offline').required()
  })
};

// Validation middleware
function validate(schema) {
  return (req, res, next) => {
    const { error, value } = schema.validate(req.body, {
      abortEarly: false,
      stripUnknown: true
    });
    
    if (error) {
      return res.status(400).json({
        error: 'Validation failed',
        details: error.details.map(d => ({
          field: d.path.join('.'),
          message: d.message
        }))
      });
    }
    
    req.validatedBody = value;
    next();
  };
}

// Usage
app.post('/api/v1/tasks', 
  authenticateAPIKey,
  validate(schemas.createTask),
  async (req, res) => {
    const task = await createTask(req.validatedBody);
    res.json(task);
  }
);
```

### SQL Injection Prevention

```javascript
// Use parameterized queries
const { Pool } = require('pg');
const pool = new Pool({ connectionString: process.env.DATABASE_URL });

// ✅ SAFE: Parameterized query
async function getTask(taskId) {
  const result = await pool.query(
    'SELECT * FROM tasks WHERE id = $1',
    [taskId]
  );
  return result.rows[0];
}

// ❌ UNSAFE: String concatenation
async function getTaskUnsafe(taskId) {
  const result = await pool.query(
    `SELECT * FROM tasks WHERE id = '${taskId}'` // DON'T DO THIS!
  );
  return result.rows[0];
}
```

### XSS Prevention

```javascript
const createDOMPurify = require('isomorphic-dompurify');
const { escape } = require('html-escaper');

// Sanitize HTML input
function sanitizeHTML(dirty) {
  return createDOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a'],
    ALLOWED_ATTR: ['href']
  });
}

// Escape output
function escapeOutput(text) {
  return escape(text);
}

// Middleware to set security headers
app.use((req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader(
    'Content-Security-Policy',
    "default-src 'self'; script-src 'self'"
  );
  next();
});
```

---

## Audit Logging

### Comprehensive Audit Logger

```javascript
const winston = require('winston');

const auditLogger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ 
      filename: 'logs/audit.log',
      maxsize: 10485760, // 10MB
      maxFiles: 10
    }),
    new winston.transports.Console({
      format: winston.format.simple()
    })
  ]
});

// Audit log function
function auditLog(event, details) {
  auditLogger.info({
    event,
    timestamp: new Date().toISOString(),
    ...details
  });
}

// Audit middleware
function auditMiddleware(req, res, next) {
  const start = Date.now();
  
  res.on('finish', () => {
    auditLog('api_request', {
      method: req.method,
      path: req.path,
      statusCode: res.statusCode,
      duration: Date.now() - start,
      ip: req.ip,
      userAgent: req.headers['user-agent'],
      userId: req.user?.id || req.apiKey?.id
    });
  });
  
  next();
}

app.use(auditMiddleware);
```

### Security Event Logging

```javascript
// Log security events
function logSecurityEvent(eventType, details) {
  auditLogger.warn({
    event: 'security_event',
    eventType,
    timestamp: new Date().toISOString(),
    severity: 'high',
    ...details
  });
  
  // Send alert if critical
  if (details.severity === 'critical') {
    sendSecurityAlert(eventType, details);
  }
}

// Examples
logSecurityEvent('failed_authentication', {
  ip: req.ip,
  apiKey: 'xxx...xxx',
  reason: 'Invalid API key'
});

logSecurityEvent('rate_limit_exceeded', {
  ip: req.ip,
  endpoint: req.path,
  count: 1001
});

logSecurityEvent('suspicious_activity', {
  ip: req.ip,
  pattern: 'Multiple failed auth attempts',
  severity: 'critical'
});
```

---

## Vulnerability Management

### Dependency Scanning

```bash
# Scan for vulnerabilities
npm audit

# Fix automatically
npm audit fix

# Check specific package
npm audit --package=package-name

# Generate audit report
npm audit --json > audit-report.json
```

### Automated Security Scanning

```javascript
// package.json
{
  "scripts": {
    "security-check": "npm audit && npm outdated",
    "security-fix": "npm audit fix",
    "pre-commit": "npm run security-check"
  }
}
```

---

## Incident Response

### Incident Response Plan

**1. Detection**
- Monitor alerts and logs
- Identify security incidents
- Assess severity

**2. Containment**
- Isolate affected systems
- Block malicious IPs
- Revoke compromised credentials

**3. Eradication**
- Remove malicious code
- Patch vulnerabilities
- Update security controls

**4. Recovery**
- Restore from backups
- Verify system integrity
- Resume normal operations

**5. Post-Incident**
- Document incident
- Update procedures
- Conduct review

### Emergency Contacts

```
Security Lead: security@nexus-api.example.com
On-Call: +1-555-SECURITY
Incident Hotline: incidents@nexus-api.example.com
```

---

**Security Runbook v1.0.0**  
Last Updated: 2025-11-03
