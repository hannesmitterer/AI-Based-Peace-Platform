# Gmail OAuth 2.0 Setup Guide

Complete guide for setting up Gmail OAuth 2.0 integration with the Nexus API Platform for sending notifications and alerts via Gmail.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Google Cloud Console Setup](#google-cloud-console-setup)
4. [OAuth Consent Screen](#oauth-consent-screen)
5. [OAuth Credentials](#oauth-credentials)
6. [Required Scopes](#required-scopes)
7. [Environment Configuration](#environment-configuration)
8. [Testing OAuth Flow](#testing-oauth-flow)
9. [Refresh Token Management](#refresh-token-management)
10. [Troubleshooting](#troubleshooting)

---

## Overview

Gmail OAuth 2.0 allows the Nexus API to:
- Send email notifications on behalf of users
- Access Gmail API for message delivery
- Securely manage email credentials without storing passwords

### Authentication Flow

```
User → Authorization Request → Google OAuth
  ↓
Google Login & Consent
  ↓
Authorization Code → Your App
  ↓
Exchange Code for Tokens
  ↓
Access Token + Refresh Token
  ↓
Use Access Token to Send Emails
```

---

## Prerequisites

- [ ] Google account with Gmail enabled
- [ ] Google Cloud Platform (GCP) account
- [ ] Nexus API deployed and accessible via HTTPS
- [ ] Valid domain name (for production)

---

## Google Cloud Console Setup

### Step 1: Create New Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a project** → **New Project**
3. Enter project details:
   - **Project name**: `Nexus API Gmail Integration`
   - **Organization**: (your organization)
   - **Location**: (your organization or "No organization")
4. Click **Create**

### Step 2: Enable Gmail API

1. In the Cloud Console, go to **APIs & Services** → **Library**
2. Search for **"Gmail API"**
3. Click on **Gmail API**
4. Click **Enable**

### Step 3: Enable Google+ API (Optional but Recommended)

1. In the Library, search for **"Google+ API"**
2. Click **Enable**
3. This helps with user profile information

---

## OAuth Consent Screen

### Step 1: Configure Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Choose user type:
   - **Internal**: Only for Google Workspace users in your organization
   - **External**: For any Google account users

3. Click **Create**

### Step 2: App Information

Fill in the required fields:

**App name:**
```
Nexus API Platform
```

**User support email:**
```
your-email@example.com
```

**App logo:** (Optional)
- Upload a 120x120 pixel logo for your application

**Application home page:**
```
https://your-nexus-api.example.com
```

**Application privacy policy link:**
```
https://your-nexus-api.example.com/privacy
```

**Application terms of service link:**
```
https://your-nexus-api.example.com/terms
```

**Authorized domains:**
```
your-nexus-api.example.com
```

**Developer contact information:**
```
your-email@example.com
```

### Step 3: Add Scopes

Click **Add or Remove Scopes** and add these Gmail scopes:

```
https://www.googleapis.com/auth/gmail.send
https://www.googleapis.com/auth/gmail.compose
https://www.googleapis.com/auth/userinfo.email
https://www.googleapis.com/auth/userinfo.profile
```

**Scope descriptions:**
- `gmail.send`: Send emails on user's behalf
- `gmail.compose`: Create draft emails
- `userinfo.email`: View user's email address
- `userinfo.profile`: View user's basic profile info

### Step 4: Test Users (External Apps Only)

For external apps in testing mode, add test users:

1. Click **Add Users**
2. Enter email addresses of test users:
   ```
   test-user1@gmail.com
   test-user2@gmail.com
   admin@your-domain.com
   ```
3. Click **Save**

### Step 5: Summary & Verification

1. Review all settings
2. Click **Save and Continue**
3. For production use, submit for verification:
   - Click **Submit for Verification**
   - Complete the verification questionnaire
   - Verification typically takes 3-7 days

---

## OAuth Credentials

### Step 1: Create OAuth Client ID

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Select **Application type**: **Web application**

### Step 2: Configure Web Application

**Name:**
```
Nexus API OAuth Client
```

**Authorized JavaScript origins:**
```
https://your-nexus-api.example.com
http://localhost:3000  (for development)
```

**Authorized redirect URIs:**
```
https://your-nexus-api.example.com/auth/google/callback
https://your-nexus-api.example.com/api/v1/auth/callback
http://localhost:3000/auth/google/callback  (for development)
```

### Step 3: Download Credentials

1. Click **Create**
2. A dialog will appear with your credentials
3. Copy the **Client ID** and **Client Secret**
4. Optionally, click **Download JSON** to save credentials

**Example credentials format:**
```json
{
  "web": {
    "client_id": "123456789-abc123xyz.apps.googleusercontent.com",
    "client_secret": "GOCSPX-abcdefghijklmnopqrstuvwx",
    "redirect_uris": [
      "https://your-nexus-api.example.com/auth/google/callback"
    ],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token"
  }
}
```

---

## Required Scopes

### Minimal Scopes (Email Sending Only)

```javascript
const SCOPES = [
  'https://www.googleapis.com/auth/gmail.send'
];
```

### Recommended Scopes (Full Features)

```javascript
const SCOPES = [
  'https://www.googleapis.com/auth/gmail.send',
  'https://www.googleapis.com/auth/gmail.compose',
  'https://www.googleapis.com/auth/userinfo.email',
  'https://www.googleapis.com/auth/userinfo.profile'
];
```

### Optional Scopes (Advanced Features)

```javascript
const ADDITIONAL_SCOPES = [
  'https://www.googleapis.com/auth/gmail.readonly',  // Read emails
  'https://www.googleapis.com/auth/gmail.modify',    // Modify emails
  'https://www.googleapis.com/auth/gmail.labels'     // Manage labels
];
```

### Scope Descriptions

| Scope | Permission | Use Case |
|-------|------------|----------|
| `gmail.send` | Send emails | Required for notifications |
| `gmail.compose` | Create drafts | Optional for draft creation |
| `gmail.readonly` | Read emails | Optional for email analysis |
| `gmail.modify` | Modify emails | Optional for email management |
| `userinfo.email` | User email | User identification |
| `userinfo.profile` | User profile | User display name |

---

## Environment Configuration

### Step 1: Add to .env File

Create or update your `.env` file with OAuth credentials:

```bash
# Gmail OAuth 2.0 Configuration
OAUTH_CLIENT_ID=123456789-abc123xyz.apps.googleusercontent.com
OAUTH_CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrstuvwx
OAUTH_REDIRECT_URI=https://your-nexus-api.example.com/auth/google/callback

# OAuth Scopes (space-separated)
OAUTH_SCOPES=https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/userinfo.email

# Token Storage (optional - for persistent tokens)
OAUTH_TOKEN_PATH=./tokens/oauth-token.json

# Gmail Sender Configuration
GMAIL_SENDER_EMAIL=noreply@your-domain.com
GMAIL_SENDER_NAME=Nexus API Notifications
```

### Step 2: Production vs Development

**Development (.env.development):**
```bash
OAUTH_REDIRECT_URI=http://localhost:3000/auth/google/callback
NODE_ENV=development
```

**Production (.env.production):**
```bash
OAUTH_REDIRECT_URI=https://your-nexus-api.example.com/auth/google/callback
NODE_ENV=production
```

### Step 3: Secure Secrets

⚠️ **Never commit secrets to version control!**

Add to `.gitignore`:
```
.env
.env.local
.env.*.local
tokens/
oauth-token.json
credentials.json
```

Use environment variable management:
- **Render**: Environment Variables section
- **Netlify**: Site Settings → Environment Variables
- **Docker**: Use `.env` file or Docker secrets
- **Kubernetes**: Use Kubernetes Secrets

---

## Testing OAuth Flow

### Step 1: Implement Authorization Endpoint

**Node.js Example:**

```javascript
const { google } = require('googleapis');

const oauth2Client = new google.auth.OAuth2(
  process.env.OAUTH_CLIENT_ID,
  process.env.OAUTH_CLIENT_SECRET,
  process.env.OAUTH_REDIRECT_URI
);

// Generate auth URL
app.get('/auth/google', (req, res) => {
  const scopes = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/userinfo.email'
  ];

  const url = oauth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: scopes,
    prompt: 'consent' // Force consent screen to get refresh token
  });

  res.redirect(url);
});
```

### Step 2: Implement Callback Endpoint

```javascript
app.get('/auth/google/callback', async (req, res) => {
  const { code } = req.query;

  try {
    // Exchange code for tokens
    const { tokens } = await oauth2Client.getToken(code);
    oauth2Client.setCredentials(tokens);

    // Save tokens securely
    await saveTokens(tokens);

    res.send('Authentication successful! You can close this window.');
  } catch (error) {
    console.error('Error retrieving access token', error);
    res.status(500).send('Authentication failed');
  }
});
```

### Step 3: Send Test Email

```javascript
async function sendEmail(to, subject, message) {
  const gmail = google.gmail({ version: 'v1', auth: oauth2Client });

  const email = [
    `To: ${to}`,
    `Subject: ${subject}`,
    '',
    message
  ].join('\n');

  const encodedEmail = Buffer.from(email)
    .toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');

  const result = await gmail.users.messages.send({
    userId: 'me',
    requestBody: {
      raw: encodedEmail
    }
  });

  return result;
}

// Test it
await sendEmail(
  'recipient@example.com',
  'Test Email from Nexus API',
  'This is a test email sent via Gmail OAuth 2.0'
);
```

### Step 4: Test Authentication

1. Start your application:
   ```bash
   npm start
   ```

2. Navigate to authorization URL:
   ```
   http://localhost:3000/auth/google
   ```

3. You should see Google's consent screen
4. Grant permissions
5. You'll be redirected back with authorization code
6. Tokens are exchanged and saved

---

## Refresh Token Management

### Understanding Token Types

**Access Token:**
- Short-lived (1 hour)
- Used for API requests
- Must be refreshed frequently

**Refresh Token:**
- Long-lived (until revoked)
- Used to get new access tokens
- Only provided once with `access_type: 'offline'`

### Automatic Token Refresh

```javascript
const { google } = require('googleapis');
const fs = require('fs').promises;

class TokenManager {
  constructor() {
    this.oauth2Client = new google.auth.OAuth2(
      process.env.OAUTH_CLIENT_ID,
      process.env.OAUTH_CLIENT_SECRET,
      process.env.OAUTH_REDIRECT_URI
    );
  }

  async loadTokens() {
    try {
      const tokens = await fs.readFile('./tokens/oauth-token.json');
      this.oauth2Client.setCredentials(JSON.parse(tokens));
      
      // Set up automatic refresh
      this.oauth2Client.on('tokens', async (tokens) => {
        if (tokens.refresh_token) {
          await this.saveTokens(tokens);
        }
      });
    } catch (error) {
      console.error('Failed to load tokens:', error);
      throw new Error('No valid tokens found. Please authenticate.');
    }
  }

  async saveTokens(tokens) {
    await fs.writeFile(
      './tokens/oauth-token.json',
      JSON.stringify(tokens, null, 2)
    );
  }

  async refreshAccessToken() {
    try {
      const { credentials } = await this.oauth2Client.refreshAccessToken();
      this.oauth2Client.setCredentials(credentials);
      await this.saveTokens(credentials);
      return credentials;
    } catch (error) {
      console.error('Failed to refresh token:', error);
      throw error;
    }
  }
}
```

### Usage

```javascript
const tokenManager = new TokenManager();

// Load saved tokens
await tokenManager.loadTokens();

// Tokens will automatically refresh when needed
const gmail = google.gmail({ 
  version: 'v1', 
  auth: tokenManager.oauth2Client 
});
```

---

## Troubleshooting

### Issue: "redirect_uri_mismatch"

**Cause:** Redirect URI doesn't match configured URI in Google Cloud Console

**Solution:**
1. Check exact redirect URI in error message
2. Add it to Authorized redirect URIs in Google Cloud Console
3. Ensure HTTPS in production
4. Check for trailing slashes

### Issue: No Refresh Token Received

**Cause:** User previously authorized app, refresh token only sent on first authorization

**Solution:**
1. Revoke app access: https://myaccount.google.com/permissions
2. Re-authorize with `prompt: 'consent'` parameter
3. Ensure `access_type: 'offline'` is set

### Issue: "invalid_client"

**Cause:** Invalid client ID or secret

**Solution:**
1. Verify `OAUTH_CLIENT_ID` matches Client ID from Google Cloud Console
2. Verify `OAUTH_CLIENT_SECRET` matches Client Secret
3. Check for extra spaces or newlines in credentials

### Issue: "insufficient_permissions"

**Cause:** Missing required scopes

**Solution:**
1. Verify scopes are correctly specified
2. Re-authorize user with updated scopes
3. Check OAuth consent screen has scopes added

### Issue: Tokens Expired

**Cause:** Access token expired and refresh failed

**Solution:**
```javascript
// Implement token refresh logic
try {
  await sendEmail(...);
} catch (error) {
  if (error.code === 401) {
    await tokenManager.refreshAccessToken();
    await sendEmail(...); // Retry
  }
}
```

### Debug Mode

Enable debug logging:

```javascript
oauth2Client.on('tokens', (tokens) => {
  console.log('New tokens received:', {
    access_token: tokens.access_token.substring(0, 20) + '...',
    refresh_token: tokens.refresh_token ? 'Present' : 'Not present',
    expiry_date: new Date(tokens.expiry_date).toISOString()
  });
});
```

---

## Security Best Practices

### 1. Store Tokens Securely

```javascript
// Bad: Store in plain text
await fs.writeFile('tokens.json', JSON.stringify(tokens));

// Good: Encrypt tokens before storing
const encrypted = encrypt(JSON.stringify(tokens), ENCRYPTION_KEY);
await fs.writeFile('tokens.enc', encrypted);
```

### 2. Rotate Secrets Regularly

- Rotate client secrets every 90 days
- Monitor for unauthorized access
- Use different credentials for dev/staging/prod

### 3. Implement Token Expiry Checks

```javascript
function isTokenExpired(token) {
  if (!token.expiry_date) return true;
  return Date.now() >= token.expiry_date;
}

if (isTokenExpired(tokens)) {
  await refreshAccessToken();
}
```

### 4. Limit Scope Requests

Only request scopes you actually need:

```javascript
// Bad: Request all scopes
const scopes = ['https://mail.google.com/']; // Full Gmail access

// Good: Request minimal scopes
const scopes = ['https://www.googleapis.com/auth/gmail.send'];
```

### 5. Monitor API Usage

- Set up usage alerts in Google Cloud Console
- Monitor quota limits
- Implement rate limiting in your application

---

## Additional Resources

- **Gmail API Documentation**: https://developers.google.com/gmail/api
- **OAuth 2.0 Guide**: https://developers.google.com/identity/protocols/oauth2
- **Node.js Quickstart**: https://developers.google.com/gmail/api/quickstart/nodejs
- **API Quotas**: https://developers.google.com/gmail/api/reference/quota

---

## Support

For Gmail OAuth setup assistance:
- **Email**: support@nexus-api.example.com
- **Documentation**: https://docs.nexus-api.example.com/gmail-oauth
- **GitHub Issues**: https://github.com/hannesmitterer/AI-Based-Peace-Platform/issues

---

**Gmail OAuth Setup Guide v1.0.0**  
Last Updated: 2025-11-03
