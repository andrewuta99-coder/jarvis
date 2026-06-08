# Changelog

## v1.0.0 — 2026-06-08

First public release. From blank AWS account to deployed full-stack app via
agent constellation. AWS-native, no PaaS lock-in, MIT.

### Headline

- **One-command install** — `curl -fsSL .../install.sh | bash`
- **Multi-agent constellation** — 15 specialist sub-agents (architect, planner,
  networking, infra, data, auth, ai, backend, api, frontend, email, payments,
  deploy, convergence, ship) run in 4 phases (parallel where independent).
- **AI SaaS starter** — CRA + FastAPI + DynamoDB + Bedrock + Stripe + SES on
  Amplify Hosting. The validated CloudMortgage stack as a single command.
- **163 feature template files** covering networking, infra, data, backend,
  frontend, auth, ai, email, payments, deploy, GPU (scale-to-zero EC2 Spot),
  pipeline (Alpamayo Step Functions), RAG-LangChain, RAG-LangGraph.

### Production patterns baked into defaults

Every gotcha from 18 months of CloudMortgage production was encoded as a
silent default that new users benefit from without knowing the failure mode:

- VPC endpoints for SES + Bedrock + AOSS + Step Functions (the 2026-12-22
  connect-timeout class of bugs)
- DynamoDB tables with `prevent_destroy` + `deletion_protection` + PITR
  (the 2026-01-18 data-loss class)
- Bedrock agent IAM with multi-model wildcards (the 2026-01-16 model-swap fix)
- `aoss:BatchGetCollection` on ECS task role (the 2026-01-16 KB-init fix)
- SIGTERM/SIGALRM handlers in backend with 1h hard timeout (the 2026-12-22
  orphan-task class)
- Stripe webhook idempotency middleware (the 2026-01-11 double-charge class)
- HMAC-SHA256 signup codes with constant-time verify (the 2026-01-28 hardening)
- Fargate Spot defaults (~70% off On-Demand)
- ECR lifecycle (keep 10 + expire untagged at 1d)
- S3 KB source lifecycle (IA at 90d, Glacier at 180d)

### What's in this release

- `bin/jarvis-render` — deterministic template renderer, no external deps
- `bin/jarvis-orchestrate` — phase runner with requires_feature dependency
  validation, parallel ThreadPoolExecutor for parallel phases
- `bin/jarvis-validate` — terraform fmt + init -backend=false + validate
  on every rendered module
- `bin/jarvis-upgrade-migrate` — template hash detection for safe upgrades
  (user edits always preserved)
- `bin/jarvis-eject-doc` — generates ARCHITECTURE.md from `.jarvis/profile.json`
- `bin/jarvis-doctor` — live AWS health check (DDB protection, S3 hygiene,
  ECS status, root MFA) via boto3
- 21 user-facing skills: `/jarvis-init`, `/jarvis-add-{users,files,email,ai,
  payments,jobs,realtime,phone,domain}`, `/jarvis-deploy`, `/jarvis-rollback`,
  `/jarvis-doctor`, `/jarvis-cost`, `/jarvis-scale`, `/jarvis-backup`,
  `/jarvis-adopt`, `/jarvis-eject`, `/jarvis-upgrade`, `/jarvis-careful`,
  `/jarvis-freeze`
- 15 specialist agents under `agents/`
- 11 feature template directories
- Cross-host support: claude, codex, cursor, openclaw via `./setup --host <name>`

### Known limitations

- The Architect + Planner agent SKILL.md files describe the prompt patterns
  but final BUILD_SPEC.md and CONSTELLATION.json generation depends on the
  invoking LLM following the prose. v1.1 will ship reference JSON outputs
  per starter template.
- `terraform plan` against a real fresh AWS account has been validated for
  individual modules; end-to-end pipeline run on a fresh sandbox is the
  v1.1 launch demo.
- Pipeline state machine's `RunTask` step has a `REPLACE_WITH_TASK_DEF_ARN`
  placeholder; v1.1 wires this from `terraform_remote_state.infra.outputs`.
