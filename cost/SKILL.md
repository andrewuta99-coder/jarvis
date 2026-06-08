---
name: jarvis-cost
version: 0.0.1
description: |
  Explain your AWS bill in plain English. Pulls Cost Explorer for the current
  month, annotates the top spend categories ("$3.40 — Bedrock agent traces"),
  compares against projections, suggests cuts. (jarvis)
allowed-tools: [Bash, Read]
triggers: [jarvis cost, explain my bill, why is my aws bill high]
---

# /jarvis-cost — your AWS bill, explained

Cost Explorer aggregated by service, annotated with the why and the what-to-do.

## Preamble

```bash
[ ! -f .jarvis/profile.json ] && echo "BLOCKED: not a Jarvis project." && exit 1
REGION=$(jq -r .region .jarvis/profile.json)
PROJECTED_IDLE=$(jq -r .cost_projection_idle .jarvis/profile.json)
PROJECTED_1K=$(jq -r .cost_projection_1k .jarvis/profile.json)
```

## Step 1: Pull Cost Explorer (current month)

```bash
START=$(date -u +%Y-%m-01)
END=$(date -u +%Y-%m-%d)

aws ce get-cost-and-usage \
  --time-period "Start=$START,End=$END" \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --output json > /tmp/cost.json
```

## Step 2: Annotate top services

For each service in the top 10, print what it is and why it costs that:

| Service | Cost | Why |
|---|---|---|
| Amazon Elastic Container Service | $8.40 | Your ECS Fargate Spot tasks |
| Amazon OpenSearch Service | $52.00 | KB vector index minimum capacity |
| Amazon Bedrock | $3.40 | Chat invocations + agent traces |
| AWS Lambda | $0.02 | Email suppression handler |
| Amazon DynamoDB | $0.50 | Pay-per-request, your tables |
| Amazon CloudWatch | $1.20 | Logs ingestion + metrics |

## Step 3: Compare against projection

```
Month-to-date:       $65.52
Projected (idle):    $14
Projected (1k MAU):  $47
You're tracking:     +40% over 1k-MAU projection
```

## Step 4: Suggest cuts (gentle, never auto-apply)

Top 3 suggestions, ranked by savings potential:

> OpenSearch is your biggest line item ($52/mo).
>   - If you're not actively using KB, consider /jarvis-doctor --pause-kb (saves $50/mo, KB rebuilds on next /jarvis-sync-kb)
>   - At 1k+ daily chats this is fine; at <100 it's expensive
>
> CloudWatch Logs is $1.20.
>   - Default log retention is 30 days. Set to 7 to halve this.
>
> Bedrock $3.40.
>   - You're invoking Nova Lite ~700 times this month. Nova Pro would be ~10x cost.
>   - Consider sampling agent traces (currently 100%, suggest 10%) for -90% trace cost.

## Step 5: Forecast end-of-month

```
Forecasted end-of-month: ~$98 (linear projection from MTD)
Budget alert at $100:    ACTIVE
```

## Voice

Plain English. No tables of incomprehensible cost codes. Always end with "next month you can save $X by doing Y."
