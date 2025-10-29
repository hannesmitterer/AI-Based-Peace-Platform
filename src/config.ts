import dotenv from 'dotenv';

dotenv.config();

export const config = {
  port: process.env.PORT || '8080',
  googleClientId: process.env.GOOGLE_CLIENT_ID || '',
  googleIssuers: (process.env.GOOGLE_ISSUERS || 'accounts.google.com,https://accounts.google.com').split(',').map(s => s.trim()),
  seedbringerEmails: (process.env.SEEDBRINGER_EMAILS || '').split(',').map(s => s.trim()).filter(s => s),
  councilEmails: (process.env.COUNCIL_EMAILS || '').split(',').map(s => s.trim()).filter(s => s),
  corsAllowOrigin: process.env.CORS_ALLOW_ORIGIN || '*',
  oracleServiceAccount: process.env.ORACLE_SERVICE_ACCOUNT_RESOURCE || '',
};

// Validate critical configuration
if (!config.googleClientId) {
  console.warn('WARNING: GOOGLE_CLIENT_ID is not set. Authentication will fail.');
}

if (config.seedbringerEmails.length === 0) {
  console.warn('WARNING: SEEDBRINGER_EMAILS is empty. No seedbringer access allowed.');
}

if (config.councilEmails.length === 0) {
  console.warn('WARNING: COUNCIL_EMAILS is empty. No council access allowed.');
}
