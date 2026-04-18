# Security Policy

## Reporting a Vulnerability

If you find a security issue:

**Do NOT open a public issue.**

Instead:
1. Email the maintainer directly via GitHub profile contact
2. Or open a private GitHub Security Advisory: https://github.com/trivenigk/flowbridge-job-forwarder/security/advisories/new

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (optional)

You will get a response within 7 days.

## Scope

In scope:
- OAuth token leakage paths
- Secrets accidentally committed
- Dependency vulnerabilities (Selenium, gspread, etc.)
- Container escape paths
- Prompt/SQL injection in any user-input fields

Out of scope:
- WhatsApp ToS issues (known risk, documented)
- Google Cloud quota abuse (per-user account)
- Social engineering targeting users
- Issues in dependencies upstream (report there)

## What We Do With Reports

1. Acknowledge within 7 days
2. Investigate and reproduce
3. Develop a fix
4. Coordinate disclosure (typically 30-90 days)
5. Credit reporter (if desired)

## Safe Harbor

Good-faith security research is welcomed. We will not pursue legal action against researchers who:
- Test only against their own installation
- Do not access other users' data
- Report vulnerabilities responsibly
- Do not extort or threaten

## User Responsibility

FlowBridge is self-hosted. You are responsible for:
- Keeping `credentials.json` and `token.json` secret (never commit)
- Securing your machine running Docker
- Reviewing OAuth scopes you authorize
- Monitoring your Google account for unauthorized access
- Revoking access at https://myaccount.google.com/permissions if compromised

## Known Limitations

- WhatsApp Web automation violates WhatsApp ToS (account ban risk)
- VNC port 5900 exposed by default (bind to localhost only in production)
- Chrome profile in volume contains sensitive session data
- OAuth token cached locally — protect your machine
