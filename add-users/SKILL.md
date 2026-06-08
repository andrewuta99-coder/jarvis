---
name: jarvis-add-users
version: 0.0.1
description: |
  Add authentication to your Jarvis-managed AWS app: DynamoDB users-v2 table
  (composite tenantId+email key), JWT with refresh tokens, bcrypt password
  hashing, signup/login/password-reset/email-verification routes, and the IAM
  policy your ECS task needs. Tenant isolation baked in. Cost: ~$0 idle. (jarvis)
allowed-tools: [Bash, Read, Write, Edit, AskUserQuestion]
triggers:
  - jarvis add users
  - add auth
  - add login
  - add signup
  - i need users
---

# /jarvis-add-users — auth in one command

Adds a complete authentication system. The composite-key pattern (tenantId+email) is the one from CloudMortgage that solved multi-tenant isolation. Constant-time verification and HMAC-based signup codes are baked in — the security hardening from the 2026-01-28 signup-verification rewrite is the default.

## Preamble

```bash
JARVIS_DIR="${JARVIS_DIR:-$HOME/.claude/skills/jarvis}"
[ ! -f .jarvis/profile.json ] && echo "BLOCKED: not a Jarvis project. Run /jarvis-init first." && exit 1
TEMPLATE=$(cat .jarvis/profile.json | python3 -c 'import sys,json;print(json.load(sys.stdin)["template"])')
BACKEND=$(cat .jarvis/profile.json | python3 -c 'import sys,json;print(json.load(sys.stdin)["backend"])')
FRONTEND=$(cat .jarvis/profile.json | python3 -c 'import sys,json;print(json.load(sys.stdin).get("frontend","none"))')
echo "BACKEND: $BACKEND | FRONTEND: $FRONTEND"
[ -d backend/auth ] && echo "ALREADY_INSTALLED: yes"
```

If `ALREADY_INSTALLED: yes`, ask the user: extend the existing auth (e.g., add SSO) or reinstall? Default: extend.

## Cost projection

Print before applying:

> About to add: Auth (DynamoDB users-v2 table + sessions table + JWT routes)
> Cost projection:
>   Idle:        +$0/mo (DynamoDB pay-per-request)
>   1k users:    +$0.50/mo
>   10k users:   +$5/mo
> Proceed?

## Step 1: Spawn the Auth specialist

```
Agent(subagent_type="general-purpose", description="Auth specialist",
      prompt=<rendered from agents/auth/SKILL.md with backend/frontend slots>)
```

The Auth agent's writes_glob covers:
- `iac/dynamodb/users.tf` and `iac/dynamodb/sessions.tf`
- `iac/iam/auth_policy.tf` (attached to the ECS task role)
- `backend/auth/*` (routes, service, JWT utils — language matches user's backend)
- `frontend/src/auth/*` (login/signup/reset pages — framework matches user's frontend)
- `tests/integration/test_auth.py`
- `docs/features/auth.md`

## Step 2: What gets generated (invisible rails)

These defaults ship silently — the user does not have to know to ask for them:

- Users table: composite key (tenantId hash + email range), PITR enabled, `prevent_destroy = true`, encryption at rest with KMS
- Sessions table: TTL on `expires_at`, refresh-token rotation
- Password hashing: bcrypt with cost factor 12
- JWT: 15-minute access tokens + 7-day refresh tokens, secret in Secrets Manager
- Signup verification: HMAC-SHA256 codes (not plain SHA), constant-time verification, rate-limit 3/10min per tenant, TTL 10 minutes
- Tenant isolation: every query scoped by tenantId at the data layer

Each generated file is tagged with a template hash header so `/jarvis-upgrade` can detect and patch updates without overwriting user customizations.

## Step 3: Convergence check

Verify contracts:
- Does the ECS task role's IAM policy include `dynamodb:*` on the new tables?
- Does the backend OpenAPI spec include the new `/auth/*` routes?
- Does the frontend have an auth context provider wired into the app root?

If any contract fails, halt with `DONE_WITH_CONCERNS` and surface the gap.

## Step 4: Integration test

Run `pytest tests/integration/test_auth.py` (or the language-equivalent). The test signs up a user, verifies the code, logs in, refreshes the token. If this passes, the IAM, VPC endpoints, and code are all correctly wired.

## Step 5: Completion report

> Auth installed.
>   - users-v2 table: created, PITR on, prevent_destroy on
>   - sessions table: created, TTL on expires_at
>   - 8 routes added: signup, verify, login, refresh, logout, forgot-password, reset-password, me
>   - JWT secret: stored in Secrets Manager, rotation enabled
>   - Frontend pages: /login, /signup, /reset
>
> Cost added: $0/mo idle, $0.50/mo at 1k users.
> Run /jarvis-deploy to push.

Update `.jarvis/profile.json` to record `features.auth = "0.0.1"`.
