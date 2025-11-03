# Deployment Instructions

This guide covers deploying the Nexus API Platform to various cloud providers and infrastructure platforms.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Render.com Deployment](#rendercom-deployment)
3. [Netlify Deployment](#netlify-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [Environment Variables](#environment-variables)
7. [Post-Deployment Checklist](#post-deployment-checklist)

---

## Prerequisites

Before deploying, ensure you have:

- [ ] Git repository access
- [ ] API keys and secrets generated
- [ ] Database (PostgreSQL) provisioned
- [ ] Redis instance available
- [ ] SSL certificates (for production)
- [ ] Domain name configured (optional)

### Generate Required Secrets

```bash
# Generate API key
openssl rand -hex 32

# Generate session secret
openssl rand -base64 32

# Generate JWT secret
openssl rand -hex 64
```

---

## Render.com Deployment

Render.com provides a simple platform-as-a-service for deploying web services.

### Step 1: Create New Web Service

1. Log in to [Render.com](https://render.com)
2. Click **"New"** → **"Web Service"**
3. Connect your GitHub repository
4. Select the repository: `hannesmitterer/AI-Based-Peace-Platform`
5. Configure the service:

```yaml
Name: nexus-api
Environment: Node
Region: Oregon (US West)
Branch: main
Build Command: npm install && npm run build
Start Command: npm start
```

### Step 2: Configure Environment Variables

In the Render dashboard, add these environment variables:

#### Core Configuration
```
PORT=3000
NODE_ENV=production
API_VERSION=v1
```

#### Database & Cache
```
DATABASE_URL=<your_postgresql_url>
REDIS_URL=<your_redis_url>
```

#### Authentication
```
NEXUS_API_KEY=<generated_api_key>
NEXUS_SECRET_KEY=<generated_secret_key>
SESSION_SECRET=<generated_session_secret>
JWT_EXPIRY=24h
```

#### OAuth (Gmail)
```
OAUTH_CLIENT_ID=<your_oauth_client_id>
OAUTH_CLIENT_SECRET=<your_oauth_client_secret>
OAUTH_REDIRECT_URI=https://your-app.onrender.com/auth/callback
```

#### Security
```
ALLOWED_ORIGINS=https://your-app.onrender.com
RATE_LIMIT_WINDOW=3600
RATE_LIMIT_MAX_REQUESTS=1000
ENABLE_CORS=true
```

#### Features
```
ENABLE_WEBSOCKET=true
ENABLE_TELEMETRY=true
ENABLE_ANALYTICS=false
LOG_LEVEL=info
```

### Step 3: Add PostgreSQL Database

1. In your Render dashboard, click **"New"** → **"PostgreSQL"**
2. Configure:
   - **Name**: nexus-db
   - **Region**: Same as web service
   - **Plan**: Starter or higher
3. Copy the **Internal Database URL** and add it as `DATABASE_URL` in your web service

### Step 4: Add Redis Instance

1. Click **"New"** → **Redis"**
2. Configure:
   - **Name**: nexus-redis
   - **Region**: Same as web service
   - **Plan**: Starter or higher
3. Copy the **Internal Redis URL** and add it as `REDIS_URL` in your web service

### Step 5: Deploy

1. Click **"Create Web Service"**
2. Render will automatically build and deploy
3. Monitor logs in the dashboard
4. Once deployed, access your API at: `https://your-app.onrender.com`

### Step 6: Verify Deployment

```bash
# Check health endpoint
curl https://your-app.onrender.com/api/v1/health

# Expected response:
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-03T01:54:42.407Z"
}
```

### Render Auto-Deploy Setup

To enable automatic deployments on push:

1. Go to your web service settings
2. Under **"Build & Deploy"**, enable **"Auto-Deploy"**
3. Select branch: `main`
4. Now every push to main will trigger a deployment

---

## Netlify Deployment

Netlify is ideal for static sites and serverless functions. For the Nexus API, we'll use Netlify Functions.

### Step 1: Install Netlify CLI

```bash
npm install -g netlify-cli
netlify login
```

### Step 2: Create netlify.toml

This file is already in the repository. Verify it contains:

```toml
[build]
  command = "npm run build"
  functions = "netlify/functions"
  publish = "public"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200

[[headers]]
  for = "/api/*"
  [headers.values]
    Access-Control-Allow-Origin = "*"
    Access-Control-Allow-Methods = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
    Access-Control-Allow-Headers = "Content-Type, Authorization"
```

### Step 3: Set Up Netlify Functions

Create function files in `netlify/functions/`:

```bash
mkdir -p netlify/functions
```

**Example: Health Check Function** (`netlify/functions/health.js`)
```javascript
exports.handler = async (event, context) => {
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      status: 'healthy',
      version: '1.0.0',
      timestamp: new Date().toISOString()
    })
  };
};
```

### Step 4: Configure Environment Variables

In Netlify dashboard:

1. Go to **Site settings** → **Environment variables**
2. Add the same variables as Render (see above)

Or via CLI:

```bash
netlify env:set NEXUS_API_KEY "your_api_key_here"
netlify env:set DATABASE_URL "your_database_url"
netlify env:set REDIS_URL "your_redis_url"
# ... (add all required variables)
```

### Step 5: Deploy

#### Option A: Manual Deploy
```bash
# Build and deploy
npm run build
netlify deploy --prod
```

#### Option B: Connect Git Repository
1. Go to Netlify dashboard
2. Click **"Add new site"** → **"Import an existing project"**
3. Connect GitHub and select repository
4. Configure:
   - **Branch**: main
   - **Build command**: `npm run build`
   - **Publish directory**: `public`
5. Click **"Deploy site"**

### Step 6: Verify Deployment

```bash
# Check health endpoint
curl https://your-site.netlify.app/api/health

# Or use Netlify CLI
netlify open
```

### Netlify Limitations

⚠️ **Note**: Netlify Functions have:
- 10-second execution limit (26s for Pro plans)
- Limited WebSocket support (use external WebSocket server)
- Consider Render or custom hosting for long-running WebSocket connections

---

## Docker Deployment

### Step 1: Create Dockerfile

Create `Dockerfile` in repository root:

```dockerfile
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy application code
COPY . .

# Build application
RUN npm run build

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node healthcheck.js || exit 1

# Start application
CMD ["npm", "start"]
```

### Step 2: Create docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://postgres:password@db:5432/nexus
      - REDIS_URL=redis://redis:6379
    env_file:
      - .env
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=nexus
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### Step 3: Build and Run

```bash
# Build image
docker build -t nexus-api .

# Run with docker-compose
docker-compose up -d

# Check logs
docker-compose logs -f api

# Check health
curl http://localhost:3000/api/v1/health
```

### Step 4: Production Deployment

For production, use Docker Swarm or Kubernetes for orchestration.

---

## Kubernetes Deployment

### Step 1: Create Kubernetes Manifests

**Namespace** (`k8s/namespace.yaml`):
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: nexus-api
```

**ConfigMap** (`k8s/configmap.yaml`):
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nexus-config
  namespace: nexus-api
data:
  NODE_ENV: "production"
  PORT: "3000"
  API_VERSION: "v1"
  LOG_LEVEL: "info"
```

**Secret** (`k8s/secret.yaml`):
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: nexus-secrets
  namespace: nexus-api
type: Opaque
stringData:
  NEXUS_API_KEY: "<base64-encoded-key>"
  DATABASE_URL: "<base64-encoded-url>"
  REDIS_URL: "<base64-encoded-url>"
  SESSION_SECRET: "<base64-encoded-secret>"
```

**Deployment** (`k8s/deployment.yaml`):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nexus-api
  namespace: nexus-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nexus-api
  template:
    metadata:
      labels:
        app: nexus-api
    spec:
      containers:
      - name: api
        image: your-registry/nexus-api:latest
        ports:
        - containerPort: 3000
        envFrom:
        - configMapRef:
            name: nexus-config
        - secretRef:
            name: nexus-secrets
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
```

**Service** (`k8s/service.yaml`):
```yaml
apiVersion: v1
kind: Service
metadata:
  name: nexus-api-service
  namespace: nexus-api
spec:
  selector:
    app: nexus-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: LoadBalancer
```

### Step 2: Apply Manifests

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create config and secrets
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

# Deploy application
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Check status
kubectl get pods -n nexus-api
kubectl get services -n nexus-api
```

### Step 3: Set Up Ingress (Optional)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nexus-api-ingress
  namespace: nexus-api
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.nexus.example.com
    secretName: nexus-api-tls
  rules:
  - host: api.nexus.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nexus-api-service
            port:
              number: 80
```

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `PORT` | Server port | `3000` |
| `NODE_ENV` | Environment | `production` |
| `DATABASE_URL` | PostgreSQL connection | `postgresql://user:pass@host/db` |
| `REDIS_URL` | Redis connection | `redis://host:6379` |
| `NEXUS_API_KEY` | API authentication key | `<generated-key>` |
| `SESSION_SECRET` | Session encryption | `<generated-secret>` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_VERSION` | API version | `v1` |
| `LOG_LEVEL` | Logging level | `info` |
| `ENABLE_WEBSOCKET` | Enable WebSocket | `true` |
| `ENABLE_TELEMETRY` | Enable telemetry | `true` |
| `RATE_LIMIT_MAX_REQUESTS` | Max requests/hour | `1000` |

---

## Post-Deployment Checklist

After deployment, verify:

- [ ] Health endpoint returns 200 OK
- [ ] Database migrations completed
- [ ] Redis connection established
- [ ] WebSocket connections working
- [ ] SSL/TLS certificates valid
- [ ] Environment variables loaded correctly
- [ ] Logging and monitoring configured
- [ ] Backup strategy implemented
- [ ] Security headers configured
- [ ] Rate limiting active
- [ ] CORS configured properly
- [ ] API documentation accessible

### Verification Commands

```bash
# Health check
curl https://your-api.example.com/api/v1/health

# Check status
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://your-api.example.com/api/v1/status

# Test WebSocket
wscat -c wss://your-api.example.com/api/v1/events?token=YOUR_API_KEY

# Load test (optional)
ab -n 1000 -c 10 https://your-api.example.com/api/v1/health
```

---

## Monitoring & Logging

### Recommended Tools

- **Logging**: Datadog, Loggly, Papertrail
- **Monitoring**: New Relic, AppDynamics, Prometheus
- **Error Tracking**: Sentry, Rollbar
- **Uptime Monitoring**: Pingdom, UptimeRobot

### Set Up Logging

```javascript
// Add to your application
const winston = require('winston');
const Sentry = require('@sentry/node');

// Sentry for error tracking
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV
});

// Winston for general logging
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});
```

---

## Troubleshooting

### Common Issues

#### Database Connection Fails
```bash
# Check DATABASE_URL format
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"

# Check firewall rules
# Ensure database allows connections from your deployment IP
```

#### WebSocket Not Working
```bash
# Verify WebSocket is enabled
echo $ENABLE_WEBSOCKET

# Check for proxy/load balancer WebSocket support
# Most platforms require specific configuration for WebSocket passthrough

# Render: WebSockets supported by default
# Netlify: Not supported, use external WebSocket server
```

#### Rate Limiting Too Strict
```bash
# Adjust rate limit
export RATE_LIMIT_MAX_REQUESTS=10000
export RATE_LIMIT_WINDOW=3600
```

---

## Rollback Procedure

If deployment fails:

### Render
1. Go to dashboard
2. Click on your service
3. Select **"Rollback"** from deploy history

### Netlify
1. Go to **Deploys** tab
2. Find previous successful deploy
3. Click **"Publish deploy"**

### Docker/Kubernetes
```bash
# Docker: Revert to previous image
docker-compose down
docker-compose pull
docker-compose up -d

# Kubernetes: Rollback deployment
kubectl rollout undo deployment/nexus-api -n nexus-api
```

---

## Support

For deployment assistance:
- **Email**: support@nexus-api.example.com
- **Documentation**: https://docs.nexus-api.example.com/deployment
- **GitHub Issues**: https://github.com/hannesmitterer/AI-Based-Peace-Platform/issues

---

**Deployment Guide v1.0.0**  
Last Updated: 2025-11-03
