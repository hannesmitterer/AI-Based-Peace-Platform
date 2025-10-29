import dotenv from 'dotenv';

dotenv.config();

export interface Config {
  googleClientId: string;
  googleIssuers: string[];
  seedbringerEmails: string[];
  councilEmails: string[];
  requiredScopesSeedbringer: string[];
  requiredScopesCouncil: string[];
  corsAllowOrigin: string;
  port: number;
}

function parseEmailList(emailString: string | undefined): string[] {
  if (!emailString) return [];
  return emailString.split(',').map(email => email.trim()).filter(email => email.length > 0);
}

function parseScopeList(scopeString: string | undefined): string[] {
  if (!scopeString) return [];
  return scopeString.split(/\s+/).filter(scope => scope.length > 0);
}

function parseIssuerList(issuerString: string | undefined): string[] {
  if (!issuerString) return ['accounts.google.com', 'https://accounts.google.com'];
  return issuerString.split(',').map(issuer => issuer.trim()).filter(issuer => issuer.length > 0);
}

const config: Config = {
  googleClientId: process.env.GOOGLE_CLIENT_ID || '',
  googleIssuers: parseIssuerList(process.env.GOOGLE_ISSUERS),
  seedbringerEmails: parseEmailList(process.env.SEEDBRINGER_EMAILS),
  councilEmails: parseEmailList(process.env.COUNCIL_EMAILS),
  requiredScopesSeedbringer: parseScopeList(process.env.REQUIRED_SCOPES_SEEDBRINGER),
  requiredScopesCouncil: parseScopeList(process.env.REQUIRED_SCOPES_COUNCIL),
  corsAllowOrigin: process.env.CORS_ALLOW_ORIGIN || '*',
  port: parseInt(process.env.PORT || '8080', 10),
};

if (!config.googleClientId) {
  console.warn('WARNING: GOOGLE_CLIENT_ID not set in environment variables');
}

export default config;
