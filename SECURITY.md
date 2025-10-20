# Security Policy

## Reporting a Vulnerability

We take the security of this project seriously. If you discover a security vulnerability, please follow these steps:

### 🔒 Private Disclosure

**DO NOT** open a public GitHub issue for security vulnerabilities.

Instead, please report security issues privately:

1. **Email**: Send details to `security@teamwork.net`
2. **Subject**: `[SECURITY] AWS AI Agent Hackathon - <Brief Description>`
3. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### ⏱️ Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity (see below)

### 🎯 Severity Levels

| Severity     | Description                                 | Response Time |
| ------------ | ------------------------------------------- | ------------- |
| **Critical** | Remote code execution, data breach          | 24-48 hours   |
| **High**     | Authentication bypass, privilege escalation | 3-7 days      |
| **Medium**   | Information disclosure, DoS                 | 7-14 days     |
| **Low**      | Minor issues with limited impact            | 14-30 days    |

### 🛡️ Security Best Practices

When using this project:

1. **AWS Credentials**
   - Never commit AWS credentials to the repository
   - Use AWS IAM roles and temporary credentials
   - Rotate credentials regularly
   - Use AWS Secrets Manager for sensitive data

2. **Environment Variables**
   - Store sensitive configuration in `.env` files (gitignored)
   - Use AWS Systems Manager Parameter Store for production
   - Never hardcode API keys or tokens

3. **Dependencies**
   - Keep dependencies up to date
   - Run `uv sync` regularly to update packages
   - Monitor security advisories for Python packages

4. **Deployment**
   - Use least-privilege IAM policies
   - Enable AWS CloudTrail for audit logging
   - Enable AWS GuardDuty for threat detection
   - Use VPC endpoints for AWS services

### 🔍 Security Scanning

This project uses:

- **Gitleaks**: Secret detection in pre-commit hooks
- **Ruff**: Code quality and security linting
- **MyPy**: Type checking to prevent runtime errors
- **Pre-commit hooks**: Automated security checks

### 📋 Supported Versions

| Version              | Supported |
| -------------------- | --------- |
| Latest (main branch) | ✅        |
| Older commits        | ❌        |

### 🏆 Acknowledgments

We appreciate responsible disclosure and will acknowledge security researchers who report valid vulnerabilities (with permission).

### 📜 License

Security fixes will be released under the same AGPL-3.0 license as the project.

---

**Project**: AWS AI Agent Global Hackathon 2025
**Team**: Teamwork Mauritius
**Last Updated**: 2025-10-08
