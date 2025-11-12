# Security Policy

## Overview

ZenMarket AI takes security seriously. This document outlines our security practices, policies, and how to report security vulnerabilities.

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Security Features

### Built-in Security Measures

1. **Paper Trading by Default**
   - The system operates in simulation mode by default
   - Real trading requires explicit configuration
   - Multiple safeguards prevent accidental real trading

2. **API Key Protection**
   - API keys stored in `.env` file (never committed to git)
   - Keys loaded via environment variables
   - `.env` file is in `.gitignore`

3. **Risk Management**
   - Circuit breakers for drawdown limits
   - Position size limits
   - Daily loss limits
   - Maximum open positions limits

4. **Input Validation**
   - All user inputs are validated
   - Type checking with Pydantic models
   - Decimal precision for financial calculations

5. **Dependency Security**
   - Regular security audits with `pip-audit`
   - Static analysis with `bandit`
   - Automated dependency updates via Renovate

## Security Best Practices

### For Users

1. **Protect Your API Keys**
   ```bash
   # Never commit .env files
   echo ".env" >> .gitignore

   # Use strong, unique API keys
   # Rotate keys regularly
   ```

2. **Start with Paper Trading**
   ```bash
   # Always test in simulation mode first
   python -m src.cli simulate --symbol AAPL
   ```

3. **Review Risk Limits**
   ```python
   # config/risk_limits.json
   {
       "max_position_size_pct": 0.20,
       "max_risk_per_trade_pct": 0.01,
       "max_daily_drawdown_pct": 0.05
   }
   ```

4. **Keep Software Updated**
   ```bash
   # Regular updates
   git pull origin main
   pip install -e ".[dev]"
   ```

5. **Monitor Logs**
   ```bash
   # Review logs regularly
   tail -f logs/zenmarket.log
   ```

### For Developers

1. **Code Security**
   - Run `bandit` before committing
   - Use type hints for better validation
   - Validate all external inputs
   - Never log sensitive data (API keys, tokens)

2. **Dependency Management**
   ```bash
   # Audit dependencies
   make audit

   # Update dependencies
   pip-audit
   pip list --outdated
   ```

3. **Secrets Management**
   - Never hardcode secrets
   - Use environment variables
   - Document required variables in `.env.example`

4. **Testing**
   - Mock external APIs in tests
   - Test error paths and edge cases
   - Include security-focused test cases

## Reporting a Vulnerability

We take all security vulnerabilities seriously. If you discover a security issue, please report it responsibly.

### How to Report

**DO NOT** create a public GitHub issue for security vulnerabilities.

Instead, please email us at:
📧 **security@technatool.com**

### What to Include

Please provide:

1. **Description**: Clear description of the vulnerability
2. **Impact**: What could an attacker accomplish?
3. **Steps to Reproduce**: Detailed steps to reproduce the issue
4. **Proof of Concept**: Code or commands demonstrating the vulnerability (if applicable)
5. **Suggested Fix**: If you have ideas for fixing the issue
6. **Your Contact Info**: How we can reach you for follow-up

### Example Report

```
Subject: Security Vulnerability: SQL Injection in Query Builder

Description:
The query builder in src/data/database.py does not properly sanitize
user input, potentially allowing SQL injection attacks.

Impact:
An attacker could execute arbitrary SQL queries, potentially accessing
or modifying sensitive data.

Steps to Reproduce:
1. Navigate to the query builder interface
2. Input the following string: ...
3. Observe the resulting SQL query: ...

Proof of Concept:
[Code demonstrating the vulnerability]

Suggested Fix:
Use parameterized queries instead of string concatenation.

Contact:
[Your email]
```

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Resolution**: Within 30 days (for critical issues)
- **Public Disclosure**: After patch is released

### Disclosure Policy

1. **Coordinated Disclosure**: We prefer coordinated disclosure
2. **Embargo Period**: Typically 90 days after initial report
3. **Credit**: We credit security researchers (unless anonymous)
4. **CVE Assignment**: We'll assign CVEs for significant vulnerabilities

## Security Updates

### How We Notify Users

1. **GitHub Security Advisories**
   - Posted to repository security tab
   - Subscribers notified automatically

2. **Release Notes**
   - Security fixes noted in CHANGELOG.md
   - Tagged with `[SECURITY]` prefix

3. **Email**
   - Critical issues emailed to known users
   - Subscribe at security@technatool.com

### Update Process

```bash
# Check for security updates
git fetch origin
git log --oneline --grep="SECURITY"

# Update to latest secure version
git pull origin main
pip install -e ".[dev]"

# Verify update
python -c "import src; print(src.__version__)"
```

## Known Limitations

### Current Scope

ZenMarket AI is designed for:
- ✅ Educational purposes
- ✅ Paper trading / simulation
- ✅ Personal use backtesting
- ✅ Research and development

### NOT Designed For

- ❌ Production algorithmic trading without additional safeguards
- ❌ Handling of large-scale real funds without proper review
- ❌ Compliance with financial regulations (user responsibility)
- ❌ High-frequency trading

### User Responsibilities

1. **Regulatory Compliance**: Users are responsible for compliance with local regulations
2. **Risk Management**: Additional safeguards may be needed for real trading
3. **Testing**: Thorough testing required before any real trading
4. **Monitoring**: Active monitoring of any live trading systems

## Security Checklist

Before using ZenMarket AI in any trading capacity:

- [ ] All dependencies are up to date
- [ ] Security audit passed (`make audit`)
- [ ] API keys are properly secured
- [ ] Risk limits are configured appropriately
- [ ] System tested thoroughly in simulation mode
- [ ] Monitoring and alerting in place
- [ ] Backup and recovery procedures established
- [ ] Legal and regulatory requirements understood
- [ ] Emergency stop procedures documented

## External Security Tools

We use the following tools for security:

- **bandit**: Python security linter
- **pip-audit**: Vulnerability scanner for Python packages
- **ruff**: Includes security-focused lint rules
- **pre-commit**: Automated security checks
- **Dependabot/Renovate**: Automated dependency updates

## Additional Resources

- [OWASP Python Security](https://owasp.org/www-project-python-security/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)
- [CWE/SANS Top 25 Most Dangerous Software Errors](https://cwe.mitre.org/top25/)

## Contact

- 📧 Security Issues: security@technatool.com
- 📧 General Contact: contact@technatool.com
- 🐛 Bug Reports: [GitHub Issues](https://github.com/TechNatool/zenmarket-ai/issues) (non-security)

## Acknowledgments

We thank the security research community for responsible disclosure and
helping keep ZenMarket AI secure.

Security researchers who have helped:
- [List will be updated as reports are received and resolved]

---

**Last Updated**: 2025-01-12
**Version**: 1.0.0
