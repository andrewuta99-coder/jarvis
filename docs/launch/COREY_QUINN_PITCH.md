# Last Week in AWS — pitch to Corey Quinn

Email, not DM. Corey hates DMs.

## Subject

`Jarvis — open-source, scale-to-zero AWS scaffold (with a NAT-vs-VPC-endpoint anecdote you'll like)`

## Body

Hi Corey,

I run CloudMortgage, a mortgage AI platform on AWS. Over 18 months on
the same account I built up a 2,800-line CLAUDE.md that's basically a
postmortem book — every incident, every "I lost a day to this," every
production gotcha that's nowhere in the AWS docs.

I open-sourced the bottled version: **Jarvis** —
github.com/andrewuta99-coder/jarvis. MIT, free, no upsell, no waitlist.

Three things I think will land for your audience:

**1. The VPC-endpoint vs NAT cost flip.** The default Jarvis VPC has zero
NAT Gateway. 10 interface endpoints across 2 AZs = ~$146/mo for the same
private-subnet AWS connectivity you'd otherwise pay $65/mo NAT for —
*until* you process more than ~50GB/mo of S3/DDB traffic, at which point
data transfer dominates and NAT loses badly. The crossover point is at a
traffic level most apps reach in week one. I have receipts (CloudMortgage's
own bill before and after the switch). Happy to share the numbers.

**2. The OpenSearch Serverless minimum-spend trap.** Every Bedrock
Knowledge Base example AWS publishes uses OpenSearch Serverless. Few of
the examples mention the $50/mo minimum (2 OCU index + 2 OCU search, even
when you have zero traffic). Jarvis prints the cost line at install time
and offers a no-KB chat-only variant for users who don't need RAG, which
drops idle cost from $200/mo to $160/mo. I think this is your kind of
"AWS published a quick-start, billed you anyway" story.

**3. The agent decomposition is the gimmick.** Jarvis runs ~15 specialist
sub-agents (architect, planner, networking, infra, data, auth, ai, etc.)
in parallel via Claude Code's Agent tool. The whole build converges in
under 10 minutes from a blank AWS account to a deployed SaaS. The pitch
isn't "AI replaces engineers"; it's "the long tail of AWS gotchas finally
gets a place to live, so newcomers stop relearning them one outage at a
time."

Demo: [link to 30s video]
Repo: https://github.com/andrewuta99-coder/jarvis
Launch post: [HN link]

Not asking for anything specific. If any of the above is newsletter-worthy,
I'm happy to dig deeper on the cost analysis, share the actual CloudMortgage
bills, or do a quick video interview. If not, no worries — wanted to put
it on your radar regardless.

Thanks,
Andrew Nguyen
CloudMortgage / Jarvis
