# HN Post Draft — Jarvis v1.0

## Title (60 char limit)

**Show HN: Jarvis – From blank AWS account to deployed SaaS in 10 minutes**

## Body

I built and run CloudMortgage, a mortgage processing platform on AWS. Over
18 months I accumulated a 2,800-line CLAUDE.md that's basically a postmortem
book — every incident, every gotcha, every "I lost half a day to this."

The most painful incidents all had the same shape: I knew the fix the
second time. The first time cost a day. Examples:

- SES emails silently never sent from private subnets until I added a
  `com.amazonaws.us-east-1.email` VPC endpoint. ($7/mo. Cost me a day.)
- Terraform recreated my `cases` and `documents` tables. Data loss.
  `prevent_destroy` would've stopped it.
- ECS tasks accumulated to 22 orphan instances when Step Functions
  timeouts didn't propagate. Hit my vCPU quota. SIGTERM handler fixed it.
- Bedrock agent IAM was locked to one model. Switching from Nova Pro to
  Nova Lite required a separate IAM redeploy. Wildcard fixed it.

So I built **Jarvis** — an agentic AWS scaffold that ships those defaults
silently. The new user types `/jarvis-init`, answers four questions, and
~10 minutes later has a deployed SaaS with auth, AI chat, billing, email,
and a frontend on Amplify Hosting. They never type "VPC endpoint" but the
endpoint is there because I once spent a day not knowing it should be.

What it is, technically:
- One-command install: `curl -fsSL .../install.sh | bash`
- 15 specialist sub-agents (architect, planner, networking, infra, data,
  auth, ai, backend, frontend, email, payments, deploy, ...) running in
  4 parallel phases via Claude Code's Agent tool
- 163 hand-crafted Terraform/Python/React template files. Every one
  carries a `feature:<name> template:<hash>` header so `/jarvis-upgrade`
  can detect user edits and preserve them on migration
- Production patterns baked in as defaults: PITR + prevent_destroy on
  every table, VPC endpoints over NAT, Fargate Spot, HMAC-SHA256 signup
  codes with constant-time verify, Stripe webhook idempotency,
  SIGTERM/SIGALRM in the backend
- AWS-native — generated Terraform is what a senior would write. No
  DSL. `/jarvis-eject` removes Jarvis and writes ARCHITECTURE.md; your
  app keeps running.

What it isn't:
- It's not AWS Amplify. Amplify invented a parallel mental model
  (`amplify add api`) that doesn't map to AWS reality and traps you.
  Jarvis writes vanilla Terraform you can read.
- It's not Vercel. Vercel is easier but you can't run Bedrock or Connect
  on it.
- It's not a SaaS. The CLI is free MIT forever. A hosted dashboard might
  exist later for teams; the CLI never moves behind a paywall.

Repo: https://github.com/andrewuta99-coder/jarvis
Demo (10 min): [link]
30-second sizzle: [link]

Happy to answer questions about the incidents, the agent decomposition
approach, or why I went CRA + FastAPI when the world is on Next.js.

## Reply-ready answers (pre-written for common Qs)

### "Why not just use CDK / SST / Pulumi?"

Same reason I didn't use AWS Amplify: those tools assume you know what
you want to build. They don't bake in the incident defaults. You can use
CDK and still ship without `prevent_destroy` on a data table. Jarvis
makes that impossible by default.

### "Why CRA when Next.js is the default?"

The validated CloudMortgage stack is CRA + Amplify Hosting. It works, it's
cheap, it ships. Most SaaS apps don't need SSR. v1.1 ships a Next.js
starter variant. Pick the one that matches your need.

### "Multi-agent feels overkill"

A single Claude session writing 163 files sequentially takes 40+ minutes.
Three specialists working in parallel finish their phase in the time of
the slowest one — typically 60-90 seconds. The whole build converges in
under 10 minutes. Parallelism isn't a flex; it's the only way the
magic-moment demo is physically possible.

### "What's the trademark situation with 'Jarvis'?"

Marvel owns the trademark for AI assistants. Jasper (formerly Jarvis.ai)
hit a C&D at ~$1.5B valuation. I shipped under Jarvis knowing the rename
risk and will accept it if pressured — the open-source repo will redirect
cleanly. Trademark risk doesn't change the technical work; it does add a
rename to the year-2 roadmap.
