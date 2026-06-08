# Jarvis Milestones

> Living tracker. Update as we ship.

## v0.0.1 — Scaffolding (DONE 2026-06-08)

- [x] Repo structure (61 directories, MIT license)
- [x] Founding docs: README, ARCHITECTURE, ETHOS, CLAUDE.md, LICENSE
- [x] CLI stubs: `bin/jarvis`, `jarvis-config`, `jarvis-update-check`, `jarvis-paths`
- [x] One-command installer: `install.sh` (curl-pipeable)
- [x] `setup` script (multi-host: claude, codex, cursor, opencode, factory, kiro, hermes, slate, gbrain, openclaw)
- [x] Root `SKILL.md` (dispatcher)
- [x] 13 user-facing skills: init, add-{users,files,email,ai,payments,jobs,realtime,phone,domain}, deploy, doctor, eject
- [x] 7 operate/safety skills: rollback, cost, scale, backup, adopt, careful, freeze, jarvis-upgrade
- [x] 14 specialist agent SKILL.md files: architect, planner, networking, infra, data, auth, ai, backend, api, frontend, email, payments, deploy, convergence, ship
- [x] 4 host configs: claude, codex, cursor, openclaw
- [x] AI SaaS starter manifest (`templates/starters/ai-saas-cra-fastapi/manifest.yaml`)
- [x] Templates README
- [x] PRODUCT_PLAN.md committed

## v0.0.2 — Templates filled (next ~1 week)

- [ ] `templates/features/networking/` — VPC, subnets, ALB, VPC endpoints .tf.tmpl files
- [ ] `templates/features/infra/` — ECS cluster, ECR, base IAM, GitHub OIDC
- [ ] `templates/features/data/` — DynamoDB table templates (users-v2, sessions, signup_codes, idempotency, etc.)
- [ ] `templates/features/auth/` — FastAPI auth routes, JWT, bcrypt, HMAC signup
- [ ] `templates/features/ai/` — Bedrock agent + KB + OpenSearch + VPC endpoints
- [ ] `templates/features/email/` — SES + VPC endpoint + bounce SNS + Lambda suppression
- [ ] `templates/features/payments/` — Stripe + webhook + idempotency
- [ ] `templates/features/backend/` — FastAPI skeleton (main, core/dynamodb, core/auth_middleware, signals)
- [ ] `templates/features/frontend/cra/` — CRA React tree with auth/chat/pricing pages

## v0.0.3 — `/jarvis-init` end-to-end

- [ ] `init/SKILL.md` orchestrator implements actual Agent() spawning
- [ ] Phase 1 runs on real AWS sandbox, produces valid Terraform
- [ ] Phase 2-3 wire correctly
- [ ] Ship agent runs terraform apply successfully
- [ ] Smoke test passes against live URL

## v0.0.4 — Demo + launch prep

- [ ] 10-minute demo: blank account → live URL, recorded
- [ ] README polish with demo link
- [ ] HN draft post ready
- [ ] Tweet thread ready
- [ ] Corey Quinn (Last Week in AWS) pitch drafted

## v0.1 — Public launch

- [ ] Push to public repo
- [ ] HN front-page attempt
- [ ] Tweet thread (47 production fixes turned defaults)
- [ ] Indie Hackers / Product Hunt
- [ ] First 10 GitHub stars (lol)
- [ ] First 10 external installs measured

## v0.2 — Template migration system

- [ ] Hash-detect user edits on generated files
- [ ] `/jarvis-upgrade` template migration with PR generation
- [ ] Versioned templates with semver per feature
