# Twitter / X Launch Thread

Tone: matter-of-fact, builder voice. No hype words. Concrete numbers
or a war story per tweet.

---

**1/12**
I open-sourced 18 months of AWS production scars as a tool.

It's called Jarvis. One command turns a blank AWS account into a deployed
SaaS in 10 minutes — auth, AI chat, billing, email, frontend. AWS-native.
No PaaS lock-in. MIT.

🔗 github.com/andrewuta99-coder/jarvis

🎥 [30-sec demo]

---

**2/12**
Every default in Jarvis exists because I once paid for the lack of it.

🔻 9 examples below 🔻

---

**3/12**
SES → silently never sends emails from private subnets.

I lost a half-day before realizing the `com.amazonaws.us-east-1.email`
VPC endpoint was missing.

Jarvis ships the endpoint with the email feature. You never type
"VPC endpoint." Cost: $7/mo. Sanity: priceless.

---

**4/12**
Terraform destroyed my `cases` and `documents` tables in production
because I forgot `prevent_destroy` lifecycle blocks.

Jarvis puts `prevent_destroy + deletion_protection + PITR` on every
DynamoDB table. Always. No flag.

---

**5/12**
ECS tasks accumulated to 22 orphans (44 vCPUs!) and hit my account
quota. Step Functions timeouts weren't propagating SIGTERM.

Jarvis backend skeleton has SIGTERM + SIGALRM handlers + 1h hard timeout
out of the box. The 2026-12-22 bug class is dead.

---

**6/12**
Bedrock agent IAM was scoped to ONE model. Swapping from Nova Pro to
Nova Lite required IAM redeploy.

Jarvis ships multi-model wildcards (Nova + Claude families). You change
DEFAULT_MODEL env var; no IAM change needed.

---

**7/12**
Stripe webhook double-charged a user because the route had no
idempotency check.

Jarvis ships an `@idempotency` decorator + DynamoDB table. Every
charging endpoint is wrapped. The 2026-01-11 bug class is dead.

---

**8/12**
Signup verification codes were SHA-256 hashed. Rainbow-tableable for
6-digit codes.

Jarvis uses HMAC-SHA256 + constant-time compare + per-tenant rate limit.
Bedrock-approved security hygiene from day 1.

---

**9/12**
OpenSearch Serverless costs $50/mo MINIMUM (2 OCU). Most AWS quickstarts
hide this.

Jarvis prints the line at install. Skip KB → drop idle cost to $160/mo
total. Show me one other AWS template that's this honest about cost.

---

**10/12**
Cost shape for the AI SaaS starter:

📊 Idle: ~$200/mo (mostly VPC endpoints + OpenSearch)
📊 At 1k MAU: ~$225/mo
📊 No NAT Gateway anywhere — saved $130/mo via endpoint pattern

vs Vercel $20/mo: yes, but you can't run Bedrock there.

---

**11/12**
How it actually works:

🤖 4 questions at init
🤖 10+ specialist sub-agents (architect, planner, networking, infra,
   data, auth, ai, backend, frontend, email, payments, deploy)
🤖 Run in 4 parallel phases via Claude Code's Agent tool
🤖 ~10 min total from cold AWS account → live URL

---

**12/12**
The agent constellation is the gimmick.

The DEFAULTS are the product.

Free. MIT. Open source. Eject anytime — the generated Terraform is
vanilla and yours.

🔗 github.com/andrewuta99-coder/jarvis
📥 Install: `curl -fsSL .../install.sh | bash`

Built it because I needed it. Sharing because everyone learns these
the hard way.
