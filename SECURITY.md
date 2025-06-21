# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

The Scout CLI team takes security vulnerabilities seriously. We appreciate your efforts to responsibly disclose your findings.

### How to Report

Please **DO NOT** file public GitHub issues for security vulnerabilities. Instead, please:

1. **Email**: Send details to security@scout-cli.org
2. **PGP**: Use our PGP key (ID: 1234567890ABCDEF) for sensitive information
3. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

1. **Acknowledgment**: We'll acknowledge receipt within 24 hours
2. **Initial Assessment**: Initial response within 48 hours
3. **Updates**: Regular updates every 72 hours during investigation
4. **Resolution Timeline**: We aim to resolve critical issues within 7 days

### Security Measures

Scout CLI implements several security measures:

- **Input Validation**: All user inputs are validated and sanitized
- **Encrypted Storage**: Sensitive data is encrypted using Fernet
- **Secure Defaults**: Security-first configuration defaults
- **Audit Logging**: Complete activity tracking
- **Rate Limiting**: Built-in API rate limiting
- **Dependency Scanning**: Regular dependency vulnerability scanning

### Security Best Practices

When using Scout CLI:

1. **Keep Updated**: Always use the latest version
2. **Secure Credentials**: Store API keys securely using Scout's secrets management
3. **Network Security**: Run scans from secure networks
4. **Output Security**: Protect scan results and reports
5. **Access Control**: Use role-based access control for teams

### CVE Process

For confirmed vulnerabilities:

1. We'll request a CVE identifier
2. Coordinate disclosure timeline
3. Prepare security patch
4. Notify users through multiple channels
5. Publish security advisory

### Recognition

We maintain a security researchers hall of fame. Researchers who report valid vulnerabilities will be:

- Credited in security advisories (with permission)
- Listed in our acknowledgments
- Eligible for our bug bounty program (when available)

### Contact Information

- **Security Email**: security@scout-cli.org
- **General Support**: support@scout-cli.org
- **Website**: https://scout-cli.org/security

Thank you for helping keep Scout CLI and our users safe!
