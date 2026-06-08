---
name: jarvis-doctor
version: 0.0.1
description: |
  Passive health check of your Jarvis-managed AWS app. Reads CloudWatch, IAM,
  Terraform state. Reports on protection (PITR, prevent_destroy), performance
  (ECS health, KB freshness), cost (vs budget, vs projection), and security
  (open SGs, wildcard IAM, MFA on root). Encouraging tone — not 47 things wrong. (jarvis)
allowed-tools: [Bash, Read]
triggers:
  - jarvis doctor
  - is my stack healthy
  - health check
  - audit my stack
---

# /jarvis-doctor — passive health check

This is the only audit-style command Jarvis ships, and by design it reads as "your stack is healthy" with a few suggestions. The 47-things-wrong interrogation style is what AWS Trusted Advisor does badly — we don't.

## Preamble

```bash
[ ! -f .jarvis/profile.json ] && echo "BLOCKED: not a Jarvis project." && exit 1
PROFILE=$(cat .jarvis/profile.json)
APP=$(echo "$PROFILE" | jq -r '.app_name')
REGION=$(echo "$PROFILE" | jq -r .region)
TEMPLATE=$(echo "$PROFILE" | jq -r .template)
AGE_DAYS=$(echo "$PROFILE" | jq -r '.created_at' | xargs -I {} python3 -c "import datetime;d=datetime.datetime.fromisoformat('{}'.replace('Z','+00:00'));print((datetime.datetime.now(datetime.timezone.utc)-d).days)")
echo "APP: $APP | TEMPLATE: $TEMPLATE | AGE: ${AGE_DAYS}d"
```

## Step 1: Protection check

Read every DynamoDB table in the user's stack. For each, verify:
- PITR enabled (yes/no)
- deletion_protection_enabled (yes/no)
- Has `prevent_destroy` in its Terraform (grep iac/dynamodb/*.tf)

Read every S3 bucket. Verify:
- public_access_block all four flags ON
- versioning enabled
- encryption configured

## Step 2: Performance check

```bash
# ECS service health
aws ecs describe-services --cluster "$APP-cluster" --services "$APP-api-service" \
  --region "$REGION" --query 'services[0].{desired:desiredCount,running:runningCount,pending:pendingCount}'

# Knowledge Base sync freshness (if AI feature present)
LAST_KB_SYNC=$(aws bedrock-agent get-ingestion-job ... 2>/dev/null || echo unknown)
```

## Step 3: Cost check

```bash
# Month-to-date spend via Cost Explorer
COST_MTD=$(aws ce get-cost-and-usage --time-period Start=$(date -u +%Y-%m-01),End=$(date -u +%Y-%m-%d) \
  --granularity MONTHLY --metrics UnblendedCost --output json | jq -r '.ResultsByTime[0].Total.UnblendedCost.Amount')

# Compare against projection in .jarvis/profile.json
PROJECTED=$(echo "$PROFILE" | jq -r '.cost_projection_idle')
```

## Step 4: Security check

- Root account MFA? `aws iam get-account-summary | jq '.SummaryMap.AccountMFAEnabled'`
- Any IAM users with access keys older than 90 days?
- Any security groups with 0.0.0.0/0 ingress on ports other than 80/443?
- Any Lambda function URLs that are public?

## Step 5: Report

Format the output as a friendly health check. Use checkmarks and warnings, not red error spam:

```
Stack: my-saas (AI SaaS)
Age:   14 days
Region: us-east-1

PROTECTION
  ok  All 4 data tables: PITR on, prevent_destroy on
  ok  3 S3 buckets: public-block on, versioning on
  ok  Secrets rotation: enabled

PERFORMANCE
  ok  ECS service: 2/2 tasks healthy
  warn Bedrock KB sync stale (3 days old) - run /jarvis-sync-kb
  ok  DynamoDB: well within capacity

COST
  Month-to-date: $34.12
  Projected:     $47/mo  (you're tracking 27% under)
  ok  No idle waste detected

SECURITY
  ok  Root MFA: enabled
  ok  No public buckets
  ok  No wildcard IAM policies
  warn 1 IAM user has access keys older than 60 days (consider rotation)

Stack is healthy. 2 warnings, both non-urgent.
Run /jarvis-doctor --fix to address warnings interactively.
```

## Step 6: --fix mode

If invoked as `/jarvis-doctor --fix`, walk through each warning interactively:

> 1 of 2: Bedrock KB sync stale (3 days). Run KB sync now?
>   A) Yes (recommended — takes ~2 min)
>   B) Skip

Never auto-fix without asking. User Sovereignty.

## Completion

Report status (DONE / DONE_WITH_CONCERNS). Doctor only escalates to BLOCKED if AWS credentials are missing or the user's account is in a clearly broken state.
