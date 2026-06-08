# Jarvis Product Plan

> The founding plan, frozen at v0. Future revisions tracked in git history.

## One-line promise

> *From `jarvis init` to a live URL with auth, AI, and payments in under 30 minutes. AWS-native. No PaaS lock-in. Open source. MIT.*

## Target user

A developer who just made an AWS account and wants to ship a full-stack app. NOT the AWS veteran with scars — the brand-new builder staring at 200 services. Most likely came from Vercel and hit the wall (Bedrock isn't on Vercel).

## The Magic Moment (the demo)

Empty AWS account + `jarvis init my-saas` -> live URL with auth, AI chat, Stripe checkout, email — in under 10 minutes. Zero clicks in the AWS console.

## Multi-agent constellation

A single Claude Code session writing all the infra sequentially would take 40+ minutes. Jarvis decomposes the work into 10-15 specialist sub-agents that run in parallel across 4 phases. Each finishes their slice; the Convergence agent verifies contracts; the Ship agent runs `terraform apply`.

```
PHASE 1 (foundation, parallel):   networking + infra + data
PHASE 2 (services, parallel):     auth + ai + backend + frontend + api
PHASE 3 (integration, parallel):  email + payments + deploy
PHASE 4 (sequential):             convergence + ship
```

Architect interviews. Planner decomposes. Specialists build. Convergence verifies. Ship deploys.

## Five architectural commitments

1. **Templates over LLM codegen.** Deterministic generation. Templates encode the 47 CloudMortgage incidents as silent defaults.
2. **Atomic Feature Transactions.** Every feature ships IaC + IAM + VPC + test + docs together.
3. **Native AWS, always.** No DSLs. Generated artifacts are vanilla Terraform a senior engineer would recognize.
4. **Eject must always work.** `jarvis eject` removes Jarvis state; the app keeps running.
5. **Cost-priced at every step.** Every command shows projected $/month before applying.

## Five principles (ETHOS)

1. **Invisible Rails** — Production gotchas become silent defaults.
2. **One Right Way** — New users don't benefit from 50 options.
3. **Native AWS Always** — Recognizable to any senior AWS engineer.
4. **No Lock-In** — `jarvis eject` is the trust contract.
5. **Cheap by Default** — VPC endpoints over NAT, Fargate Spot over On-Demand, etc.

## Distribution

**Launch artifact**: 30-second screencast. Empty account -> live URL. No voiceover. End card: "AWS-native. No lock-in. MIT. github.com/andrewuta99-coder/jarvis"

**Channels**:
1. HN front page — "I open-sourced create-next-app for a full AWS stack"
2. Twitter: Vercel vs Jarvis comparison
3. Y Combinator distribution
4. Last Week in AWS / Corey Quinn pitch
5. AI Twitter (Bedrock angle)
6. AWS re:Invent submission

## Roadmap

### v0 (3 weeks): Demo-able alpha
- Repo + setup + install.sh scaffolded -- DONE
- 14 specialist agents written as SKILL.md -- DONE
- 13 user-facing skills written -- DONE
- 4 host configs (claude, codex, cursor, openclaw) -- DONE
- AI SaaS starter scaffolded -- DONE
- Templates filled for AI SaaS path (auth, ai, payments, email) -- NEXT
- `/jarvis-init` runs Phase 1 end-to-end on real AWS -- NEXT
- 30-second demo recorded -- LAUNCH GATE

### v1 (3 months)
- Conductor integration (specialists in git worktrees)
- 4 more starters (AI Agent, Marketplace, Internal Tool, Mobile Backend)
- Template auto-migration with hash-detected user-edit detection
- Native ChatGPT custom GPT
- OpenClaw native methodology skills
- All 10 host configs

### v2 (6 months)
- ACP-based specialist spawning (model-tier optimization)
- Compliance modes (SOC 2 / HIPAA / FedRAMP)
- Multi-account / multi-region
- Hosted dashboard (monetization layer — CLI stays MIT free)

### v3 (year 2)
- Second cloud (Cloudflare Workers + R2 + D1)
- Multi-cloud constellation

## Risks (top 3)

| Risk | Mitigation |
|---|---|
| AWS trademark on "Jarvis" (Marvel) | Accept risk for v0-v1, rebrand if pressured. Jasper precedent: $1.5B company rebranded fine. |
| Template auto-migration corrupts user code | Hash-detect user edits. User code always wins. Migration is opt-in via PR. |
| Cost model wrong -> user bill shock | Conservative estimates (50% pad). Hard ceiling at init. Budget alerts default on. |

## What we deliberately do not build (yet)

- Multi-cloud (v3+)
- GUI dashboard (later, monetization layer)
- Custom DSL (never — Terraform is the artifact)
- Multi-tenant SaaS at v0
- A "debug 47 things" surface — incident knowledge encoded as defaults, not as debug commands

## Status (2026-06-08)

v0 scaffolding committed. Next milestone: fill in `templates/features/auth/`, `templates/features/ai/`, `templates/features/payments/`, `templates/features/email/` with concrete .tmpl files so /jarvis-init can run end-to-end on a real AWS account.
