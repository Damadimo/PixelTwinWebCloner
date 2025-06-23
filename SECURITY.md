# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

### How to Report

If you discover a security vulnerability in PixelTwin Website Cloner, please report it responsibly:

1. **DO NOT** open a public GitHub issue for security vulnerabilities
2. Email the maintainers directly (contact information in README)
3. Include as much detail as possible about the vulnerability
4. Allow reasonable time for us to respond and fix the issue

### What to Include

When reporting a security vulnerability, please include:

- **Description** of the vulnerability
- **Steps to reproduce** the issue
- **Potential impact** and severity assessment
- **Suggested fix** (if you have one)
- **Your contact information** for follow-up

### Response Timeline

- **Initial response**: Within 48 hours
- **Status update**: Within 1 week
- **Fix timeline**: Depends on severity (critical issues within days)

## Security Considerations

### API Keys and Sensitive Data

- **Never commit API keys** to the repository
- Use environment variables for all sensitive configuration
- The `.gitignore` is configured to exclude `.env` files
- Regularly rotate your API keys

### Input Validation

- All user-provided URLs are validated and sanitized
- The scraper includes protections against malicious content
- LLM outputs are sanitized to remove potentially harmful scripts

### Network Security

- The application respects robots.txt when possible
- Rate limiting is implemented to prevent abuse
- HTTPS is enforced for all external requests

### Data Privacy

- No user data is stored permanently
- Scraped content is processed in memory only
- API keys are never logged or transmitted

## Safe Usage Guidelines

### For Users

1. **Only clone websites you have permission to clone**
2. **Respect copyright and intellectual property rights**
3. **Be aware of the legal implications** in your jurisdiction
4. **Use responsibly** - don't overwhelm target servers
5. **Keep your API keys secure** and don't share them

### For Developers

1. **Review all dependencies** regularly for vulnerabilities
2. **Validate all inputs** from users and external sources
3. **Follow secure coding practices**
4. **Test security implications** of any changes
5. **Keep dependencies updated**

## Known Security Limitations

### Current Limitations

- **JavaScript execution**: The tool executes JavaScript from scraped sites in a sandboxed environment
- **External resources**: The tool fetches external CSS and images from target sites
- **LLM processing**: User URLs are sent to third-party LLM providers

### Mitigation Strategies

- Playwright runs in a sandboxed, headless environment
- All external requests include proper headers and timeouts
- LLM providers (OpenAI, Anthropic, Google) have their own privacy policies
- No persistent storage of sensitive data

## Responsible Disclosure

We are committed to working with security researchers and the community to keep PixelTwin Website Cloner secure. We appreciate responsible disclosure and will:

1. **Acknowledge** your contribution publicly (if you wish)
2. **Provide updates** on our progress fixing the issue
3. **Credit you** in our security advisories (unless you prefer anonymity)
4. **Work with you** to understand and resolve the issue

## Security Updates

Security updates will be:

- **Released promptly** for critical vulnerabilities
- **Documented** in our changelog and release notes
- **Announced** through GitHub security advisories
- **Backported** to supported versions when applicable

## Contact

For security-related questions or to report vulnerabilities:

- **Security issues**: Create a private security advisory on GitHub
- **General security questions**: Open a GitHub Discussion
- **Urgent security matters**: Contact maintainers directly

---

**Remember**: This tool should be used responsibly and ethically. Always respect website terms of service, copyright laws, and privacy rights. 