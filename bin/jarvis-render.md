# jarvis-render & jarvis-orchestrate

Two Python binaries that ship with Jarvis to make template rendering and
phase orchestration deterministic.

## jarvis-render

Renders one feature template directory into the user's app.

```bash
jarvis-render \
  --feature networking \
  --context .jarvis/CONTEXT.json \
  --target-dir /path/to/app
```

**What it does:**
1. Reads `templates/features/<feature>/manifest.yaml`
2. Walks `files.always` entries (all rendered)
3. For each `files.conditional`, renders if its `if_feature` is in context.features[]
4. Substitutes `{{SLOTS}}` from context (REGION, APP_NAME, ACCOUNT_ID, etc.)
5. Computes a sha256 of each template's content, exposes as `{{TEMPLATE_HASH}}`
6. Writes to `<target-dir>/<dst>` from the manifest

**Why deterministic:** the same context + same template = same output bytes.
`/jarvis-upgrade` compares the user's file hash to the template's recorded
hash to detect user edits before patching.

## jarvis-orchestrate

Reads `.jarvis/CONSTELLATION.json`, runs each phase end-to-end.

```bash
jarvis-orchestrate --target-dir /path/to/app
```

**What it does:**
1. Reads `.jarvis/CONSTELLATION.json` (produced by the Planner agent)
2. For each phase:
   - If `parallel: true`, runs all features in a ThreadPoolExecutor
   - If `parallel: false`, runs sequentially
   - Each feature invocation = `jarvis-render --feature <name> ...`
3. After each phase, merges `.jarvis/agent-outputs/*.json` into the context
   so later phases can reference earlier outputs (e.g., `VPC_ID`, `ECR_REPO_URL`)
4. Reports per-phase durations + total

**What it doesn't do:**
- Doesn't run `terraform apply` — that's the Ship agent's job.
- Doesn't render IAM policies dynamically — those are in templates already.
- Doesn't talk to AWS at all. Pure file manipulation.

## Context format

```json
{
  "JARVIS_VERSION": "0.0.3",
  "ISO_DATE": "2026-06-08",
  "REGION": "us-east-1",
  "APP_NAME": "my-saas",
  "ACCOUNT_ID": "618143339406",
  "GITHUB_OWNER": "andrewuta99-coder",
  "GITHUB_REPO": "my-saas",
  "DOMAIN": "my-saas.jarvis.app",
  "TASK_ROLE_NAME": "my-saas-task",
  "features": ["auth", "ai", "email", "payments", "frontend"]
}
```

After orchestration, this same file accumulates phase outputs:

```json
{
  ...the above...
  "VPC_ID": "vpc-0a1b2c",
  "ALB_DNS_NAME": "my-saas-alb.us-east-1.elb.amazonaws.com",
  "ECS_CLUSTER_ARN": "...",
  "ECR_REPO_URL": "...",
  ...
}
```

## Slot syntax

`{{SLOT_NAME}}` — must be UPPER_SNAKE_CASE per convention. The renderer's
regex enforces this. Missing slots render as empty by default (use
`--strict` to fail loudly on missing values; not yet wired into the CLI).

## Why Python, not Bun?

`jarvis-render` is one of the few Jarvis binaries written in Python rather
than Bun. Reasons:
- Every dev has python3 on macOS/Linux; bun is opt-in.
- The renderer has no perf-critical path (it writes ~50 files at most).
- Easier to read + extend than a TypeScript port.
- The Bun-compiled binaries are for surfaces with high invocation rate
  (CLI dispatch, browser daemon equivalents); the renderer runs once per
  /jarvis-init or /jarvis-add-X invocation.

## Testing

```bash
# Render one feature in dry-run mode
jarvis-render --feature networking --context test/fixtures/ctx.json \
  --target-dir /tmp/test-out --dry-run

# Full orchestration against a sample constellation
jarvis-orchestrate --target-dir /tmp/test-app
```
