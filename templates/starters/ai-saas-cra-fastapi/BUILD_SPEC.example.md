# BUILD_SPEC (reference output for the AI SaaS — CRA + FastAPI starter)

This is the exact `.jarvis/BUILD_SPEC.md` that the Architect agent
produces for this starter. Any LLM following `agents/architect/SKILL.md`
against this starter's manifest should produce this same shape.

## App

- **Name**: {{APP_NAME}}              (from init interview)
- **Template**: ai-saas-cra-fastapi
- **Frontend**: cra                   (Create React App on Amplify Hosting)
- **Backend**: fastapi                (FastAPI on ECS Fargate Spot)
- **Region**: {{REGION}}              (defaults us-east-1)
- **Account**: {{ACCOUNT_ID}}

## Features

| Feature   | Phase | Description |
|-----------|-------|-------------|
| networking | 1 (foundation) | VPC, 3 private + 2 public subnets, ALB with HTTPS, VPC endpoints |
| infra      | 1 (foundation) | ECS cluster (Fargate Spot), ECR, IAM, GitHub OIDC, Terraform backend |
| data       | 1 (foundation) | DynamoDB tables: users-v2, sessions, signup_codes, chat_threads, chat_messages, customers, subscriptions, idempotency, email_suppression |
| auth       | 2 (services)   | JWT routes (signup/verify/login/refresh/forgot/reset/me), bcrypt, HMAC signup codes |
| ai         | 2 (services)   | Bedrock agent + Knowledge Base + OpenSearch Serverless, chat routes |
| backend    | 2 (services)   | FastAPI skeleton (signals, core/dynamodb, secrets, auth_middleware), ECS task def, service |
| frontend   | 2 (services)   | CRA app with Login/Signup/Dashboard/Chat pages, Tailwind, secureTokenStorage, ThemeContext |
| email      | 3 (integration) | SES sender + DKIM + bounce/complaint SNS + Lambda suppression |
| payments   | 3 (integration) | Stripe customer + subscription + webhook + idempotency middleware |
| deploy     | 3 (integration) | GitHub Actions OIDC deploy + Amplify Hosting branch |

## AWS resources

| Service | Count | Why |
|---|---|---|
| VPC + subnets | 1 + 5 | Private app, public ALB |
| ALB | 1 | HTTPS termination |
| ACM cert | 1 | Wildcard subdomain |
| VPC endpoints | 10 | S3 + DDB (gateway) + Logs/STS/Secrets/ECR-api/ECR-dkr/SES/Bedrock×2/AOSS (interface) |
| ECS cluster | 1 | Fargate Spot capacity provider default |
| ECR repo | 1 | 10-image lifecycle |
| DynamoDB tables | 9 | PITR + deletion_protection + prevent_destroy on every one |
| Bedrock agent | 1 | Multi-model IAM wildcard |
| Bedrock KB | 1 | Linked to OpenSearch + S3 source |
| OpenSearch Serverless | 1 vector collection | ~$50/mo minimum |
| SES identity | 1 + DKIM + bounce/complaint | Per-tenant DKIM keys |
| Secrets Manager | 4+ | JWT, HMAC, Stripe, GitHub-OIDC scoped |
| Amplify Hosting | 1 | Auto-deploy on push to main |
| GitHub Actions OIDC | 1 role | No long-lived AWS keys in CI |

## Cost projection

| | Idle | At 1k users |
|---|---|---|
| VPC endpoints (10 × 2 AZ × $0.01/hr) | $146/mo | $146/mo |
| OpenSearch Serverless minimum | $50/mo | $50/mo |
| ECS Fargate Spot | $4.50/mo | $20/mo |
| DynamoDB pay-per-request | $0 | $1-3/mo |
| SES | $0 | $0 (under 62k free tier) |
| CloudWatch + Secrets Manager | $2.40/mo | $5/mo |
| **Total** | **~$203/mo** | **~$225/mo** |

(Excludes Bedrock invocation per-chat cost (~$0.005 each on Nova Lite),
Stripe transaction fees, Amplify build minutes — all usage-based.)

## Risk callouts

1. **Bedrock model access** — Nova + Claude must be enabled in the
   AWS Console (one-time per region). The `/jarvis-add-ai` skill links
   the right console URL.
2. **SES sandbox mode** — accounts start sandboxed; can only email
   verified addresses. Production access request takes 24-48 hours.
   `/jarvis-add-email` walks through the request.
3. **OpenSearch minimum spend** — $50/mo idle baseline. If KB isn't
   needed, the user can omit the `ai` feature and drop idle cost to
   ~$160/mo.
4. **VPC endpoint cost** — $146/mo for 10 interface endpoints across
   2 AZs. The alternative (NAT Gateway) is $65/mo + data transfer for
   the same outcome. Endpoints win on data-transfer cost above ~50GB/mo.
