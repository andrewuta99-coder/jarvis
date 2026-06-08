# Changelog

## v1.3.0 — 2026-06-08

Launch-ready release. Reference outputs, test suite, CI, launch artifacts.
Bundles v1.1 + v1.2 + v1.3.

### Added (v1.1)
- `templates/starters/ai-saas-cra-fastapi/BUILD_SPEC.example.md` — the
  exact BUILD_SPEC.md that the Architect agent should produce for the
  AI SaaS starter. Lets any LLM reproduce identical output.
- `templates/starters/ai-saas-cra-fastapi/CONSTELLATION.example.json` —
  matching constellation with all 13 specialist agents, full inputs/
  outputs/writes per agent.
- `templates/starters/ai-agent/manifest.yaml` — second starter for
  Bedrock-heavy + Step Functions + GPU-optional agentic apps.
- Pipeline state machine `RunTask` step now wires Subnets, SecurityGroups,
  and TaskDefinition from `terraform_remote_state.networking` +
  `terraform_remote_state.infra` (was a placeholder in v1.0).

### Added (v1.2)
- `test/test_render.py` — 11 tests: slot substitution, template-hash
  stability, manifest parsing (block + inline forms), end-to-end render
  of the real networking feature.
- `test/test_orchestrate.py` — 5 tests for `requires_feature` dependency
  resolver and `merge_outputs` context-merging.
- `test/test_upgrade_migrate.py` — 3 tests for the generated-by header
  parser used by `jarvis-upgrade-migrate`.
- `test/run_tests.sh` — stdlib-only test runner (no pytest needed).
- `scripts/gen-skill-docs` — keeps SKILL.md descriptions in sync with
  feature manifests. `--check` mode for CI.

### Added (v1.3)
- `.github/workflows/test.yml` — CI: unit tests + smoke-renders every
  feature + shellchecks install scripts + verifies SKILL.md sync.
  All inputs hardcoded — no GitHub-event-interpolation injection risk.
- `docs/launch/HN_POST.md` — Show HN draft + 5 pre-written replies for
  common objections.
- `docs/launch/DEMO_SCRIPT.md` — 30-second screencast storyboard, 4
  audience variants (HN/IH/YC/conf).
- `docs/launch/COREY_QUINN_PITCH.md` — Last Week in AWS email pitch.
- `docs/launch/TWITTER_THREAD.md` — 12-tweet thread, one production
  scar per tweet.
- `docs/launch/LAUNCH_CHECKLIST.md` — T-7 / T-1 / T-0 / T+1 / T+7
  launch-day playbook.

### Verified
- 19/19 tests pass on Python 3.14 (using SourceFileLoader workaround for
  extensionless bin scripts).
- All 14 features render cleanly: networking(12), infra(7), data(11),
  backend(20), frontend(25), auth(7), ai(11), email(10), payments(7),
  deploy(4), gpu(9), pipeline(11), rag-langchain(6), rag-langgraph(6).
  124 generated files total per a full render against sample-context.json.

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
