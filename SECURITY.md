# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Currently supported versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of ShadowOps Digest seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Please do NOT:

- Open a public GitHub issue
- Disclose the vulnerability publicly before it has been addressed

### Please DO:

1. Email details to: [security@example.com] (replace with your actual security contact)
2. Include the following information:
   - Type of vulnerability
   - Full paths of source file(s) related to the vulnerability
   - Location of the affected source code (tag/branch/commit or direct URL)
   - Step-by-step instructions to reproduce the issue
   - Proof-of-concept or exploit code (if possible)
   - Impact of the issue, including how an attacker might exploit it

### What to expect:

- We will acknowledge receipt of your vulnerability report within 48 hours
- We will send a more detailed response within 7 days indicating next steps
- We will work with you to understand and resolve the issue promptly
- We will notify you when the vulnerability is fixed
- We will credit you in the security advisory (unless you prefer to remain anonymous)

## Security Best Practices

When using ShadowOps Digest:

1. **API Keys**: Never commit API keys or secrets to the repository
   - Use environment variables for all sensitive data
   - Keep your `.env` file secure and never share it
   - Rotate API keys regularly

2. **Dependencies**: Keep dependencies up to date
   - Regularly run `npm audit` for frontend dependencies
   - Use `pip-audit` or similar tools for Python dependencies
   - Review and update dependencies monthly

3. **Docker**: Follow container security best practices
   - Don't run containers as root
   - Use official base images
   - Scan images for vulnerabilities

4. **Database**: Secure your database
   - Use strong passwords
   - Limit network access
   - Enable SSL/TLS for connections
   - Regular backups

5. **CORS**: Configure CORS appropriately for production
   - Don't use wildcard origins in production
   - Specify exact allowed origins

## Known Security Considerations

- This application uses OpenAI API which sends ticket data externally
- Ensure compliance with your organization's data handling policies
- Consider data anonymization for sensitive ticket information
- Review and configure CORS settings before production deployment

## Security Updates

Security updates will be released as patch versions and announced via:
- GitHub Security Advisories
- Release notes
- Project README

Thank you for helping keep ShadowOps Digest secure!
