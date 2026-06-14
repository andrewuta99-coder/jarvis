# Changelog

## v1.7.0 — 2026-06-14

Three new audit + product skills.

### Code Audit (new)

`bin/jarvis-code-audit` + `code-audit/SKILL.md`. Line-by-line review
against Google Style Guides + Anthropic engineering principles.

Detects:
- Static-analysis findings via ruff, mypy, eslint, tsc, terraform fmt,
  shellcheck (graceful skip when a tool is missing — no hard dep)
- God files (> 500 lines), god functions (> 50 lines, cyclomatic > 10),
  god classes (> 12 public methods), long parameter lists (> 5)
- Duplicated 10-line blocks across files (sha1-indexed)
- O(n²) patterns: nested loops over same collection, .find/.includes
  inside .map/.forEach, string concatenation in loops
- Architecture smells: circular imports detection
- Naming/readability: bare `except:`, `: any` in TypeScript, magic numbers,
  missing test files
- Cyclomatic complexity per Python function (AST-based)

Outputs `.jarvis/audits/code-<ISO_DATE>.md` with severity-ranked findings
(CRITICAL / MAJOR / MINOR / NIT) + a 0-100 score. Exits 1 in `--strict`
mode if MAJOR or CRITICAL found.

### Security Audit (new)

`bin/jarvis-security-audit` + `security-audit/SKILL.md`. OWASP Top 10
(2021) + OWASP LLM Top 10 (2025) + AWS Well-Architected Security Pillar.

Detects:
- Hardcoded secrets: AWS keys, Stripe, GitHub, Anthropic, OpenAI, Google,
  Slack tokens, PEM blocks, DB connection strings with creds. Suppresses
  obvious placeholders (`xxx`, `your-key-here`, etc.) and test fixtures.
- A01 Broken Access Control: DynamoDB queries without tenantId scope,
  SQL without WHERE, mutating routes without Depends() auth
- A02 Crypto: MD5/SHA-1 in auth context, weak random for tokens,
  `jwt.decode` without `algorithms=` (algorithm confusion), AES-ECB,
  missing SSE on Terraform
- A03 Injection: f-string SQL, subprocess `shell=True`, `os.system`,
  SSRF candidates with variable URLs
- A05 Misconfig: CORS `*` with credentials, `DEBUG=True`, S3 without
  public_access_block, IAM wildcard Action+Resource, SG with 0.0.0.0/0
  on sensitive ports
- A06 Vulnerable deps: pip-audit when installed (graceful skip)
- A09 Logging hygiene: PII/secrets in formatted log statements
- LLM01 Prompt injection: user input concatenated into system prompts
- LLM04 Model DoS: invoke_model without max_tokens
- LLM08 Vector weakness: Bedrock Retrieve without metadataFilter
- AWS live (with `--aws` flag): root MFA, old IAM access keys,
  S3 public-access-block, DynamoDB PITR

Outputs `.jarvis/audits/security-<ISO_DATE>.md`. Never prints secret
values, even partial. Exits 1 on CRITICAL or (in `--strict`) HIGH.

### Product Manager (new)

`bin/jarvis-pm-spec` + `pm/SKILL.md`. PM copilot for non-technical
product managers.

The skill walks a PM through 5 structured phases (who/why/what →
journey → edge cases → wireframes → engineering translation), producing
**11 markdown files** an engineer can implement directly:

1. Customer journey
2. User stories
3. Acceptance criteria
4. Edge cases (with feature-shape-specific checklists)
5. API contracts (request/response/errors/PM-notes per endpoint)
6. Data model
7. Wireframes (ASCII layouts of every screen)
8. Analytics events
9. Rollout plan (phased + kill switch)
10. PM-to-engineer phrase translation
11. SUMMARY.md (one-page exec summary)

The bin (`jarvis-pm-spec`) supports `init`, `set-meta`, `add-story`,
`add-edge`, `add-api`, `add-event`, `summary`, `list`, `show`. PMs who
like CLI move fast; PMs who don't, just talk to the agent.

Includes a worked example walkthrough for "complete shopping experience
on an ecommerce app" in the SKILL.md so PMs see what the output looks
like before they start.

### Plumbing

- `setup` script's SKILLS array now includes `code-audit security-audit pm`
- Three new bins added: jarvis-code-audit, jarvis-security-audit,
  jarvis-pm-spec
- 19 unit tests still pass

## v1.6.0 — 2026-06-08

Operational maturity release. Bundles v1.4 + v1.5 + v1.6.
20 CLI binaries (was 10 in v1.3), 6 starter manifests (was 2), and a
comprehensive command-reference README. All 19 unit tests pass.

### v1.4 — Community on-ramp

- Three new starter manifests: marketplace, internal-tool, mobile-backend
- CONTRIBUTING.md — what we accept (incident-derived defaults first),
  template contract, local-sandbox testing pattern
- .github/ISSUE_TEMPLATE/bug.yml and incident-default.yml
- .github/PULL_REQUEST_TEMPLATE.md
- bin/jarvis-doctor --fix — interactive remediation. Walks each WARN/FAIL,
  asks before applying (enable PITR, deletion-protection, S3 versioning).
- bin/jarvis-upgrade-migrate --apply — actually writes the patches now.
  Backs up each file before overwriting (in .jarvis/upgrade-backups/<ts>/).

### v1.5 — Extensibility + cross-machine

- ~/.jarvis/specialists/<name>/ — user-defined specialists. The renderer
  resolves user dirs BEFORE built-ins. Same-name overrides built-ins.
- docs/CUSTOM_SPECIALISTS.md — how to write one + override rules.
- bin/jarvis-brain-sync init|status|push|pull — cross-machine memory via
  a user-owned private git repo. Never syncs secrets, AWS access keys,
  env files, .terraform, anything matching secret patterns. Files > 500KB
  skipped automatically.
- bin/jarvis-import — bulk import existing AWS account into Terraform.
  Discovers DynamoDB/S3/ECS/Lambda/Secrets/ECR with --include / --exclude
  fnmatch filters. Always adds prevent_destroy on data-bearing resources.
  Never applies — writes iac/import/*.tf for the user to plan + apply.

### v1.6 — Operational commands + first-run UX

- bin/jarvis-aws-setup — get AWS credentials with three inputs (access key,
  secret, region). Detects existing setup. Optional one-tap billing alarm
  at $50/mo. --sso for Identity Center, --check for CI.
- bin/jarvis-tail — multi-resource CloudWatch tail. Color-codes
  ERROR/WARN/INFO. --filter (CW pattern), --service (filter to one
  feature's logs), --follow (stream live).
- bin/jarvis-debug-vpc — paste a Connect-timeout error, get the fix.
  Parses the AWS service hostname, prints aws-cli one-off + Terraform
  snippet. Covers SES, Bedrock, AOSS, States, SNS, SQS, Lambda, KMS,
  and 10 more services.
- bin/jarvis-debug-iam — paste an AccessDenied error, get an IAM policy
  patch. Parses role + action + resource from the standard AWS error
  shape.
- bin/jarvis-cost — explains your AWS bill in plain English. Annotates
  each Cost Explorer line with what it actually is, recommends cuts
  ranked by savings potential.
- bin/jarvis-canary — post-deploy monitoring loop with auto-rollback.
  Watches health-check + recent error count for a window (default 10min).
  3 consecutive failures → automatic rollback to prior task def.
- bin/jarvis-scale — right-size from 14 days of CloudWatch metrics.
  Applies a decision matrix, prints the Terraform variable change to
  apply. Never auto-applies — capacity changes affect prod.

### Repository hygiene

- Scrubbed all references to external inspiration projects.
- README rewritten as a complete command reference. Every binary,
  every slash-skill, what it does, how to use it, with examples.

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
