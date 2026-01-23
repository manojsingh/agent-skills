# Security Hardening Checklist

A comprehensive security checklist for React + Python applications migrated from .NET.

## Table of Contents

1. [Application Security](#application-security)
2. [Backend API Security](#backend-api-security)
3. [Frontend Security](#frontend-security)
4. [Database Security](#database-security)
5. [Infrastructure Security](#infrastructure-security)
6. [Authentication & Authorization](#authentication--authorization)
7. [Network Security](#network-security)
8. [Monitoring & Incident Response](#monitoring--incident-response)

---

## Application Security

### Code Security

- [ ] **No hardcoded secrets** - Use environment variables or secrets manager
- [ ] **Dependencies up to date** - Run `npm audit` and `pip check` regularly
- [ ] **Security scanning** - Use tools like Snyk, Bandit (Python), ESLint security plugins
- [ ] **Input validation** - Validate all user inputs on both frontend and backend
- [ ] **Output encoding** - Prevent XSS by encoding output
- [ ] **Error handling** - Don't expose stack traces in production
- [ ] **Logging** - Log security events (failed logins, suspicious activity)
- [ ] **Code reviews** - Security-focused code reviews for all changes

### Configuration Security

- [ ] **Debug mode disabled** - `DEBUG=False` in production
- [ ] **Secure session configuration** - HttpOnly, Secure, SameSite cookies
- [ ] **CORS properly configured** - Whitelist specific origins only
- [ ] **Content Security Policy** - Implement CSP headers
- [ ] **Remove unnecessary endpoints** - Disable admin panels, debug routes
- [ ] **Environment separation** - Different configs for dev/staging/prod

---

## Backend API Security

### FastAPI/Flask Security

#### Input Validation

```python
from pydantic import BaseModel, validator, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    
    @validator('username')
    def username_alphanumeric(cls, v):
        assert v.isalnum(), 'Username must be alphanumeric'
        assert len(v) >= 3, 'Username must be at least 3 characters'
        return v
    
    @validator('password')
    def password_strength(cls, v):
        assert len(v) >= 8, 'Password must be at least 8 characters'
        assert any(c.isupper() for c in v), 'Password must contain uppercase'
        assert any(c.islower() for c in v), 'Password must contain lowercase'
        assert any(c.isdigit() for c in v), 'Password must contain digit'
        return v
```

#### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/login")
@limiter.limit("5/minute")
async def login(request: Request):
    # Login logic
    pass
```

#### SQL Injection Prevention

```python
# GOOD - Use parameterized queries
from sqlalchemy import text

query = text("SELECT * FROM users WHERE email = :email")
result = db.execute(query, {"email": user_email})

# BAD - Never do string formatting
# query = f"SELECT * FROM users WHERE email = '{user_email}'"  # VULNERABLE!
```

#### API Security Checklist

- [ ] **Rate limiting** - Prevent brute force and DoS attacks
- [ ] **Request size limits** - Max body size, file upload limits
- [ ] **SQL injection prevention** - Use ORM or parameterized queries
- [ ] **NoSQL injection prevention** - Validate/sanitize inputs
- [ ] **Command injection prevention** - Avoid `os.system()`, use subprocess safely
- [ ] **Path traversal prevention** - Validate file paths
- [ ] **XXE prevention** - Disable external entities in XML parsers
- [ ] **Deserialization attacks** - Avoid `pickle`, use JSON
- [ ] **API versioning** - `/api/v1/` for backward compatibility
- [ ] **HTTPS only** - Redirect HTTP to HTTPS

---

## Frontend Security

### React Security

#### XSS Prevention

```jsx
// GOOD - React automatically escapes
<div>{userInput}</div>

// DANGEROUS - Avoid dangerouslySetInnerHTML
// <div dangerouslySetInnerHTML={{__html: userInput}} />

// If you must use it, sanitize first
import DOMPurify from 'dompurify';
<div dangerouslySetInnerHTML={{__html: DOMPurify.sanitize(userInput)}} />
```

#### Secure Token Storage

```javascript
// BEST - Use httpOnly cookies (set by backend)
// Token stored in cookie, not accessible to JavaScript

// ACCEPTABLE - sessionStorage for SPA
sessionStorage.setItem('token', token);

// AVOID - localStorage (persists across sessions)
// localStorage.setItem('token', token);  // Less secure
```

#### CSRF Protection

```javascript
// Include CSRF token in requests
const response = await fetch('/api/endpoint', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': getCsrfToken(),
  },
  credentials: 'include',
  body: JSON.stringify(data),
});
```

#### Frontend Checklist

- [ ] **XSS prevention** - Sanitize user input, avoid `dangerouslySetInnerHTML`
- [ ] **CSRF tokens** - Include in state-changing requests
- [ ] **Secure token storage** - HttpOnly cookies or sessionStorage
- [ ] **Content Security Policy** - Whitelist script sources
- [ ] **Subresource Integrity** - Use SRI for CDN resources
- [ ] **Dependencies audit** - Run `npm audit fix` regularly
- [ ] **HTTPS only** - Ensure all requests use HTTPS
- [ ] **Disable autocomplete** - For sensitive fields (passwords)
- [ ] **Clickjacking protection** - Use X-Frame-Options or CSP frame-ancestors

---

## Database Security

### PostgreSQL Security

#### Connection Security

```python
# Use SSL for database connections
DATABASE_URL = "postgresql://user:pass@host:5432/db?sslmode=require"

# Or in SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "sslmode": "require",
        "sslcert": "/path/to/client-cert.pem",
        "sslkey": "/path/to/client-key.pem",
        "sslrootcert": "/path/to/ca-cert.pem"
    }
)
```

#### Access Control

```sql
-- Create read-only user for reporting
CREATE ROLE readonly_user WITH LOGIN PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE myapp TO readonly_user;
GRANT USAGE ON SCHEMA public TO readonly_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;

-- Limit app user permissions
REVOKE ALL ON SCHEMA public FROM app_user;
GRANT CONNECT ON DATABASE myapp TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
```

#### Database Checklist

- [ ] **Encrypted connections** - SSL/TLS required
- [ ] **Strong passwords** - 16+ characters, random
- [ ] **Least privilege** - Users have only necessary permissions
- [ ] **Network isolation** - Database in private subnet
- [ ] **Backup encryption** - Encrypt database backups
- [ ] **Audit logging** - Enable query logging for sensitive tables
- [ ] **Regular updates** - Keep database version updated
- [ ] **Sensitive data encryption** - Encrypt PII at rest
- [ ] **No default credentials** - Change all default passwords
- [ ] **Connection pooling** - Limit max connections

---

## Infrastructure Security

### Docker Security

#### Dockerfile Best Practices

```dockerfile
# Use specific versions, not 'latest'
FROM python:3.11-slim

# Run as non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# Don't copy unnecessary files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser . .

# Use read-only filesystem where possible
# docker run --read-only ...

# Scan images for vulnerabilities
# docker scan myimage:latest
```

#### Docker Compose Security

```yaml
services:
  backend:
    # Don't expose ports unnecessarily
    expose:
      - "8000"
    # Set resource limits
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
    # Use secrets instead of environment variables
    secrets:
      - db_password
      - secret_key
    # Run as non-root
    user: "1000:1000"

secrets:
  db_password:
    file: ./secrets/db_password.txt
  secret_key:
    file: ./secrets/secret_key.txt
```

### Infrastructure Checklist

- [ ] **Use official images** - From trusted registries
- [ ] **Scan for vulnerabilities** - Use Docker scan, Trivy, Clair
- [ ] **Run as non-root** - Create and use unprivileged user
- [ ] **Resource limits** - Set CPU and memory limits
- [ ] **Read-only containers** - Where possible
- [ ] **Secrets management** - Use Docker secrets or external vault
- [ ] **Network segmentation** - Use Docker networks
- [ ] **Remove unnecessary packages** - Minimize attack surface
- [ ] **Keep images updated** - Rebuild regularly with latest base images
- [ ] **Sign images** - Use Docker Content Trust

---

## Authentication & Authorization

### JWT Token Security

```python
from datetime import datetime, timedelta
from jose import jwt
import secrets

# Generate strong secret key
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": secrets.token_urlsafe(16),  # JWT ID for revocation
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Check if token is revoked
        if is_token_revoked(payload.get("jti")):
            raise HTTPException(status_code=401, detail="Token revoked")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Password Security

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Add password complexity requirements
def validate_password_strength(password: str):
    if len(password) < 12:
        raise ValueError("Password must be at least 12 characters")
    if not any(c.isupper() for c in password):
        raise ValueError("Password must contain uppercase letter")
    if not any(c.islower() for c in password):
        raise ValueError("Password must contain lowercase letter")
    if not any(c.isdigit() for c in password):
        raise ValueError("Password must contain digit")
    if not any(c in "!@#$%^&*" for c in password):
        raise ValueError("Password must contain special character")
```

### Authentication Checklist

- [ ] **Strong password policy** - Min 12 chars, complexity requirements
- [ ] **Password hashing** - Use bcrypt, scrypt, or argon2
- [ ] **Salt passwords** - Unique salt per password (handled by bcrypt)
- [ ] **JWT best practices** - Short expiry, secure secret key
- [ ] **Refresh tokens** - Separate long-lived refresh tokens
- [ ] **Token revocation** - Ability to invalidate tokens
- [ ] **Multi-factor authentication** - Optional or required MFA
- [ ] **Account lockout** - After N failed login attempts
- [ ] **Password reset** - Secure token-based reset flow
- [ ] **Session management** - Timeout, logout functionality

---

## Network Security

### Nginx Security Headers

```nginx
# nginx.conf security headers
server {
    # ... other config ...
    
    # Prevent clickjacking
    add_header X-Frame-Options "SAMEORIGIN" always;
    
    # Prevent MIME sniffing
    add_header X-Content-Type-Options "nosniff" always;
    
    # Enable XSS protection
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Content Security Policy
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://trusted-cdn.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self' https://api.yourdomain.com; frame-ancestors 'none';" always;
    
    # HSTS - Force HTTPS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    
    # Referrer Policy
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Permissions Policy
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
    
    # Hide Nginx version
    server_tokens off;
}
```

### CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com"
    ],  # Never use "*" in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Be specific
    allow_headers=["Content-Type", "Authorization"],  # Whitelist only needed headers
    max_age=3600,  # Cache preflight requests
)
```

### Network Checklist

- [ ] **HTTPS everywhere** - No HTTP in production
- [ ] **TLS 1.2+** - Disable older protocols
- [ ] **Strong cipher suites** - Modern encryption algorithms
- [ ] **HSTS enabled** - Force HTTPS with preload
- [ ] **Security headers** - CSP, X-Frame-Options, etc.
- [ ] **CORS properly configured** - Whitelist specific origins
- [ ] **Firewall rules** - Allow only necessary ports
- [ ] **VPN/Private network** - For admin access
- [ ] **DDoS protection** - Use CloudFlare, AWS Shield, etc.
- [ ] **WAF** - Web Application Firewall

---

## Monitoring & Incident Response

### Security Monitoring

```python
import logging

# Configure security logger
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.WARNING)

# Log security events
def log_security_event(event_type: str, details: dict):
    security_logger.warning(
        f"Security Event: {event_type}",
        extra={
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            **details
        }
    )

# Examples
log_security_event("failed_login", {
    "username": username,
    "ip_address": request.client.host,
    "user_agent": request.headers.get("user-agent")
})

log_security_event("suspicious_activity", {
    "user_id": user_id,
    "action": "bulk_delete_attempt",
    "count": 1000
})
```

### Monitoring Checklist

- [ ] **Log security events** - Failed logins, unusual activity
- [ ] **Monitor for vulnerabilities** - Automated dependency scanning
- [ ] **Intrusion detection** - Set up IDS/IPS
- [ ] **Anomaly detection** - Alert on unusual patterns
- [ ] **Regular security audits** - Periodic penetration testing
- [ ] **Incident response plan** - Documented procedures
- [ ] **Backup and recovery** - Regular backups, tested restore
- [ ] **Security training** - Team awareness of security practices
- [ ] **Vulnerability disclosure** - Process for reporting issues
- [ ] **Regular updates** - Patch systems promptly

---

## Pre-Production Security Checklist

Before going live, ensure all items are checked:

### Critical (Must Have)

- [ ] All secrets removed from code and configs
- [ ] HTTPS enabled with valid SSL certificate
- [ ] Database connections encrypted
- [ ] Strong passwords on all accounts
- [ ] Security headers configured
- [ ] CORS properly configured (no "*")
- [ ] Rate limiting enabled
- [ ] Input validation implemented
- [ ] SQL injection prevention verified
- [ ] XSS prevention verified
- [ ] Authentication working correctly
- [ ] Debug mode disabled
- [ ] Error messages don't expose sensitive info
- [ ] Backups automated and tested
- [ ] Monitoring and alerting configured

### Important (Should Have)

- [ ] WAF configured
- [ ] DDoS protection enabled
- [ ] Regular security scanning scheduled
- [ ] Log aggregation set up
- [ ] Incident response plan documented
- [ ] MFA enabled for admin accounts
- [ ] Dependency scanning automated
- [ ] Security training completed
- [ ] Penetration testing performed
- [ ] Compliance requirements met (GDPR, HIPAA, etc.)

### Nice to Have

- [ ] Bug bounty program
- [ ] Security audit by third party
- [ ] Advanced threat detection
- [ ] Security champions program
- [ ] Regular security drills

---

## Tools and Resources

### Security Scanning Tools

- **Python**: Bandit, Safety, Snyk
- **JavaScript**: npm audit, Snyk, OWASP Dependency-Check
- **Docker**: Docker Scan, Trivy, Clair
- **SAST**: SonarQube, Checkmarx
- **DAST**: OWASP ZAP, Burp Suite
- **Secrets**: GitGuardian, TruffleHog

### Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [SANS Security Checklist](https://www.sans.org/security-resources/)
- [Mozilla Observatory](https://observatory.mozilla.org/)

---

## Regular Security Maintenance

### Weekly
- [ ] Review security logs
- [ ] Check for suspicious activity
- [ ] Monitor failed login attempts

### Monthly
- [ ] Update dependencies
- [ ] Run security scans
- [ ] Review access controls
- [ ] Check backup integrity

### Quarterly
- [ ] Security training refresher
- [ ] Review and update security policies
- [ ] Penetration testing
- [ ] Access audit (remove unused accounts)

### Annually
- [ ] Third-party security audit
- [ ] Disaster recovery drill
- [ ] Update incident response plan
- [ ] Compliance audit
