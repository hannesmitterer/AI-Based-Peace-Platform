# ALO-001 Backend Setup Guide

This guide explains how to set up and deploy the ALO-001 backend with Google OAuth RBAC.

## Prerequisites

- Node.js 18+ and npm
- A Google Cloud Platform project with OAuth 2.0 credentials
- Domain or localhost for testing

## Setup Instructions

### 1. Google Cloud Configuration

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable the **People API** or **Google Identity Services**
4. Go to **APIs & Services > Credentials**
5. Create an **OAuth 2.0 Client ID** (Web application)
6. Add authorized JavaScript origins:
   - For local development: `http://localhost:8080` and `http://localhost:3000`
   - For production: Your domain (e.g., `https://yourplatform.com`)
7. Add authorized redirect URIs (if needed for your flow)
8. Copy the **Client ID** (format: `xxx.apps.googleusercontent.com`)

### 2. Environment Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Update `.env` with your Google Client ID:
   ```
   GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
   ```

3. Verify the email allowlists in `.env`:
   ```
   SEEDBRINGER_EMAILS=hannes.mitterer@gmail.com
   COUNCIL_EMAILS=dietmar.zuegg@gmail.com,bioarchitettura.rivista@gmail.com,consultant.laquila@gmail.com
   ```

### 3. Frontend Configuration

Update the Google Client ID in `public/pbl-001/index.html`:

```html
<div id="g_id_onload"
     data-client_id="YOUR_GOOGLE_CLIENT_ID"
     data-callback="handleCredentialResponse"
     data-auto_prompt="false">
</div>
```

Replace `YOUR_GOOGLE_CLIENT_ID` with the same Client ID from step 2.

### 4. Install Dependencies

```bash
npm install
```

### 5. Build the Backend

```bash
npm run build
```

### 6. Start the Server

```bash
npm start
```

The server will start on port 8080 (or the port specified in `.env`).

### 7. Test the Application

1. Open `public/pbl-001/index.html` in a web browser
2. Ensure the backend API URL in the HTML matches your server (default: `http://localhost:8080`)
3. Sign in with a Google account listed in the allowlists
4. Test the protected endpoints

## API Endpoints

### Public Endpoints

- **GET /health** - Health check endpoint (no authentication required)

### Protected Endpoints

All protected endpoints require a valid Google ID token in the `Authorization` header:

```
Authorization: Bearer <google-id-token>
```

#### GET /sfi

**Description:** Systemic Fairness Index - Global inequality and access metrics  
**Access:** Council or Seedbringer  
**Response:**
```json
{
  "index": "Systemic Fairness Index",
  "currentValue": 7.2,
  "status": "Persistent Disparity",
  "requestedBy": {
    "email": "user@example.com",
    "role": "council"
  }
}
```

#### GET /mcl/live

**Description:** Mission Critical Live - Real-time system monitoring  
**Access:** Council or Seedbringer  
**Response:**
```json
{
  "endpoint": "Mission Critical Live",
  "metrics": {
    "globalScarcityIndex": 6.8,
    "regionalStability": "Elevated Risk",
    "dasProtocolImpact": "Initial Growth Phase"
  }
}
```

#### POST /allocations

**Description:** Create a new resource allocation  
**Access:** Seedbringer only (write access)  
**Request Body:**
```json
{
  "amount": 50000,
  "target": "Sahel Region",
  "purpose": "DAS Protocol implementation"
}
```

**Response:**
```json
{
  "message": "Allocation created successfully",
  "allocation": {
    "id": "alloc-1698765432000",
    "amount": 50000,
    "target": "Sahel Region",
    "purpose": "DAS Protocol implementation",
    "status": "pending",
    "createdBy": "hannes.mitterer@gmail.com",
    "createdAt": "2025-10-29T05:00:00.000Z"
  }
}
```

## Role-Based Access Control

### Seedbringer Role

**Emails:** hannes.mitterer@gmail.com  
**Permissions:**
- Read access to GET /sfi
- Read access to GET /mcl/live
- Write access to POST /allocations

**Required Scopes:**
- `https://www.googleapis.com/auth/userinfo.email`
- `https://www.googleapis.com/auth/userinfo.profile`

### Council Role

**Emails:**
- dietmar.zuegg@gmail.com
- bioarchitettura.rivista@gmail.com
- consultant.laquila@gmail.com

**Permissions:**
- Read access to GET /sfi
- Read access to GET /mcl/live
- No write access (403 on POST /allocations)

**Required Scopes:**
- `https://www.googleapis.com/auth/userinfo.email`

## Security Notes

1. **Never commit `.env` to version control** - It contains sensitive configuration
2. **Token verification happens server-side** - The backend validates all Google ID tokens
3. **Role enforcement is server-side** - Client-side role checks are for UX only
4. **HTTPS in production** - Always use HTTPS for production deployments
5. **CORS configuration** - Update `CORS_ALLOW_ORIGIN` in `.env` for production (set to specific domain instead of `*`)
6. **Rate limiting** - The server includes rate limiting (default: 100 requests per 15 minutes per IP). Configure via `RATE_LIMIT_WINDOW_MS` and `RATE_LIMIT_MAX_REQUESTS` in `.env`

### Rate Limiting

The backend includes automatic rate limiting to prevent abuse and DoS attacks:
- Default: 100 requests per 15 minutes per IP address
- Configurable via environment variables:
  - `RATE_LIMIT_WINDOW_MS`: Time window in milliseconds (default: 900000 = 15 minutes)
  - `RATE_LIMIT_MAX_REQUESTS`: Maximum requests per window (default: 100)
- Rate limit information is returned in response headers:
  - `RateLimit-Limit`: Maximum requests allowed
  - `RateLimit-Remaining`: Remaining requests in current window
  - `RateLimit-Reset`: Time until the rate limit resets (in seconds)

## Deployment

### Option 1: Traditional Server

1. Deploy to a server (e.g., AWS EC2, DigitalOcean, etc.)
2. Set environment variables
3. Run `npm install && npm run build && npm start`
4. Use a process manager like PM2 to keep the server running
5. Configure nginx or Apache as a reverse proxy

### Option 2: Containerized Deployment

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 8080
CMD ["npm", "start"]
```

### Option 3: Serverless

- Adapt the Express app for serverless platforms (AWS Lambda, Google Cloud Functions, etc.)
- Use serverless frameworks or platform-specific adapters

## Troubleshooting

### "Invalid token" errors

- Verify the Google Client ID matches in both `.env` and the frontend HTML
- Ensure the token is being sent in the Authorization header
- Check that the user's email is in the allowlist

### CORS errors

- Update `CORS_ALLOW_ORIGIN` in `.env` to match your frontend origin
- For development: `CORS_ALLOW_ORIGIN=http://localhost:3000`
- For production: `CORS_ALLOW_ORIGIN=https://yourplatform.com`

### "User not authorized" errors

- Verify the user's email is exactly matched in `SEEDBRINGER_EMAILS` or `COUNCIL_EMAILS`
- Email matching is case-sensitive and whitespace-sensitive

## Development

### Run in development mode

```bash
npm run dev
```

### Watch mode for TypeScript

Install `ts-node` and `nodemon` for development:

```bash
npm install --save-dev ts-node nodemon
```

Add to `package.json` scripts:

```json
"dev:watch": "nodemon --watch src --ext ts --exec ts-node src/server.ts"
```

## License

MIT
