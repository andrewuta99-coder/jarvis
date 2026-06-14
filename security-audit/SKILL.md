---
name: jarvis-security-audit
version: 0.1.0
description: |
  Security audit aligned with OWASP Top 10 (2021) + AWS Well-Architected
  Security pillar + Anthropic and Google secure-coding guidance. Checks
  every line for: hardcoded secrets, weak crypto, injection vectors
  (SQL/NoSQL/OS/LLM prompt), broken auth patterns, IAM wildcards,
  Terraform misconfig, public buckets, dependency CVEs, and LLM-specific
  risks (jailbreak resistance, prompt injection, secrets-in-prompts).
  Produces an actionable report with exact line numbers and concrete
  remediation per finding. (jarvis)
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - AskUserQuestion
triggers:
  - jarvis security audit
  - security audit
  - owasp check
  - check for vulnerabilities
  - secret scan
  - threat model
---

# /jarvis-security-audit — OWASP + AWS + LLM threat coverage

## Standards this maps to

- **OWASP Top 10 (2021)**: A01–A10
- **OWASP Top 10 for LLM Applications (2025)**: LLM01 prompt injection,
  LLM02 sensitive info disclosure, LLM04 model DoS, LLM06 excessive
  agency, LLM07 system prompt leakage, LLM08 vector/embedding weaknesses
- **AWS Well-Architected Security Pillar**: identity, detection, infra
  protection, data protection, incident response
- **CIS AWS Foundations Benchmark**: applicable controls
- **NIST SSDF (SP 800-218)** secure-coding practices
- **Anthropic + Google secure-coding**: defense-in-depth, fail-closed,
  trust boundary marking, no secrets in logs, structured error responses

The bin produces findings tagged with the standard(s) they violate, so
you can hand the report directly to a compliance reviewer.

## When to run this

| Trigger | Why |
|---|---|
| Before every PR merge | Pre-landing gate (CI mode: `--strict --since main`) |
| Weekly cron | Drift control + new CVE detection |
| After adding a new feature | Map new attack surface |
| Pre-launch / pre-funding | Investor or customer audit prep |
| After a near-miss incident | Confirm fix + find adjacent gaps |

## How it runs

```bash
~/.claude/skills/jarvis/bin/jarvis-security-audit \
  --target-dir <repo>             # default: cwd
  --since main                    # only changed files
  --aws                           # also scan live AWS (DynamoDB, IAM, S3 hygiene)
  --strict                        # exit 1 on CRITICAL or HIGH
  --output-dir .jarvis/audits/
  --max-files 500
  --json                          # machine-readable
```

The conversational agent (this skill) invokes the bin, then walks the
report with the user.

## What the bin checks

### 1. Hardcoded secrets (CRITICAL when found)

Regex + entropy detection for:
- AWS access keys (`AKIA[0-9A-Z]{16}`), session tokens
- Stripe live + test keys (`sk_live_`, `sk_test_`, `rk_live_`, `whsec_`)
- GitHub tokens (`ghp_`, `gho_`, `ghs_`)
- Anthropic, OpenAI, Google API keys
- Slack tokens (`xox[abp]-`)
- Generic PEM blocks (`-----BEGIN ... PRIVATE KEY-----`)
- JWT secrets (high-entropy strings near `secret`, `key`, `token` words)
- Database connection strings with embedded credentials

False-positive suppression:
- Test fixtures clearly marked (file paths matching `test`, `fixture`,
  `mock`, `example`)
- Placeholders like `xxx`, `your-key-here`, `PLACEHOLDER`, `REPLACE_ME`

### 2. OWASP A01 — Broken Access Control

- DynamoDB queries without `tenantId` scope (tenant isolation breach)
- SQL queries missing `WHERE user_id = ?` filter on user-owned data
- API endpoints with no auth dependency
- Routes that accept user-supplied IDs without ownership check
- IAM policies with `"Resource": "*"` and `"Action": "*"`
- Insecure direct object reference patterns

### 3. OWASP A02 — Cryptographic Failures

- MD5 / SHA-1 used for anything other than non-security checksums
- Passwords NOT hashed with bcrypt/argon2/scrypt
- Weak random: `random.random()` instead of `secrets.SystemRandom`
- Encryption with `ECB` mode
- Hard-coded IV/nonce
- TLS configuration files allowing TLSv1.0/1.1 ciphers
- DynamoDB tables / S3 buckets without `server_side_encryption`
- Secrets stored in plaintext env vars instead of Secrets Manager

### 4. OWASP A03 — Injection

- **SQL**: string-concatenated queries, f-string SQL, `%`-format SQL
- **NoSQL**: `MongoClient.find({...user_input})` without sanitization
- **OS command**: `subprocess.run(...shell=True...)` with user input,
  `os.system(...)` with user input
- **LDAP, XPath, XML**: unparameterized queries
- **SSRF candidate**: `requests.get(user_supplied_url)` without
  allow-list of permitted hosts

### 5. OWASP A04 — Insecure Design

- Missing rate limits on auth endpoints
- Password reset by knowledge of email alone (no verification token)
- Identifiers that leak data ordering (sequential integers exposed in
  URLs — should be opaque IDs)
- No idempotency on charging endpoints (the CloudMortgage 2026-01-11 lesson)

### 6. OWASP A05 — Security Misconfiguration

- `DEBUG = True` in production-shaped code paths
- CORS `allow_origins=["*"]` with `allow_credentials=True`
- Default credentials anywhere
- Disabled CSRF protection
- Verbose error messages returning stack traces to clients
- Public S3 buckets (`block_public_acls = false`)
- VPC security groups with `0.0.0.0/0` ingress on non-public ports
- Root account access keys present

### 7. OWASP A06 — Vulnerable Components

- `requirements.txt` / `package.json` deps with known CVEs (uses `pip-audit`
  or `npm audit` when installed; degrades to a static lockfile check
  otherwise)
- Pinned to known-vulnerable versions
- Unmaintained packages (last release > 2 years)
- Anti-pattern: `pip install` from a URL without hash pinning

### 8. OWASP A07 — Identification & Authentication Failures

- JWT verification missing `algorithms=` arg (algorithm confusion attack)
- Tokens stored in plain `localStorage` without rotation
- Refresh tokens never rotated
- Password complexity checks weaker than NIST SP 800-63B
- No bcrypt cost factor or `< 10`
- Signup verification codes hashed with plain SHA (not HMAC)
- Constant-time comparison missing on token verify

### 9. OWASP A08 — Software/Data Integrity Failures

- `pip install` from untrusted index
- `npm install` without `package-lock.json` integrity field
- Unsigned container images
- CI/CD scripts that `curl ... | bash` without checksum verification
- GitHub Actions using `@latest` instead of pinned SHA

### 10. OWASP A09 — Security Logging & Monitoring

- No CloudWatch alarms on auth failures
- Logs containing PII (`email=`, `phone=`, `ssn=` in log statements)
- Logs containing secrets (`token=`, `password=`, `api_key=` in
  log statements)
- No log retention policy (uncapped CloudWatch costs + compliance issue)
- Missing CloudTrail in production accounts

### 11. OWASP A10 — Server-Side Request Forgery (SSRF)

- HTTP libraries called with user-supplied URLs
- Missing allow-list / deny-list for outbound calls
- Missing timeout
- AWS ECS / EC2: not configured for IMDSv2 only

### 12. LLM Top 10 (Bedrock + Anthropic + OpenAI usage)

- **LLM01 Prompt injection**: user input concatenated directly into
  system prompt; missing instruction hierarchy markers
- **LLM02 Sensitive info disclosure**: model context window logged in
  full; tool-call args logged including arguments containing secrets
- **LLM04 Model DoS**: no max_tokens limit; no per-tenant rate limit
- **LLM06 Excessive agency**: agent has tool access that's broader than
  the user's IAM
- **LLM07 System prompt leakage**: prompt visible in error messages or
  client-side code
- **LLM08 Vector/embedding**: Knowledge Base not scoped per tenant
  (cross-tenant retrieval risk)

### 13. AWS-specific (when `--aws` flag is set)

Uses boto3 to read live state:

- IAM users with access keys older than 90 days
- IAM policies with wildcards in `Action` AND `Resource`
- S3 buckets with public access blocks disabled
- DynamoDB tables without PITR or deletion_protection
- ECR repos without image scanning
- KMS keys with rotation disabled
- Root account without MFA
- Untagged production resources (governance failure)
- VPC default security groups with active rules
- CloudTrail not enabled in any region

## Severity scale

| Severity | Maps to | CI behavior |
|---|---|---|
| **CRITICAL** | Live secret in code, public bucket with PII, SQL injection in production path, root MFA off | Block merge always |
| **HIGH** | OWASP A01–A03 confirmed paths, weak crypto, missing auth on endpoints | Block in `--strict` |
| **MEDIUM** | OWASP A04–A07, verbose errors, deprecated deps | Warn |
| **LOW** | Logging hygiene, missing alarms, governance | Track |

## Report format

```markdown
# Security Audit — {{REPO_NAME}}
Generated: 2026-06-14T12:00:00Z
Standards covered: OWASP Top 10 (2021), OWASP LLM Top 10 (2025), AWS WAF Security Pillar
Score: 82/100 (B)

## Summary
- 1 CRITICAL — live secret in commit history
- 3 HIGH — missing tenant scope in 3 DDB queries
- 8 MEDIUM
- 14 LOW

## CRITICAL

### SEC-C1. AWS access key found in commit
**File**: `scripts/deploy_legacy.sh:23`
**Standard**: A02 (Crypto failures), AWS root account guidance
**Detail**: AKIAIOSFODNN7EXAMPLE matches the AWS access-key pattern.
**Action**: Rotate the key IMMEDIATELY in IAM console.
       Then `git filter-repo` to remove from history.

## HIGH

### SEC-H1. Cross-tenant DynamoDB query
**File**: `real_estate_service/api/cases/routes.py:142`
**Standard**: A01 (Broken Access Control)
**Detail**: `cases_table.query(KeyConditionExpression=Key("caseId").eq(case_id))`
         does not scope by `tenantId`. A user from tenant A who guesses
         a case_id from tenant B will read tenant B's data.
**Fix**: Add `Key("tenantId").eq(user.tenant_id) & Key("caseId").eq(case_id)`.
...
```

## How the agent walks the report

1. Run the bin.
2. **CRITICAL findings**: surface inline; **never** display the actual
   secret value in chat — show file:line + the pattern that matched.
3. For HIGH findings: walk one at a time. Show the offending code,
   propose the fix, ask before applying.
4. For MEDIUM / LOW: summarize counts; offer to file a single tracking
   issue with all of them grouped.
5. End with score + the 1-2 things that would move the score most.

## Anti-patterns the agent must avoid

- **Never print secret values, even partial.** Show file:line + the
  pattern matched.
- **Never auto-fix CRITICAL findings.** Rotating a credential or removing
  from git history is the user's call — Jarvis advises, user acts.
- **Never invent a CVE.** If `pip-audit` isn't installed, the agent says
  "dependency CVE check skipped — install pip-audit for coverage" rather
  than guessing.
- **Tenant isolation findings are not optional.** If the agent finds a
  DDB query without `tenantId`, it must always flag as HIGH minimum.

## Voice

> One CRITICAL: there's an AWS access key in `scripts/deploy_legacy.sh:23`.
> Rotate it now — open the IAM console and click Deactivate, then go.
> I'll wait. After rotation, we'll scrub git history together.
