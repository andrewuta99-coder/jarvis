# Jarvis

> *"Jarvis, build me a SaaS."*

Jarvis is your AI cloud architect — a multi-specialist agentic scaffold that goes from a blank AWS account to a deployed, production-ready full-stack app in under 30 minutes. Like Tony Stark's lab AI, you describe what you want and a team of specialist sub-agents builds it: networking, infrastructure, data, auth, AI, backend, API, frontend, email, payments, deployment. All in parallel. All AWS-native. No PaaS lock-in.

**MIT licensed. Free forever. Open source.**

## The 10-minute demo

```
$ jarvis init my-saas

? What are you building?
  -> AI SaaS (auth + billing + AI chat + email)
     AI agent (chatbot, document processor)
     Marketplace
     Internal tool
     Custom (interview me)

? Frontend?
  -> React (Create React App on Amplify Hosting)
     React + Vite
     Next.js (SSR on ECS)

? Backend?
  -> FastAPI on ECS Fargate Spot
     Node/Express on ECS Fargate Spot
     Lambda + API Gateway

? Region?  us-east-1

Architect agent -> drafting BUILD_SPEC.md (12 features identified)
Planner agent   -> producing constellation (10 specialists, 4 phases)

Phase 1: Foundation (parallel)
   Networking agent: VPC, subnets, VPC endpoints, ALB     (47s)
   Infra agent:      ECS cluster, ECR, IAM, OIDC          (51s)
   Data agent:       DynamoDB tables                       (44s)

Phase 2: Services (parallel)
   Auth agent:       users table, JWT, signup/login        (38s)
   AI agent:         Bedrock + KB + OpenSearch             (62s)
   API agent:        FastAPI routes + OpenAPI              (55s)
   Frontend agent:   CRA app + auth UI + chat UI           (71s)

Phase 3: Integration (parallel)
   Email agent:      SES + VPC endpoint + bounce SNS       (29s)
   Payments agent:   Stripe + webhook + idempotency        (41s)
   Deploy agent:     GitHub Actions + ECR + Amplify        (38s)

Phase 4: Convergence + Ship
   Contract verification passed
   terraform apply (3m 12s)

YOUR APP IS LIVE
   https://my-saas-12abc.jarvis.app
   Test login: demo@my-saas-12abc.jarvis.app / demo
   Cost projection (idle):     $14/mo
   Cost projection (1k users): $47/mo

Total time: 9m 14s
Total clicks in AWS console: 0
```

Zero clicks in the AWS console. Auth, billing, AI, email — all wired correctly.

## Why Jarvis

You just made an AWS account. You stare at 200 services. You close the tab. You go back to Vercel and accept the lock-in for another year.

Jarvis is the on-ramp. From blank account to live URL with auth + AI + payments, in the time it takes to make coffee. The Terraform we generate is what a senior AWS engineer would write — clean, native, opinionated. You can eject any time and your app keeps running.

**You are not locked in.** `jarvis eject` and we leave. The Terraform, the Dockerfile, the GitHub Actions — they're yours. Use them, modify them, take them anywhere.

## What makes it different

| | Jarvis | Vercel / Render | AWS Amplify | CDK / Pulumi |
|---|---|---|---|---|
| AWS-native | yes | no | yes | yes |
| Full-stack scaffold | yes | partial | partial | no |
| Multi-agent build | yes | no | no | no |
| Production defaults baked in | yes | n/a | no | no |
| No PaaS lock-in | yes | no | mostly no | yes |
| Eject command | yes | n/a | painful | n/a |
| Time to live URL | ~10 min | ~5 min (no backend) | ~30 min if lucky | days |
| Open source, MIT | yes | no | no | yes |

## Architecture in one diagram

```
USER: "build me a SaaS"
   |
   v
ARCHITECT agent   - conversational interview, writes BUILD_SPEC.md
   |
   v
PLANNER agent     - decomposes into specialist tasks, writes CONSTELLATION.json
   |
   v
PARALLEL FAN-OUT (10 specialists work concurrently across 3 phases)
   |
   +-- Networking agent  -> iac/networking
   +-- Infra agent       -> iac/ecs, iac/iam base
   +-- Data agent        -> iac/dynamodb
   +-- Auth agent        -> users, sessions, JWT routes
   +-- AI agent          -> Bedrock, KB, OpenSearch
   +-- Backend agent     -> FastAPI service code
   +-- API agent         -> routes, OpenAPI
   +-- Frontend agent    -> CRA app, components
   +-- Email agent       -> SES + VPC endpoint
   +-- Payments agent    -> Stripe webhook
   +-- Deploy agent      -> GitHub Actions + Amplify Hosting
   |
   v
CONVERGENCE agent  - verifies contracts across all specialists
   |
   v
SHIP agent         - terraform apply, first deploy, smoke test
   |
   v
LIVE URL
```

Each specialist has a contract (inputs from prior phases, outputs to later phases). The Convergence agent enforces the contracts. No specialist can write outside its declared `writes_glob`. This is what makes parallel execution safe.

## Install (one command)

```bash
curl -fsSL https://raw.githubusercontent.com/andrewuta99-coder/jarvis/main/install.sh | bash
```

That's it. The installer clones Jarvis to `~/.claude/skills/jarvis`, runs setup, symlinks skills into Claude Code, and prints next steps. Takes ~10 seconds.

**Other AI agents** (Codex, Cursor, OpenCode, etc.):

```bash
curl -fsSL https://raw.githubusercontent.com/andrewuta99-coder/jarvis/main/install.sh | bash -s -- --host codex
```

Supported: `claude` (default), `codex`, `cursor`, `opencode`, `factory`, `kiro`, `hermes`, `slate`, `gbrain`, `openclaw`.

**Prefer to inspect before running?**

```bash
git clone --depth 1 https://github.com/andrewuta99-coder/jarvis.git ~/.claude/skills/jarvis
cd ~/.claude/skills/jarvis && ./setup
```

## Update (one command)

```bash
/jarvis upgrade
```

Pulls the latest patterns, rebuilds the CLI, and offers to migrate any of your generated Terraform that's improved upstream. Your customizations always win — Jarvis detects which files you've edited and never overwrites them silently.

## The principles

1. **Invisible Rails** — Every production gotcha I've hit is baked in as a silent default. You never type "VPC endpoint" but the endpoint is there.
2. **One Right Way** — A new builder does not need 50 options. Jarvis picks; you override when you want.
3. **Native AWS Always** — The Terraform we write is what a senior AWS engineer would write. No DSLs, no parallel mental models.
4. **No Lock-In** — `jarvis eject` works from day one. We're the on-ramp, not the prison.
5. **Atomic Feature Transactions** — IaC + IAM + VPC + integration test + docs ship together or not at all.

Read [ETHOS.md](ETHOS.md) for the full philosophy. Read [ARCHITECTURE.md](ARCHITECTURE.md) for the design.

## Status

**v0 — Pre-alpha.** Scaffolding complete; specialist agents under active development. First demo target: AI SaaS starter (Create React App + FastAPI + DynamoDB + Bedrock + Stripe + SES on Amplify Hosting). Star and watch the repo for the public launch.

## License

MIT. Free forever. Go build something.
