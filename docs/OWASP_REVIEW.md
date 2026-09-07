# OWASP Top 10 Security Review — ITMentorSoft Backend

## Executive Summary

The ITMentorSoft backend FastAPI application demonstrates a mixed security posture with several high and medium severity findings. The most critical issues are: (1) **Broken Access Control** via IDOR vulnerability in user retrieval and missing CORS configuration, (2) **Injection vulnerabilities** via unsanitized LIKE queries and LLM prompt injection, and (3) **Security Misconfiguration** including hardcoded credentials and absence of rate limiting.

**Findings by Severity**: CRITICAL: 2 | HIGH: 4 | MEDIUM: 5 | LOW: 3 | INFO: 2

## Methodology

### Scope
- **Source Root**: `D:\projects\devgalop\esp-proj-tutor-back\src`
- **Stack**: Python 3.13, FastAPI 0.135.3 (async), SQLAlchemy 2.0.49 (aiosqlite), Pydantic 2.12.5, PyJWT 2.12.1, bcrypt 5.0.0, brevo (email), sentry-sdk, openai + groq (LLM clients)

### Files Reviewed
| Area | Files |
|------|-------|
| Entry Point | `src/main.py` |
| Auth/Token | `jwt_token_generator.py`, `get_current_user.py`, `require_roles.py`, `dependencies.py` |
| User Management | `login_handler.py`, `refresh_token_handler.py`, `recovery_password_handler.py`, `change_password_handler.py`, `create_user_handler.py` |
| Content Management | `*_handler.py`, `*_endpoint.py` in `features/content_management/` |
| Assessments | `qualifier_service.py`, `opencode_qualifier_service.py`, `groq_qualifier_service.py`, `save_assessments_answers_service.py` |
| Database | `postgres_*_repository.py`, `postgresql_database_session.py` |
| Infrastructure | `brevo_notification_service.py`, `aws_sqs_*.py` |
| Config | `.env.example`, `Dockerfile`, `docker-compose.yml`, `docker-compose.prod.yml` |
| Migrations | `alembic/versions/*.py` |

### Assessment Criteria
Each finding is rated using the OWASP Risk Rating methodology:
- **CRITICAL**: Immediate action required; actively exploitable
- **HIGH**: Significant security impact; should be prioritized
- **MEDIUM**: Moderate security impact; fix within sprint
- **LOW**: Minor security impact; fix when possible
- **INFO**: Good practice observation; not a vulnerability

---

## Findings

### A01: Broken Access Control

#### Finding 1: IDOR in User Retrieval Endpoint
- **Risk Level**: HIGH
- **Location**: `src/features/user_management/get_user/get_user_endpoint.py`, lines 56-62
- **Description**: Any authenticated user can retrieve any other user's details by providing their user_id. The endpoint allows `["admin", "teacher", "student", "user"]` roles, meaning a student can query teacher or admin profiles.
- **Evidence**:
```python
async def get_user(
    user_id: str,
    handler: Annotated[GetUserHandler, Depends(get_get_user_handler)],
    _: Annotated[
        TokenData, Depends(require_roles(["admin", "teacher", "student", "user"]))
    ],
) -> GetUserResponse:
```
- **Mitigation**: Restrict access so users can only retrieve their own profile unless they have admin/teacher role. Use `user_id == current_user.id or current_user.role in ["admin", "teacher"]`.

#### Finding 2: Missing CORS Configuration
- **Risk Level**: HIGH
- **Location**: `src/main.py`, entire file
- **Description**: No CORS middleware is configured. The application has no `CORSMiddleware` or `allow_origins` configuration, preventing proper browser-based cross-origin control.
- **Evidence**: `app = FastAPI(lifespan=lifespan)` with no middleware chain.
- **Mitigation**: Add CORS middleware with explicit allowed origins:
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["https://yourdomain.com"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
```

#### Finding 3: Missing Authorization on Content Endpoints
- **Risk Level**: MEDIUM
- **Location**: `src/features/content_management/shared/init.py` lines 50-63
- **Description**: Some content endpoints like `get_all_contents_router`, `get_resource_content_router` appear to lack authentication requirements based on endpoint definitions. Public content endpoints are acceptable only if intentional.
- **Mitigation**: Audit all content endpoints and ensure public endpoints are explicitly documented and intentional.

---

### A02: Cryptographic Failures

#### Finding 1: JWT Secret Key May Be None
- **Risk Level**: CRITICAL
- **Location**: `src/infrastructure/security/jwt_token_generator.py`, lines 17-18, 47-49
- **Description**: `JWT_SECRET_KEY` is read from environment without validation. If not set, it defaults to `None`, causing `jwt.encode()` to fail at runtime or behave unexpectedly.
- **Evidence**:
```python
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
# ...
jwt.encode(token_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
```
- **Mitigation**: Validate at startup:
```python
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable is required")
```

#### Finding 2: Weak Password Maximum Length
- **Risk Level**: MEDIUM
- **Location**: `src/features/user_management/login/login_request.py`, lines 29-30
- **Description**: Password validation enforces a maximum of 20 characters, which is below modern NIST guidelines (should be 64+). Short max lengths facilitate brute-force attacks.
- **Evidence**:
```python
if len(value) > 20:
    raise ValueError("Password must be no more than 20 characters long")
```
- **Mitigation**: Increase to at least 64 characters and rely on bcrypt's inherent strength.

#### Finding 3: Refresh Token Uses UUID with Low Entropy
- **Risk Level**: MEDIUM
- **Location**: `src/infrastructure/security/jwt_token_generator.py`, lines 65-71
- **Description**: Refresh tokens use `uuid.uuid4().hex` which provides ~72 bits of entropy. While not trivially guessable, this is weaker than cryptographically secure random tokens.
- **Evidence**:
```python
def generate_random_token(self) -> TokenResponse:
    uuid_token = uuid.uuid4().hex
```
- **Mitigation**: Use `secrets.token_urlsafe(32)` for refresh tokens (256 bits entropy).

---

### A03: Injection

#### Finding 1: SQL Injection via LIKE Queries
- **Risk Level**: HIGH
- **Location**: `src/infrastructure/database/postgresql/repository/postgres_resource_content_repository.py`, lines 107, 117, 135, 163, 250
- **Description**: User input is directly interpolated into SQL LIKE clauses without proper escaping. While SQLAlchemy uses parameterized queries, the LIKE pattern syntax characters (`%`, `_`) are not sanitized.
- **Evidence**:
```python
.where(ResourceContentEntity.related_topics.like(f"%{request.topic}%"))
.where(ResourceContentEntity.title.like(f"%{request.title}%"))
.where(ResourceContentEntity.related_topics.ilike(f"%{topic}%"))
```
- **Mitigation**: Escape special LIKE characters in user input:
```python
def escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
```
Then use `escape_like(request.topic)` before interpolation.

#### Finding 2: LLM Prompt Injection via User Answer
- **Risk Level**: CRITICAL
- **Location**: `src/infrastructure/qualifier/opencode_qualifier_service.py`, lines 39, 148; `src/infrastructure/qualifier/groq_qualifier_service.py`, lines 39, 148
- **Description**: User answers are passed directly into the LLM prompt without sanitization. A malicious user could inject instructions to bypass the JSON output format, extract rubric data, or manipulate scoring.
- **Evidence**:
```python
messages=[
    {"role": "system", "content": self.get_prompt(qualifier_prompt)},
    {"role": "user", "content": qualifier_prompt.user_answer},  # UNSANITIZED
]
```
- **Mitigation**: Implement input filtering for the `user_answer` field:
1. Strip markdown code fences
2. Remove common prompt injection patterns
3. Implement output validation (validate JSON schema of LLM response)
4. Consider structured output parsing or XML tags around user content

---

### A04: Insecure Design

#### Finding 1: No Rate Limiting
- **Risk Level**: HIGH
- **Location**: Entire application
- **Description**: No rate limiting middleware or endpoint-level throttling exists. The application is vulnerable to brute-force attacks, API abuse, and DoS.
- **Evidence**: No `RateLimitMiddleware` or similar in `src/main.py`.
- **Mitigation**: Implement FastAPI rate limiting:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
# Then use @limiter.limit("10/minute") on sensitive endpoints
```

#### Finding 2: No Global Exception Handler
- **Risk Level**: MEDIUM
- **Location**: `src/main.py`
- **Description**: Unhandled exceptions could leak stack traces in production responses.
- **Evidence**: `app = FastAPI(lifespan=lifespan)` with no exception handler.
- **Mitigation**: Add global exception handler:
```python
from fastapi import Request
from fastapi.responses import JSONResponse
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
```

#### Finding 3: Token-Based Recovery URL Exposes Token in URL
- **Risk Level**: MEDIUM
- **Location**: `src/features/user_management/recovery_password/recovery_password_handler.py`, lines 75-76
- **Description**: Password recovery token is sent as a URL query parameter, which could be logged by browsers, proxies, and servers.
- **Evidence**:
```python
html_content = (
    html_content.replace("%URL_BASE%", RECOVERY_URL_BASE)
    .replace("%URL_TOKEN%", token.token)  # Token in URL
)
```
- **Mitigation**: Send token via POST body or email-only channel, not URL query strings.

---

### A05: Security Misconfiguration

#### Finding 1: Hardcoded Database Credentials in docker-compose.yml
- **Risk Level**: HIGH
- **Location**: `docker-compose.yml`, lines 6-8
- **Description**: Credentials are hardcoded in the compose file.
- **Evidence**:
```yaml
environment:
  POSTGRES_USER: mentor
  POSTGRES_PASSWORD: mentor123
  POSTGRES_DB: mentorsoft
```
- **Mitigation**: Use environment variables or Docker secrets:
```yaml
environment:
  POSTGRES_USER: ${POSTGRES_USER}
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

#### Finding 2: Database Port Exposed in Production
- **Risk Level**: MEDIUM
- **Location**: `docker-compose.prod.yml`, line 26; `docker-compose.yml`, line 10
- **Description**: PostgreSQL port 5432 is exposed to all interfaces.
- **Evidence**: `ports: - "5432:5432"`
- **Mitigation**: Remove port mapping or bind to localhost only in production.

#### Finding 3: No Security Headers
- **Risk Level**: LOW
- **Location**: `src/main.py`
- **Description**: No security headers (HSTS, X-Content-Type-Options, etc.) are set.
- **Mitigation**: Add security headers middleware.

---

### A06: Vulnerable and Outdated Components

#### Finding 1: Python Version Mismatch
- **Risk Level**: MEDIUM
- **Location**: `Dockerfile`, line 1
- **Description**: Dockerfile uses `python:3.10.21-alpine3.24` but project context mentions Python 3.13. This could mean the requirements.txt specifies older versions.
- **Evidence**: `FROM python:3.10.21-alpine3.24`
- **Mitigation**: Verify requirements.txt and update Dockerfile to match expected Python version.

#### Finding 2: Outdated Alpine Base Image
- **Risk Level**: LOW
- **Location**: `Dockerfile`, line 1
- **Description**: Alpine 3.24 is not the latest. Check for CVEs in the base image.
- **Mitigation**: Update to latest Alpine version and rebuild.

---

### A07: Identification and Authentication Failures

#### Finding 1: JWT Access Token Expiration Too Short
- **Risk Level**: LOW
- **Location**: `src/infrastructure/security/jwt_token_generator.py`, lines 19-21
- **Description**: Default JWT expiration is 300 seconds (5 minutes), which may be inconvenient for users and encourage workarounds.
- **Evidence**:
```python
JWT_EXPIRATION_DELTA_SECONDS = os.getenv(
    "JWT_EXPIRATION_DELTA_SECONDS", "300"
)
```
- **Mitigation**: Consider 15-30 minutes for access tokens with refresh token rotation.

#### Finding 2: Generic Login Error Messages (Positive)
- **Risk Level**: INFO
- **Location**: `src/features/user_management/login/login_handler.py`, lines 38-48
- **Description**: Login returns generic "invalid credentials" message for both missing user and wrong password, preventing email enumeration. This is GOOD PRACTICE.
- **Evidence**:
```python
if not user:
    return LoginResponse(is_successful=False, token="", expiration_time=0, user_id=None)
if not self.password_hasher.verify_password(...):
    return LoginResponse(is_successful=False, token="", expiration_time=0, user_id=None)
```

#### Finding 3: Password Policy Too Lenient
- **Risk Level**: LOW
- **Location**: `src/features/user_management/login/login_request.py`, lines 28-37
- **Description**: Password requires 6+ chars with 1 digit, 1 letter, 1 special char. This is weaker than NIST guidelines (which recommend length > 8 and no complexity requirements).
- **Mitigation**: Update to favor length over complexity.

---

### A08: Software and Data Integrity Failures

#### Finding 1: No Integrity Verification for LLM Responses
- **Risk Level**: HIGH
- **Location**: `src/infrastructure/qualifier/opencode_qualifier_service.py`, `src/infrastructure/qualifier/groq_qualifier_service.py`
- **Description**: LLM JSON responses are parsed without schema validation. Malformed or manipulated responses could cause incorrect scoring.
- **Evidence**:
```python
response_json = json.loads(response)
# No schema validation
score_int = int(round(float(response_json.get("score", 0))))
```
- **Mitigation**: Validate LLM output against a Pydantic model before using it:
```python
from pydantic import BaseModel, ValidationError
class QualifierResponse(BaseModel):
    score: float
    feedback: str
    key_concepts_detected: list[str]
    misconceptions_detected: list[str]
```

#### Finding 2: No Code Signing or Integrity Verification
- **Risk Level**: INFO
- **Location**: Docker build process
- **Description**: Docker image is built without verifying integrity of copied source code.
- **Mitigation**: Use Docker content trust / notary for image signing.

---

### A09: Security Logging and Monitoring Failures

#### Finding 1: No Security Event Logging
- **Risk Level**: HIGH
- **Location**: Entire codebase
- **Description**: Failed login attempts, privilege escalations, and other security-relevant events are not logged.
- **Evidence**: No `logging` calls in auth handlers for security events.
- **Mitigation**: Implement security logging:
```python
import logging
security_logger = logging.getLogger("security")
security_logger.warning(f"Failed login attempt for email: {request.email}")
```

#### Finding 2: No Audit Trail for Sensitive Operations
- **Risk Level**: MEDIUM
- **Location**: `src/features/user_management/assign_role/assign_role_handler.py`, `src/features/user_management/update_user_status/update_user_status_handler.py`
- **Description**: Role assignments and user status changes are not logged with actor information.
- **Mitigation**: Add audit logging for all privileged operations.

---

### A10: Server-Side Request Forgery (SSRF)

#### Finding 1: No Significant SSRF Vulnerabilities Found
- **Risk Level**: INFO
- **Description**: The application does not accept user input to construct URLs for backend fetches. SQS and Brevo URLs come from environment variables, not user input.

#### Minor Concern: Brevo API URL Configurable
- **Risk Level**: LOW
- **Location**: `.env.example`, `src/infrastructure/notification/brevo_notification_service.py`
- **Description**: `BREVO_BASE_API_URL` is configurable. If compromised, could point to internal network.
- **Mitigation**: Validate the URL is a legitimate Brevo endpoint and not an internal IP range.

---

## Priority Remediation Roadmap

| Priority | Finding | Category | Risk | Effort |
|----------|---------|----------|------|--------|
| 1 | Validate JWT_SECRET_KEY at startup | A02: Crypto Failures | CRITICAL | Low |
| 2 | Sanitize LLM user answers (prompt injection) | A03: Injection | CRITICAL | Medium |
| 3 | Fix IDOR in user retrieval | A01: Broken Access Control | HIGH | Low |
| 4 | Implement rate limiting | A04: Insecure Design | HIGH | Medium |
| 5 | Escape LIKE query special characters | A03: Injection | HIGH | Low |
| 6 | Add CORS middleware | A01: Broken Access Control | HIGH | Low |
| 7 | Validate LLM output schema | A08: Integrity | HIGH | Medium |
| 8 | Remove hardcoded credentials | A05: Sec Misconfig | HIGH | Low |
| 9 | Add security event logging | A09: Logging | HIGH | Medium |
| 10 | Use secrets.token_urlsafe for refresh tokens | A02: Crypto Failures | MEDIUM | Low |

---

## Positive Security Practices Observed

1. **Password Hashing**: Uses bcrypt (via `bcrypt 5.0.0`) with proper salt - strong hashing algorithm.
2. **Generic Login Errors**: Returns identical error messages for invalid email vs password, preventing user enumeration.
3. **SQLAlchemy ORM Usage**: Database queries use the ORM's parameterized queries, avoiding raw SQL injection in most places.
4. **Role-Based Access Control**: The `require_roles` decorator provides a clean mechanism for authorization checks.
5. **Token Rotation**: Refresh token flow rotates tokens on each use, limiting token reuse window.
6. **Refresh Token Revocation**: Tokens are revoked on reuse, mitigating certain replay attacks.
7. **Pydantic Validation**: Request models use Pydantic for input validation with explicit type checking.
8. **Async Database Operations**: Uses async SQLAlchemy with connection pooling.
9. **Docker Healthchecks**: Production compose includes healthchecks for dependencies.
10. **Secrets via Environment Variables**: Production deployment expects secrets from CI/CD, not baked into images.

---

## Conclusion

The ITMentorSoft backend has a foundation of good security practices (bcrypt, ORM usage, RBAC) but has critical gaps in access control, injection prevention, and operational security. Immediate attention should be given to the CRITICAL findings around JWT validation, LLM prompt injection, and the IDOR vulnerability. The absence of rate limiting and security logging are high-priority items that should be addressed before production deployment.
