# Architecture

This document explains **why** Jarvis is built the way it is. For setup and usage, see [README.md](README.md). For philosophy, see [ETHOS.md](ETHOS.md).

## The core idea

Jarvis gives Claude Code a virtual cloud platform team. Where most coding agents are a single Claude session writing code sequentially, Jarvis decomposes a build request into specialist sub-agents that work **in parallel** and converge on a deployed app.

The key insight: **AWS deployments fail at three boundaries — IAM, VPC, and Terraform state.** Every architectural choice in Jarvis flows from making sure all three boundaries are addressed atomically in every change.

## The multi-agent constellation

```
USER's Claude Code session  (the orchestrator)
              |
              | Agent tool — spawns specialists in parallel
              v
+----------+-----------+-----------+-----------+
| Architect | Planner  | Convergence | Ship    |
+----------+-----------+-----------+-----------+
              |
              v  (Phase 1 — parallel)
+----------+-----------+-----------+
| Networking | Infra   | Data      |
+----------+-----------+-----------+
              v  (Phase 2 — parallel, depends on Phase 1)
+--------+--------+---------+-----------+
| Auth   | AI     | Backend | Frontend  |
+--------+--------+---------+-----------+
              v  (Phase 3 — parallel, depends on Phase 2)
+--------+----------+-----------+
| Email  | Payments | Deploy    |
+--------+----------+-----------+
              v  (Phase 4 — sequential)
+----------------+--------+
| Convergence    | Ship   |
+----------------+--------+
              v
        LIVE URL
```

### Why parallel?

A single Claude Code session writing all of this sequentially takes 40+ minutes. Three specialists working in parallel finish their phase in the time of the slowest one — usually under 90 seconds per phase. The whole build converges in under 10 minutes.

### How parallelism is implemented

**v0 (current):** The orchestrator session uses the Claude Code `Agent` tool to spawn specialist sub-agents. Multiple `Agent` calls in a single tool-use block execute concurrently. Each sub-agent has isolated context, returns a single message with structured outputs, and exits. This is native to Claude Code today.

**v1:** Each specialist gets its own git worktree (Conductor pattern) for builds too large for a single sub-agent context.

**v2:** Specialists spawn as separate Claude Code sessions via ACP, allowing different model tiers per agent (Opus for Architect, Sonnet for build agents, Haiku for verification).

## Contracts — how specialists don't collide

The Planner produces `CONSTELLATION.json` declaring inputs, outputs, and exclusive `writes_glob` per specialist:

```json
{
  "phases": [
    {
      "id": "foundation",
      "parallel": true,
      "agents": [
        {
          "agent": "networking",
          "outputs": ["vpc_id", "private_subnet_ids", "alb_arn", "vpc_endpoint_arns"],
          "writes": ["iac/networking/*.tf"]
        },
        {
          "agent": "infra",
          "outputs": ["ecs_cluster_arn", "ecr_repo_url", "task_exec_role_arn"],
          "writes": ["iac/ecs/*.tf", "iac/iam/base/*.tf"]
        },
        {
          "agent": "data",
          "outputs": ["users_table_name", "sessions_table_name"],
          "writes": ["iac/dynamodb/*.tf"]
        }
      ]
    },
    {
      "id": "services",
      "depends_on": ["foundation"],
      "parallel": true,
      "agents": [
        {
          "agent": "auth",
          "inputs": ["users_table_name", "sessions_table_name", "task_exec_role_arn"],
          "outputs": ["auth_routes_openapi"],
          "writes": ["backend/auth/*.py", "iac/iam/auth_policy.tf"]
        }
      ]
    }
  ]
}
```

**Conflict prevention:** Two agents can never write the same file. If they need to, the Planner inserts a Convergence sub-step that merges outputs.

**Output passing:** Each completed agent writes structured outputs to `.jarvis/agent-outputs/<agent>.json`. The next phase's prompts include these as concrete `input` values.

**Failure handling:** If any agent returns `BLOCKED` or `NEEDS_CONTEXT`, the orchestrator halts the phase and surfaces the issue to the user. No silent failures.

## Templates, not LLM codegen

Terraform files, IAM policies, and code files are generated from **hand-crafted templates with slot substitution**, not from free-form LLM output. The LLM helps the *user* decide (interview, parameter selection). It does not generate Terraform freehand.

This matters because the production defaults — PITR, deletion protection, `prevent_destroy`, VPC endpoint per service, multi-model IAM wildcards — must be deterministic. An LLM forgetting a single line can lose a database. Templates can't forget.

```
templates/features/email/
├── manifest.yaml             # which files compose this feature
├── terraform/
│   ├── ses.tf.tmpl
│   ├── vpc_endpoint_ses.tf.tmpl       <- baked-in default
│   ├── sns_bounce_complaint.tf.tmpl   <- baked-in default
│   └── iam_policy.tf.tmpl
├── code/
│   └── python/
│       └── email_service.py.tmpl
└── tests/
    └── test_email_iam.py.tmpl
```

The Email specialist reads `manifest.yaml`, picks the partials matching the user's stack (FastAPI vs Node, etc.), fills slots (`{{REGION}}`, `{{APP_NAME}}`, `{{TASK_ROLE_NAME}}`), and writes to disk. The 2026-12-22 SES connect-timeout incident from CloudMortgage is permanently solved because `vpc_endpoint_ses.tf.tmpl` always ships with the email feature.

## Atomic Feature Transactions

Every `/jarvis add-*` command produces, in one PR:

```
iac/<module>/<feature>.tf         # Terraform with prevent_destroy + PITR + tags
iac/iam/<feature>_policy.tf       # IAM policy attached to executor role
tests/integration/<feature>_iam_test.py   # tests IAM works at run-time
docs/features/<feature>.md        # what was added and why
```

The Convergence agent refuses to merge if any of the four are missing. This is what makes the 47 incident defaults from CloudMortgage permanent — they can't be skipped under deadline pressure.

## The five architectural commitments

1. **Templates over codegen.** Deterministic generation. The moat is the template library, not the prompt.
2. **Atomic Feature Transactions.** IaC + IAM + VPC + test + docs together.
3. **Native AWS, always.** No DSLs. Generated artifacts are vanilla Terraform.
4. **Eject must always work.** `rm -rf .jarvis/` leaves a working app on day 1.
5. **Cost-priced at every step.** Every command shows projected $/month before applying.

## State management

```
.jarvis/                            # in user's app repo
├── profile.json                    # what was set up at init
├── constellation.json              # last-run constellation
├── agent-outputs/                  # per-agent outputs (input to next phase)
│   ├── networking.json
│   ├── infra.json
│   └── ...
├── learnings.jsonl                 # project-specific learnings
└── version                         # which Jarvis version generated this repo
```

`.jarvis/` is local-only state. Generated Terraform, code, and IaC live in the user's main tree (`iac/`, `backend/`, `frontend/`). On `jarvis eject`, the `.jarvis/` directory is removed; everything else stays.

## Cost transparency

Every command runs through `bin/jarvis-cost` before applying infra. An offline YAML cost model produces idle and load-projected estimates:

```yaml
dynamodb:
  pay_per_request:
    fixed_per_month: 0
    per_million_writes: 1.25
    per_million_reads: 0.25
nat_gateway:
  per_hour: 0.045
  per_gb_processed: 0.045
vpc_endpoint_interface:
  per_hour: 0.01
  per_az: true
```

Before any `/jarvis add-*` runs, the user sees:

```
About to add: Bedrock agent + Knowledge Base
Cost projection:
  Idle:     +$0.50/mo (KB storage on S3)
  1k users: +$47/mo
Proceed?
```

This kills the #1 fear of AWS new users: a surprise $10,000 bill.

## Update model

`jarvis upgrade` pulls new templates and offers to migrate user repos. Migration uses hash detection:

```hcl
# Generated by Jarvis v0.4.0 — feature:auth template:auth.iam@2026-06-01
# Safe to edit. Jarvis detects edits and asks before overwriting.
```

On upgrade, files whose content hash matches the original template are eligible for auto-patch. Files the user has edited are skipped. The user always wins.

## What's intentionally not here

- **No multi-cloud at v0.** AWS-specific defaults are the moat. Multi-cloud at v2+, never as the wedge.
- **No GUI.** CLI / agent surface only. A dashboard is a separate (future) product.
- **No custom DSL.** Terraform HCL is the artifact. Pulumi/CDK adapters maybe at v2.
- **No multi-tenant SaaS at v0.** Pure laptop install. Hosted dashboard is year-2 monetization, not the wedge.
- **No "debug 47 things" surface.** Build-first. The incident knowledge is encoded as invisible defaults, not user-facing debug commands.

## Cross-host support

Jarvis installs into the right directory for 10+ AI agents via one TypeScript config per host:

```
hosts/
├── claude.ts      # ~/.claude/skills/
├── codex.ts       # ~/.codex/skills/
├── cursor.ts      # ~/.cursor/skills/
├── opencode.ts    # ~/.config/opencode/skills/
├── factory.ts     # ~/.factory/skills/
├── openclaw.ts    # ~/.openclaw/skills/
└── ...
```

`./setup --host <name>` reads the host config and links the skill files into the right place. Adding a new host is a config change, not a code change.

## Why Bun

Same reasons as GStack chose Bun:

1. **Compiled binaries** — `bun build --compile` produces a single ~60MB executable. No node_modules at runtime, no PATH games.
2. **Native SQLite** — for the learnings cache. No `better-sqlite3` native addon compilation.
3. **Native TypeScript** — fast dev loop without ts-node.
4. **Built-in HTTP server** — for the future `jarvis-server` daemon when we add it.

Bun startup is also fast (~1ms vs ~100ms for Node), which matters when the user runs `jarvis cost` 20 times during a build.
