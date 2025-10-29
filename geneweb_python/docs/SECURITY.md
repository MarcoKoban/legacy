# Security Documentation for Geneweb API

## Overview
This API implementation includes comprehensive security measures to protect against common web application vulnerabilities and ensure data privacy, including a **modern JWT-based authentication system**.

## Security Features Implemented

### 1. Authentication & Authorization ⭐ NEW

#### JWT Token-Based Authentication
- **Access Tokens**: Short-lived tokens (30 minutes) for API access
- **Refresh Tokens**: Long-lived tokens (7 days) for token renewal
- **Token Revocation**: JTI-based blacklist mechanism
- **Token Rotation**: Automatic refresh token rotation on use

#### Password Security
- **Hashing Algorithm**: bcrypt with automatic salt generation
- **Cost Factor**: 12 rounds (2^12 = 4096 iterations)
- **Password History**: Prevents password reuse (last 5 passwords)
- **Password Validation**: Minimum strength requirements enforced

#### Session Management
- **Session Tracking**: All active sessions stored in database
- **IP Tracking**: Session IP addresses recorded
- **Automatic Cleanup**: Expired sessions automatically removed
- **Multi-device Support**: Multiple sessions per user allowed

#### Audit Logging
- **Login Events**: All authentication attempts logged
- **Token Events**: Token creation, refresh, and revocation logged
- **Password Changes**: Password modification tracked
- **IP Addresses**: All events include IP address

#### Database Models
- **UserModel**: User accounts with hashed passwords
- **UserSessionModel**: Active user sessions
- **LoginAttemptModel**: Login attempt history
- **PasswordHistoryModel**: Password change history
- **BlacklistedTokenModel**: Revoked tokens

> 📖 **Documentation complète** : [AUTHENTICATION_GUIDE.md](AUTHENTICATION_GUIDE.md)

### 2. HTTPS and Transport Security
- **Forced HTTPS**: All HTTP requests are redirected to HTTPS in production
- **HSTS (HTTP Strict Transport Security)**: Prevents downgrade attacks
  - Max age: 1 year (31,536,000 seconds)
  - Includes subdomains
  - Preload enabled
- **TLS Configuration**: Minimum TLS 1.2, preferred TLS 1.3
- **Certificate Pinning**: Optional HPKP headers for enhanced security

### 3. Security Headers
All responses include security headers:
- **Content-Security-Policy**: Prevents XSS and code injection
- **X-Frame-Options**: Prevents clickjacking (set to DENY)
- **X-Content-Type-Options**: Prevents MIME sniffing attacks
- **X-XSS-Protection**: Browser XSS protection
- **Referrer-Policy**: Controls referrer information leakage
- **Permissions-Policy**: Restricts browser features

### 4. CORS (Cross-Origin Resource Sharing)
- **Restricted Origins**: Only configured Angular frontend domains allowed
- **Credential Support**: Secure cookie handling
- **Method Filtering**: Only necessary HTTP methods allowed
- **Header Controls**: Strict header whitelist

### 5. Rate Limiting and DDoS Protection
- **Request Rate Limiting**: 100 requests per minute per IP (configurable)
- **Burst Protection**: Additional burst limit (20 requests)
- **IP-based Tracking**: Uses sliding window algorithm
- **Whitelist Support**: Internal IPs can bypass limits
- **Request Size Limiting**: Maximum 1MB request size
- **Authentication Rate Limiting**: Special limits for login endpoints

### 6. Input Validation and Sanitization
- **Global Input Validation**: All inputs checked for injection attacks
- **SQL Injection Prevention**: SQLAlchemy ORM + pattern detection
- **XSS Prevention**: HTML/JavaScript injection protection
- **Command Injection Protection**: System command pattern blocking
- **Path Traversal Protection**: Directory traversal prevention
- **Data Sanitization**: Automatic cleaning of dangerous content

### 7. Logging and Monitoring
- **Structured Logging**: JSON-formatted logs with security context
- **Sensitive Data Filtering**: Automatic removal of PII and secrets
- **Security Event Tracking**: Special handling for security-related events
- **Authentication Audit**: Complete audit trail for auth events
- **Log Rotation**: Automatic log file management
- **Prometheus Metrics**: Security metrics collection
- **Grafana Integration**: Security monitoring dashboards

### 8. Secrets Management
- **Environment Variables**: Secure configuration through environment
- **JWT Secrets**: Cryptographically secure secret keys
- **Encryption at Rest**: Secrets encrypted using Fernet (AES 128)
- **Key Derivation**: PBKDF2 with SHA256 for key generation
- **Secure Token Generation**: Cryptographically secure random tokens
- **Password Hashing**: bcrypt with cost factor 12

### 9. Health Checks and Monitoring
- **Secure Health Endpoints**: No sensitive information exposed
- **Authentication Health**: Dedicated `/auth/health` endpoint
- **Internal Monitoring**: Detailed metrics for internal networks only
- **Kubernetes Readiness**: Liveness and readiness probes
- **Performance Monitoring**: Request metrics and timing

### 10. Docker Security
- **Non-root User**: Application runs as non-privileged user
- **Minimal Image**: Alpine-based for reduced attack surface
- **Security Options**: no-new-privileges enabled
- **Resource Limits**: CPU and memory constraints
- **Health Checks**: Container health monitoring

## Configuration Security

### Environment Variables
All sensitive configuration is handled through environment variables:

#### JWT Authentication (REQUIRED)
- `GENEWEB_JWT_SECRET_KEY`: JWT signing key (min 32 chars, 256-bit recommended)
- `GENEWEB_JWT_ALGORITHM`: JWT algorithm (default: HS256)
- `GENEWEB_JWT_ACCESS_TOKEN_EXPIRE_MINUTES`: Access token lifetime (default: 30)
- `GENEWEB_JWT_REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token lifetime (default: 7)

#### Database (REQUIRED for authentication)
- `GENEWEB_DB_DATABASE_URL`: Database connection string
  - Development: `sqlite:///./geneweb.db`
  - Production: `postgresql://user:pass@host:port/db`

#### General Security
- `GENEWEB_SECURITY_SECRET_KEY`: Main application secret (min 32 chars)
- `GENEWEB_SECURITY_ENCRYPTION_KEY`: Data encryption key (min 32 chars)
- `GENEWEB_SECURITY_CORS_ORIGINS`: Allowed frontend domains
- `GENEWEB_API_SSL_CERTFILE`: SSL certificate path
- `GENEWEB_API_SSL_KEYFILE`: SSL private key path

### Production Requirements
1. **SSL Certificates**: Valid SSL certificates required
2. **Strong Secrets**: All secrets must be at least 32 characters (256-bit recommended for JWT)
3. **Database Security**: Use encrypted database connections (PostgreSQL with SSL)
4. **JWT Security**: Unique, random secret key for JWT signing
5. **Token Blacklist**: Use Redis for production token blacklist (not in-memory)
6. **Network Security**: Deploy behind reverse proxy/firewall
7. **Log Security**: Ensure log files have proper permissions

## Compliance and Standards
- **OWASP Top 10**: Protection against all OWASP Top 10 vulnerabilities
- **GDPR Ready**: PII filtering and data protection measures
- **SOC 2**: Logging and monitoring for compliance requirements
- **Security by Design**: Security controls built into architecture

## Monitoring and Alerting
The API provides metrics for:
- Request rates and response times
- Security events (rate limiting, blocked requests)
- Error rates and types
- System health metrics
- Authentication events

## Security Best Practices for Deployment

1. **Use HTTqu'ePS Only**: Never deploy without SSL in production
2. **Firewall Configuration**: Restrict access to necessary ports only
3. **Regular Updates**: Keep dependencies updated for security patches
4. **Monitoring**: Set up alerts for security events
5. **Backup Security**: Encrypt backups and limit access
6. **Network Segmentation**: Isolate API from public networks when possible
7. **Regular Security Audits**: Perform periodic security assessments

## Incident Response
The logging system provides detailed security event tracking for:
- Failed authentication attempts
- Rate limiting violations
- Input validation failures
- Suspicious request patterns
- System errors and exceptions

All security events are logged with sufficient detail for investigation while protecting sensitive data.

## Contact
For security concerns or to report vulnerabilities, please contact the development team through secure channels.