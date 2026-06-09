# Jarvis

> *"Jarvis, build me a SaaS."*

From a blank AWS account to a deployed, production-ready full-stack app in
under 10 minutes. Multi-agent constellation. AWS-native Terraform. No PaaS
lock-in. MIT.

```bash
curl -fsSL https://raw.githubusercontent.com/andrewuta99-coder/jarvis/main/install.sh | bash
```

---

## Table of contents

- [Install](#install)
- [First-time setup — AWS credentials](#first-time-setup--aws-credentials)
- [The 5-minute first run](#the-5-minute-first-run)
- [Command reference](#command-reference) — every command, what it does, how to use it
- [Six starter templates](#six-starter-templates)
- [Eleven feature templates](#eleven-feature-templates)
- [Architecture in one diagram](#architecture-in-one-diagram)
- [Five principles](#five-principles)
- [Update + uninstall](#update--uninstall)
- [Status & roadmap](#status--roadmap)

---

## Install

**One command. Takes ~10 seconds.**

```bash
curl -fsSL https://raw.githubusercontent.com/andrewuta99-coder/jarvis/main/install.sh | bash
```

This clones Jarvis into `~/.claude/skills/jarvis`, symlinks every skill
into Claude Code, and prints next steps. Re-running it updates an
existing install in place.

**Other AI agents:**

```bash
# Codex CLI / Cursor / OpenClaw / OpenCode / Factory / Kiro / Hermes / Slate / GBrain
curl -fsSL https://raw.githubusercontent.com/andrewuta99-coder/jarvis/main/install.sh \
  | bash -s -- --host codex
```

**Prefer to inspect before running?**

```bash
git clone --depth 1 https://github.com/andrewuta99-coder/jarvis.git ~/.claude/skills/jarvis
cd ~/.claude/skills/jarvis && ./setup
```

---

## First-time setup — AWS credentials

After install, get AWS credentials configured with **three inputs**:

```bash
jarvis-aws-setup
```

What it does in order, no extra questions:

1. Checks the AWS CLI is installed (prints the install one-liner if not).
2. Tests `aws sts get-caller-identity`. If creds already work, exits clean.
3. If creds don't work, asks for the **three** things needed:
   - AWS Access Key ID
   - AWS Secret Access Key (masked input)
   - Default region (suggests `us-east-1`)
4. Writes to `~/.aws/credentials` + `~/.aws/config` with mode 0600.
5. Re-tests. On success, offers a **single yes/no**: set a $50/mo
   billing alarm so you never wake up to a surprise bill.

If you use AWS Identity Center (SSO):

```bash
jarvis-aws-setup --sso        # walks through `aws configure sso`
```

---

## The 5-minute first run

```bash
$ jarvis init my-saas

? What are you building?
  > AI SaaS (auth + billing + AI chat + email)        recommended
    AI agent (chatbot, document processor)
    Marketplace (two-sided + Stripe Connect)
    Internal tool (SSO-ready)
    Mobile backend (push + 90d refresh tokens)
    Custom (interview me)

? Frontend?      React (CRA + Amplify Hosting)        recommended
? Backend?       FastAPI on ECS Fargate Spot           recommended
? Region?        us-east-1                              recommended

Architect agent  drafting BUILD_SPEC.md
Planner agent    producing CONSTELLATION.json (10 specialists, 4 phases)

Phase 1: Foundation (parallel — ~50s)
   ok  networking   VPC + subnets + ALB + VPC endpoints
   ok  infra        ECS cluster (Fargate Spot) + ECR + IAM + GitHub OIDC
   ok  data         9 DynamoDB tables (PITR + prevent_destroy on every one)

Phase 2: Services (parallel — ~70s)
   ok  auth         JWT routes, HMAC signup codes, constant-time verify
   ok  ai           Bedrock agent + KB + OpenSearch Serverless
   ok  backend      FastAPI + SIGTERM handlers + ECS task def
   ok  frontend     CRA + Tailwind + secureTokenStorage + ErrorBoundary

Phase 3: Integration (parallel — ~40s)
   ok  email        SES + VPC endpoint + bounce SNS + Lambda suppression
   ok  payments     Stripe + webhook + @idempotency middleware
   ok  deploy       GitHub Actions OIDC + Amplify Hosting

Phase 4: Ship (sequential — ~3 min)
   ok  convergence  all 47 contracts verified
   ok  ship         terraform apply succeeded

YOUR APP IS LIVE
   https://my-saas-12abc.jarvis.app
   demo@my-saas-12abc.jarvis.app / demo
   Idle cost: $14/mo     At 1k MAU: $47/mo
   AWS console clicks: 0
```

---

## Command reference

Every command Jarvis ships. Each is a Python script under `bin/` you
can also call directly, or a slash-skill that Claude Code (Cursor / etc.)
invokes through the agent surface.

### `jarvis-aws-setup` — configure AWS credentials

Get the AWS CLI working with the **minimum questions** (3 inputs).
Detects existing setup, walks you through Access Key entry, optionally
adds a billing alarm. See [First-time setup](#first-time-setup--aws-credentials).

```bash
jarvis-aws-setup              # interactive, smart-detect
jarvis-aws-setup --check      # exit 0 if creds work, 1 otherwise
jarvis-aws-setup --sso        # use Identity Center instead of access keys
jarvis-aws-setup --profile myapp   # write under a non-default profile
```

### `/jarvis init` — bootstrap a new app

The 10-minute magic moment. 4 questions, then 4 parallel phases of
specialist agents build everything: VPC → ECS → DynamoDB → auth → AI →
backend → frontend → email → payments → deploy. Ends with a live URL.

```bash
/jarvis init <app-name>                 # interactive in Claude Code
jarvis init my-saas --starter ai-saas-cra-fastapi --region us-east-1
```

### `/jarvis-add-<feature>` — add one feature to an existing app

11 feature commands, one per capability. Each one is an atomic transaction:
IaC + IAM + VPC + integration test + docs ship in one commit. The
Convergence agent refuses to merge incomplete features.

| Command | Adds |
|---|---|
| `/jarvis-add-users` | DynamoDB users-v2 table + JWT routes + bcrypt + HMAC signup codes + constant-time verify + tenant isolation |
| `/jarvis-add-files` | S3 bucket (public-block + versioning + KMS) + presigned-URL routes + frontend upload widget |
| `/jarvis-add-email` | SES verified sender + DKIM + VPC endpoint + bounce/complaint SNS + Lambda suppression list |
| `/jarvis-add-ai` | Bedrock agent + Knowledge Base + OpenSearch Serverless + multi-model IAM wildcard + chat routes |
| `/jarvis-add-payments` | Stripe customer + subscription + webhook + `@idempotency` decorator + Secrets Manager |
| `/jarvis-add-jobs` | SQS + ECS worker (or Step Functions for multi-step) + SIGTERM handlers + DLQ + idempotency |
| `/jarvis-add-realtime` | API Gateway WebSockets + DDB connections table + broadcast helper + React hook |
| `/jarvis-add-phone` | Amazon Connect + inbound flow + AI screening Lambda + transcription |
| `/jarvis-add-domain` | Route53 + ACM cert + ALB HTTPS listener + HTTP→HTTPS redirect + Amplify custom domain |

### `/jarvis-deploy` — build, push, deploy

Build the Docker image for linux/amd64, push to ECR, register a new ECS
task definition, rolling deploy with healthcheck, auto-rollback on
failure. Same proven pattern as CloudMortgage's `deploy.sh`.

```bash
/jarvis-deploy                  # in Claude Code
./scripts/deploy.sh             # equivalent direct invocation
```

### `/jarvis-rollback` — revert to previous deploy

One command back to the previous ECS task definition. Reads
`.jarvis/deploys.jsonl` to find the prior revision and force-deploys it.

### `/jarvis-doctor` — live health check

Reads `.jarvis/profile.json` + queries real AWS via boto3. Checks
DynamoDB protection, S3 hygiene, ECS service health, root account MFA.
Encouraging tone — surfaces warnings, not 47-point interrogations.

```bash
jarvis-doctor --target-dir .                # report
jarvis-doctor --target-dir . --json         # machine-readable
jarvis-doctor --target-dir . --fix          # interactive remediation
```

`--fix` walks each WARN/FAIL and asks for confirmation before applying
a fix (e.g., "Enable PITR on `my-saas-users-v2`? [y/N]").

### `/jarvis-study` — subsystem-scoped briefing

Pairs with `/jarvis-doctor`. Doctor answers *"what's wrong?"*; study
answers *"what is?"* — for one slice of the app, ready-for-work.

Run it before any focused task ("add a tier to membership management",
"extend the leads engine") and a sub-agent walks a 9-layer discovery
recipe — project orientation, code surface, data, infra, cross-cutting
concerns, conventions, past-incident gotchas (mined from CLAUDE.md),
recent activity, and **touch-point synthesis** (the file:line list of
what to modify for the most common feature changes).

```bash
/jarvis-study membership management   # produce or load brief
/jarvis-study --refresh leads engine  # force regenerate
/jarvis-study --list                  # enumerate cached briefs
/jarvis-study                         # list briefs and prompt for topic
```

Briefs cache to `.jarvis/subsystems/<slug>.md`. Auto-refreshes when any
file in scope changes (file-mtime based). When AWS credentials are
available, IaC claims are verified against live state — drift is
surfaced explicitly, not hidden.

Output to the terminal is a TL;DR + section index + 10-line cheatsheet;
the full brief stays in the file so it doesn't blow up your context.

### `/jarvis-cost` — explain your AWS bill

Pulls Cost Explorer for the current month, breaks down by service,
annotates each line with **what it actually is** ("$50 — OpenSearch
Serverless minimum, your KB vector index"), recommends cuts.

```bash
jarvis-cost                    # current month
jarvis-cost --month 2026-05    # specific month
jarvis-cost --forecast         # project end-of-month from MTD
jarvis-cost --json             # machine-readable
```

### `/jarvis-scale` — right-size from real metrics

Reads 14 days of CloudWatch CPU + memory + latency. Applies a decision
matrix, recommends a new task size, prints the Terraform variable
change to apply. Never auto-applies — capacity changes affect prod.

```bash
jarvis-scale                   # 14-day window
jarvis-scale --window 7d       # narrower window
```

### `/jarvis-canary` — post-deploy monitoring

Watches your live app for a configurable window after a deploy. If the
health-check fails or errors spike, **rolls back automatically**.

```bash
jarvis-canary                            # 10-min window, rollback on
jarvis-canary --window 30m               # longer watch
jarvis-canary --no-rollback              # alert only
jarvis-canary --error-threshold 10       # tolerate more errors
```

### `/jarvis-tail` — multi-resource CloudWatch tail

Tails every log group your app writes to (ECS, Lambdas, API Gateway).
Color-codes ERROR (red), WARN (yellow), INFO (dim).

```bash
jarvis-tail                              # last 10 minutes
jarvis-tail --since 30m                  # custom window
jarvis-tail --follow                     # stream new events
jarvis-tail --filter "ERROR"             # CloudWatch filter pattern
jarvis-tail --service auth               # only log groups containing -auth
```

### `/jarvis-debug-vpc` — fix VPC endpoint timeouts

Paste a `Connect timeout on endpoint URL: ...` error. The tool parses
the AWS service, prints the one-off `aws ec2 create-vpc-endpoint`
command **and** the Terraform snippet to make the fix permanent.

```bash
echo "Connect timeout on endpoint URL: email.us-east-1.amazonaws.com" \
  | jarvis-debug-vpc
```

### `/jarvis-debug-iam` — fix AccessDenied errors

Paste an IAM `AccessDenied` error. The tool extracts role + action +
resource, prints the minimum IAM statement to unblock it (both as
`aws-cli` one-off and as Terraform).

```bash
echo "User: arn:aws:sts::123:assumed-role/my-task is not authorized to perform: bedrock:InvokeModel on resource: arn:..." \
  | jarvis-debug-iam
```

### `/jarvis-backup` — verify recoverability

Audits PITR on every DynamoDB table, versioning on every S3 bucket,
rotation on Secrets Manager. Read-only check; opt-in fixes via
`--fix`.

### `/jarvis-adopt` — import existing AWS

Layered on top of `jarvis-import`. Walks an existing AWS account,
generates Terraform with import blocks for everything, applies
`prevent_destroy` to data-bearing resources.

### `jarvis-import` — bulk import to Terraform

Direct invocation of the brownfield import. Scans DynamoDB / S3 / ECS
/ Lambda / Secrets / ECR. Writes `iac/import/*.tf` files. Never applies
— you run `terraform plan + apply` yourself.

```bash
jarvis-import --target-dir . --region us-east-1
jarvis-import --target-dir . --include 'cloudmortgage-*'
jarvis-import --target-dir . --exclude 'test-*' --dry-run
```

### `/jarvis-eject` — leave cleanly

Generates a complete `ARCHITECTURE.md` capturing what was set up + why
+ all the production-defaults the team must keep, then removes
`.jarvis/`. Your Terraform, code, IAM, and deploy pipeline stay. Run
this any time — the promise is that leaving always works.

### `/jarvis-upgrade` — update to latest

Pulls the latest Jarvis, rebuilds the CLI, then **detects which of your
generated files you've edited** (template-hash compare) and patches only
the unedited ones. Backups go to `.jarvis/upgrade-backups/<ts>/`.

```bash
jarvis-upgrade-migrate --target-dir . --apply
```

### `jarvis-brain-sync` — cross-machine memory

Push per-project Jarvis state (profile, learnings, deploys) to a
**user-owned private git repo** so your memory follows you across
laptops. Defense-in-depth: never syncs secrets, AWS keys, env vars,
files >500KB, or anything outside `.jarvis/`.

```bash
jarvis-brain-sync init git@github.com:you/jarvis-brain.git    # one-time
jarvis-brain-sync status                                       # preview
jarvis-brain-sync push                                         # sync this project
jarvis-brain-sync pull                                         # pull on new laptop
```

### `/jarvis-careful` — destructive-command guard

Warns before any destructive AWS or Terraform operation: `terraform
destroy`, ECS delete-service, DynamoDB delete-table, `git push --force`.
User overrides each warning explicitly.

### `/jarvis-freeze` — scope-lock editing

Restricts file edits to one directory for the rest of the session.
Prevents the agent from "helpfully" editing unrelated code while
you're debugging a feature.

### Internal binaries (you usually don't call these)

| Bin | Used by |
|---|---|
| `jarvis-render` | called by `init` and every `add-*` skill to render templates with slot substitution |
| `jarvis-orchestrate` | called by `init` to run constellation phases in parallel + merge agent outputs |
| `jarvis-validate` | called by Convergence agent to run `terraform fmt + init + validate` on every module before Ship |
| `jarvis-eject-doc` | called by `eject` to generate ARCHITECTURE.md from `.jarvis/profile.json` |
| `jarvis-upgrade-migrate` | called by `upgrade` to safely patch unedited generated files |
| `jarvis-config` | get/set `~/.jarvis/config.yaml` entries |
| `jarvis-paths` | emit shell exports for Jarvis paths |
| `jarvis-update-check` | throttled check for upstream version newer than current |

---

## Six starter templates

| Starter | Idle cost | At 1k users | Pick when |
|---|---|---|---|
| **AI SaaS** (CRA + FastAPI) | $200/mo | $225/mo | Default. User-facing SaaS with auth + AI chat + Stripe |
| **AI Agent** | $195/mo | $280/mo | Heavy AI: Step Functions + Bedrock agent + optional GPU |
| **Marketplace** | $215/mo | $245/mo | Two-sided platform, Stripe Connect for split payments |
| **Internal Tool** | $165/mo | $185/mo | Employee dashboard, SSO-ready, no public auth |
| **Mobile Backend** | $210/mo | $245/mo | iOS/Android push, 90d refresh tokens, no consumer web UI |
| **Bare bones** | $90/mo | $90/mo | Just VPC + ECS + DynamoDB; you write the app |

---

## Eleven feature templates

Composable. Each writes only to its declared `writes_glob` — no overlap
with any other feature.

| Feature | What ships |
|---|---|
| networking | VPC, 3 private + 2 public subnets, ALB+HTTPS, security groups, **10 VPC endpoints** |
| infra | ECS cluster (**Fargate Spot default**), ECR (10-image lifecycle), IAM roles, GitHub OIDC, Terraform backend |
| data | DynamoDB tables with **PITR + deletion_protection + prevent_destroy + ignore_changes** on every one |
| backend | FastAPI with SIGTERM/SIGALRM handlers, tenant middleware, structured logs, moto-backed tests |
| frontend | CRA + Tailwind + secureTokenStorage (sessionStorage default) + ThemeContext + ErrorBoundary |
| auth | JWT (15min access / 7d refresh with rotation), bcrypt, **HMAC-SHA256 + constant-time** signup verify |
| ai | Bedrock agent + KB + OpenSearch Serverless, **multi-model IAM wildcard** (swap models w/o IAM redeploy) |
| email | SES + DKIM + **`com.amazonaws.{region}.email` VPC endpoint** + bounce/complaint Lambda |
| payments | Stripe customer + subscription + webhook + **`@idempotency` middleware** (no double-charges) |
| deploy | GitHub Actions **OIDC** (no AWS keys in CI) + Amplify Hosting + local deploy.sh |
| gpu | **Scale-to-zero EC2 Spot ASG** (min=0, max=2) for occasional GPU workloads — $0/hr idle |
| pipeline | Step Functions + S3 inbox/claimed/done/failed protocol + 5 Lambda orchestrators |
| rag-langchain | LangChain LCEL chain over Bedrock (alternative to default `invoke_agent`) |
| rag-langgraph | LangGraph state machine with DynamoDB checkpointer (when reasoning needs explicit state) |

**Custom specialists** — drop your own at `~/.jarvis/specialists/<name>/` and
Jarvis picks them up alongside the built-ins. See
[`docs/CUSTOM_SPECIALISTS.md`](docs/CUSTOM_SPECIALISTS.md).

---

## Architecture in one diagram

```
USER: "build me a SaaS"
   ↓
ARCHITECT agent   — 4-question interview, writes BUILD_SPEC.md
   ↓
PLANNER agent     — decomposes into specialists, writes CONSTELLATION.json
   ↓
PARALLEL FAN-OUT  (10 specialists across 3 phases)
   ├─ Phase 1 (foundation, parallel):  networking · infra · data
   ├─ Phase 2 (services, parallel):    auth · ai · backend · frontend
   └─ Phase 3 (integration, parallel): email · payments · deploy
   ↓
CONVERGENCE agent — verifies every specialist's contract
   ↓
SHIP agent        — terraform apply, first deploy, smoke test
   ↓
LIVE URL
```

Each specialist has a contract: declared `inputs`, `outputs`, and
exclusive `writes_glob`. Convergence enforces — no specialist can
write outside its glob, no specialist's outputs can be missing.

---

## Five principles

1. **Invisible Rails** — Every production gotcha is a silent default. You
   never type "VPC endpoint" but the endpoint is there.
2. **One Right Way** — A new builder does not benefit from 50 options.
   Jarvis picks; you override when you want.
3. **Native AWS Always** — The Terraform is what a senior would write.
   No DSL, no parallel mental model.
4. **No Lock-In** — `/jarvis-eject` works from day one. We're the
   on-ramp, not the prison.
5. **Atomic Feature Transactions** — IaC + IAM + VPC + test + docs
   ship together or not at all.

Read [ETHOS.md](ETHOS.md) for the full philosophy.
Read [ARCHITECTURE.md](ARCHITECTURE.md) for the design.
Read [CHANGELOG.md](CHANGELOG.md) for the release history.

---

## Update + uninstall

### Update

```bash
/jarvis-upgrade
```

Pulls the latest, rebuilds the CLI, offers to migrate unedited
generated files. Your edits always win.

### Uninstall

```bash
rm -rf ~/.claude/skills/jarvis ~/.jarvis
find ~/.claude/skills -maxdepth 1 -type l -name 'jarvis-*' -delete
```

Your apps stay live — Jarvis only manages the scaffold-time tooling.

---

## Status & roadmap

**v1.6.0** (current) — Operational maturity.
- 16 CLI binaries, 22 user-facing skills, 14 feature templates
- 6 starter manifests
- 19 unit tests pass, CI workflow in place
- Cross-machine memory + custom specialists shipped
- Brownfield AWS import shipped
- Live tail + cost + scale + canary + 2 debug commands shipped

**v1.7** — Demo + first 100 users, polished error messages
**v1.8** — Compliance modes (`--compliance soc2` / hipaa / fedramp)
**v1.9** — Plugin system for community-contributed specialists
**v2.0** — Hosted team dashboard (CLI stays MIT free forever) +
template registry + second cloud (Cloudflare adapter)

See [docs/PRODUCT_PLAN.md](docs/PRODUCT_PLAN.md) for the long view.

---

## License

MIT. Free forever. Go build something.
