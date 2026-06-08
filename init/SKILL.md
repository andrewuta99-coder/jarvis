---
name: jarvis-init
version: 0.0.1
description: |
  Bootstrap a new AWS project from scratch. Interviews the user (4 questions),
  produces a BUILD_SPEC.md, decomposes into a constellation of specialist agents,
  spawns them in parallel across 4 phases, converges and deploys. Goes from
  blank AWS account to live URL in under 30 minutes. (jarvis)
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - AskUserQuestion
  - Agent
triggers:
  - jarvis init
  - build me an app
  - bootstrap aws
  - new aws project
  - spin up infra
---

# /jarvis init — the magic moment

This is the headline skill. From blank repo + AWS credentials to deployed app in under 30 minutes.

## Preamble (run first)

```bash
JARVIS_DIR="${JARVIS_DIR:-$HOME/.claude/skills/jarvis}"
VERSION=$(cat "$JARVIS_DIR/VERSION" 2>/dev/null || echo "0.0.0")
echo "JARVIS_VERSION: $VERSION"

# Upgrade check (throttled, silent failure)
_UPD=$("$JARVIS_DIR/bin/jarvis-update-check" 2>/dev/null || true)
[ -n "$_UPD" ] && echo "$_UPD"

# AWS identity (BLOCKS if missing — init cannot proceed without credentials)
AWS_ID=$(aws sts get-caller-identity --output json 2>/dev/null || echo "")
if [ -z "$AWS_ID" ]; then
  echo "BLOCKED: no AWS credentials. Run 'aws configure' then re-run /jarvis-init."
  exit 1
fi
ACCOUNT=$(echo "$AWS_ID" | python3 -c 'import sys,json;print(json.load(sys.stdin)["Account"])' 2>/dev/null)
echo "AWS_ACCOUNT: $ACCOUNT"

# Region
REGION="${AWS_REGION:-${AWS_DEFAULT_REGION:-us-east-1}}"
echo "AWS_REGION: $REGION"

# Project state — refuse to re-init an existing Jarvis project
if [ -d .jarvis ] && [ -f .jarvis/profile.json ]; then
  echo "EXISTING_PROJECT: yes"
fi

# Working directory must be empty-ish (no existing app files)
EXISTING_FILES=$(ls -A 2>/dev/null | grep -v -E '^\.(git|jarvis|gitignore|DS_Store)$' | wc -l | tr -d ' ')
echo "EXISTING_FILES: $EXISTING_FILES"
```

## Step 0: Safety checks

If `EXISTING_PROJECT: yes`, stop and tell the user:

> This directory is already a Jarvis project. Use `/jarvis-add-<feature>` to extend it, or `/jarvis-eject` first if you want to start over.

If `EXISTING_FILES` is greater than 0, ask the user:

> This directory already has files. Jarvis init writes to `iac/`, `backend/`, `frontend/`, and a few root files. It will not delete existing files but may conflict.
>
> Continue? (y / pick a different empty directory)

## Step 1: The interview (4 questions)

Use AskUserQuestion. Keep it to 4 questions. Each should auto-default to the recommended option.

**Question 1: What are you building?**

Options:
- A) AI SaaS — auth, billing, AI chat, email (recommended for first-time users)
- B) AI Agent — chatbot or document processor
- C) Marketplace — two-sided platform with payments
- D) Internal tool / dashboard
- E) Custom — interview me further

**Question 2: Frontend?**

Options:
- A) React (Create React App on Amplify Hosting) (recommended — validated stack from CloudMortgage)
- B) React + Vite
- C) Next.js (SSR on ECS)
- D) None — backend only

**Question 3: Backend?**

Options:
- A) FastAPI on ECS Fargate Spot (recommended)
- B) Node + Express on ECS Fargate Spot
- C) Lambda + API Gateway (low-traffic, pay-per-request)

**Question 4: Region?**

Options:
- A) us-east-1 (recommended — widest service availability, includes Bedrock)
- B) us-west-2
- C) eu-west-1
- D) Other (ask)

Save answers as `.jarvis/profile.json`:

```json
{
  "version": "0.0.1",
  "template": "ai-saas",
  "frontend": "cra",
  "backend": "fastapi",
  "region": "us-east-1",
  "account": "{{ACCOUNT}}",
  "created_at": "{{ISO_TIMESTAMP}}"
}
```

## Step 2: Architect agent — produce BUILD_SPEC.md

Spawn the Architect sub-agent to produce a structured spec. Use the Agent tool:

```
Agent(
  subagent_type="general-purpose",  # v0 — will be jarvis-architect once registered
  description="Architect: draft BUILD_SPEC",
  prompt="""
You are the Jarvis Architect agent. Read the user's profile choices below and
produce a BUILD_SPEC.md that enumerates the AWS resources, features, and
contracts needed.

User profile:
  template: ai-saas
  frontend: cra
  backend: fastapi
  region: us-east-1
  account: {{ACCOUNT}}

Produce BUILD_SPEC.md with these sections:
  1. Features (list each feature with one-line description)
  2. AWS resources (table: service, count, why)
  3. Estimated cost (idle, 1k users)
  4. Risk callouts (anything the user should know before we proceed)

Write to: .jarvis/BUILD_SPEC.md

Do not write any other files. Return a single message with the spec summary.
"""
)
```

After Architect returns, read `.jarvis/BUILD_SPEC.md` and show the user a 3-line summary plus the cost estimate. Ask for approval.

## Step 3: Planner agent — produce CONSTELLATION.json

Spawn the Planner sub-agent:

```
Agent(
  subagent_type="general-purpose",  # v0 — will be jarvis-planner
  description="Planner: produce constellation",
  prompt="""
You are the Jarvis Planner agent. Read .jarvis/BUILD_SPEC.md and produce
.jarvis/CONSTELLATION.json declaring the specialist agents, their phases,
contracts (inputs/outputs), and exclusive writes_glob per agent.

Use this exact JSON shape:
{
  "version": "1",
  "phases": [
    {
      "id": "foundation",
      "parallel": true,
      "agents": [
        {
          "agent": "networking",
          "outputs": [...],
          "writes": [...]
        }
      ]
    }
  ]
}

For the AI SaaS template, the constellation has 4 phases:
  Phase 1 (foundation, parallel): networking, infra, data
  Phase 2 (services, parallel, depends_on=foundation): auth, ai, api, frontend
  Phase 3 (integration, parallel, depends_on=services): email, payments, deploy
  Phase 4 (sequential): convergence, ship

Each agent's writes_glob must be exclusive (no two agents write the same file).
"""
)
```

## Step 4: Phase 1 — Foundation (parallel)

Read `.jarvis/CONSTELLATION.json`. For Phase 1, spawn Networking, Infra, and Data agents in parallel — three Agent calls in a single tool-use block:

```
parallel:
  Agent(subagent_type="general-purpose", description="Networking",
        prompt="<render with networking spec>")
  Agent(subagent_type="general-purpose", description="Infra",
        prompt="<render with infra spec>")
  Agent(subagent_type="general-purpose", description="Data",
        prompt="<render with data spec>")
```

Each agent writes its `outputs` JSON to `.jarvis/agent-outputs/<agent>.json`. The orchestrator reads them after the parallel block returns.

**NOTE for v0:** The specialist SKILL.md files in `agents/<name>/SKILL.md` are the prompt templates. Read them and pass their contents as the Agent prompt. The agents themselves are v0-stubs — they will write Terraform that validates but doesn't apply yet.

## Step 5: Phase 2 — Services (parallel)

Same pattern. Spawn Auth, AI, API, Frontend in parallel. Inputs come from Phase 1's agent outputs.

## Step 6: Phase 3 — Integration (parallel)

Email, Payments, Deploy in parallel.

## Step 7: Phase 4 — Convergence + Ship

Convergence agent verifies all contracts. Ship agent runs `terraform init && terraform apply` and waits for the ALB to come healthy.

## Step 8: Reveal

Print the live URL, the test credentials, and the cost projection. Open the URL in the user's browser. Save the state.

```bash
PROFILE=$(cat .jarvis/profile.json)
URL=$(jq -r .url .jarvis/agent-outputs/deploy.json)
COST_IDLE=$(jq -r .cost_idle .jarvis/agent-outputs/ship.json)
COST_1K=$(jq -r .cost_1k_users .jarvis/agent-outputs/ship.json)

echo ""
echo "YOUR APP IS LIVE"
echo "   $URL"
echo "   Test login: demo@$URL / demo"
echo "   Cost projection (idle):     \$$COST_IDLE/mo"
echo "   Cost projection (1k users): \$$COST_1K/mo"
echo ""
```

## Step 9: Telemetry + completion status

Report `DONE` with evidence: live URL, cost projection, time elapsed.

If any phase failed: report `BLOCKED` with the failed agent's error and recommendations.

## v0 scope notes

This skill is the SKELETON for v0. The actual Architect / Planner / specialist agents are stubs in `agents/<name>/SKILL.md` that need to be fleshed out before this works end-to-end. The init flow above is the target user experience; the agents are what get built next.

First milestone: get Phase 1 working end-to-end on a real AWS account, producing valid Terraform that `terraform plan` accepts. That's the demo-of-the-demo.
