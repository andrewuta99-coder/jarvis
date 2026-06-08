# Jarvis Development Guide

This file guides Claude Code when working **on the Jarvis project itself**, not when Jarvis is being used to scaffold someone else's app.

## What Jarvis is

Jarvis is an agentic scaffold that builds full-stack AWS apps from a blank account. The user types `/jarvis init`, ~10 specialist sub-agents work in parallel, and ~10 minutes later they have a deployed app.

The user-facing surface is a set of skills (`/jarvis init`, `/jarvis add-users`, etc.). The internal surface is the specialist agents in `agents/` and the templates in `templates/`.

## Project structure

```
jarvis/
├── README.md, ARCHITECTURE.md, ETHOS.md  # the founding docs
├── VERSION, LICENSE, package.json
├── setup                                   # one-time install
├── bin/                                    # CLI binaries (will be bun-compiled)
├── agents/                                 # 15 specialist sub-agent definitions
│   ├── architect/SKILL.md                  # interviews the user
│   ├── planner/SKILL.md                    # decomposes into constellation
│   ├── networking/                         # VPC, ALB, VPC endpoints
│   ├── infra/                              # ECS, ECR, IAM base
│   ├── data/                               # DynamoDB tables
│   ├── auth/                               # users + JWT
│   ├── ai/                                 # Bedrock + KB + OpenSearch
│   ├── backend/                            # FastAPI / Node service code
│   ├── api/                                # routes, OpenAPI
│   ├── frontend/                           # React app
│   ├── email/                              # SES + VPC endpoint
│   ├── payments/                           # Stripe + webhook
│   ├── deploy/                             # GitHub Actions + Amplify
│   ├── convergence/                        # contract verification
│   └── ship/                               # terraform apply + smoke test
├── templates/                              # the heart of the product
│   ├── starters/                           # full-app starting points
│   └── features/                           # per-feature partials
├── hosts/                                  # per-AI-agent install configs
│   ├── claude.ts, codex.ts, cursor.ts, ...
├── init/SKILL.md                           # /jarvis init (user-facing entry)
├── add-users/, add-files/, ...             # one skill per feature
├── deploy/SKILL.md, doctor/SKILL.md, ...   # operate skills
├── eject/SKILL.md                          # the trust-promise skill
├── jarvis-upgrade/SKILL.md                 # self-updater
└── docs/                                   # design docs, decisions, postmortems
```

## Core principles (when modifying Jarvis)

1. **Templates not codegen.** Add a new feature by adding a template directory under `templates/features/`. Do NOT add LLM-generation code for the Terraform itself — the LLM helps the user *decide*, the templates handle generation.

2. **Specialists own their writes_glob.** When editing an agent, do not let it write outside its declared `writes` paths. The Convergence agent enforces this at integration time.

3. **Every default has an incident reason.** When adding a baked-in default (e.g., a VPC endpoint, a `prevent_destroy` block), include a comment with the date and the failure mode that motivated it. The CLAUDE.md of CloudMortgage is the spec.

4. **Eject must always work.** Test that `rm -rf .jarvis/` leaves a working app after every change. If a change makes ejection harder, redesign.

## Build commands

```bash
bun install              # install dependencies
bun test                 # run free tests
bun run build            # compile binaries + regen skill docs
bun run gen:skill-docs   # regenerate SKILL.md from templates
./setup                  # one-time install (for the user)
./setup --host codex     # install for OpenAI Codex CLI
./setup --team           # team mode (repo-shared)
```

## Skill template workflow (when we get there)

SKILL.md files will be generated from `.tmpl` templates by `bun run gen:skill-docs`. This prevents docs from drifting from code. CI fails if `git diff` shows uncommitted regeneration.

At v0 we're hand-writing skills directly. The template system arrives in v0.2.

## Agent invocation pattern

Specialists run via Claude Code's `Agent` tool. The orchestrator (`init/SKILL.md`) spawns them in parallel:

```
# Conceptual — actual implementation in init/SKILL.md
Phase 1: parallel(
    Agent(subagent_type="jarvis-networking", prompt=phase1.networking_spec),
    Agent(subagent_type="jarvis-infra",      prompt=phase1.infra_spec),
    Agent(subagent_type="jarvis-data",       prompt=phase1.data_spec),
)
```

Each specialist's SKILL.md declares its `contract.inputs`, `contract.outputs`, and `contract.writes_glob`. The orchestrator renders the prompt with concrete `inputs` from prior phase outputs.

## Status

**v0 — pre-alpha.** Scaffolding committed. Next milestones:

1. Specialist agents: write SKILL.md for Architect, Planner, Networking, Infra, Data
2. AI SaaS starter template: complete `templates/starters/ai-saas-cra-fastapi/`
3. `init` skill that runs Phase 1 end-to-end on a real AWS account
4. Demo recording at <10 minutes

Track progress in `docs/MILESTONES.md`.

## Voice (for docs and skill prose)

- Lead with the point. Say what it does, why it matters, what changes for the builder.
- Be concrete. Name files, services, dollar amounts.
- Tie technical choices to user outcomes.
- Never corporate, academic, or PR voice.
- The user has context the models don't. Cross-model agreement is a recommendation, not a decision.

Good: *"add-email creates an SES verified sender, the VPC endpoint for SES, bounce/complaint SNS topic, and the IAM policy your ECS task needs. Idle cost: $0. At 10k emails/month: $0.50."*

Bad: *"This feature provisions a comprehensive email delivery solution with robust security and monitoring."*
