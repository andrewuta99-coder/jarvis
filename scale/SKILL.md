---
name: jarvis-scale
version: 0.0.1
description: |
  Right-size your ECS service based on real CloudWatch metrics. Suggests
  capacity changes when CPU or memory is consistently over/under threshold.
  Never auto-applies — surfaces recommendations. (jarvis)
allowed-tools: [Bash, Read, AskUserQuestion]
triggers: [jarvis scale, right-size, scale up, scale down]
---

# /jarvis-scale — capacity tuning

Read CloudWatch metrics for the last 14 days, recommend ECS task size + count adjustments.

## Preamble

```bash
[ ! -f .jarvis/profile.json ] && echo "BLOCKED: not a Jarvis project." && exit 1
APP=$(jq -r .app_name .jarvis/profile.json)
REGION=$(jq -r .region .jarvis/profile.json)
```

## Step 1: Pull metrics

For the ECS service over the last 14 days, get:
- Average CPU utilization
- Average memory utilization
- Max CPU
- Max memory
- Request count / ALB

```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ClusterName,Value="$APP-cluster" Name=ServiceName,Value="$APP-api-service" \
  --start-time $(date -u -v-14d +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Average,Maximum \
  --region "$REGION"
```

## Step 2: Decision matrix

| Avg CPU | Max CPU | Recommendation |
|---|---|---|
| < 20% | < 50% | Scale DOWN: halve vCPU |
| 20-60% | < 80% | KEEP current size |
| 60-80% | > 80% | Scale UP: 1.5x vCPU |
| > 80% | > 95% | Scale UP urgent: 2x vCPU |

Similar matrix for memory.

| P95 request latency | Recommendation |
|---|---|
| < 200ms | Healthy |
| 200-1000ms | Investigate slow routes (point at /jarvis-doctor) |
| > 1s | Likely undersized — recommend scale UP |

## Step 3: Surface recommendation

> Current: 1 vCPU / 2 GB / 2 tasks
> Avg CPU (14d): 18% / Max: 42%
> Avg Memory: 31% / Max: 58%
> P95 latency: 87ms
>
> RECOMMENDATION: Scale DOWN
>   Suggest: 0.5 vCPU / 1 GB / 2 tasks
>   Savings: ~$8/mo (Fargate Spot)
>   Risk: low — peak usage stays well within new bounds
>
> Apply?
>   A) Yes, update task definition (recommended)
>   B) Stay at current size
>   C) Apply only to staging, keep prod current

## Step 4: Apply (if confirmed)

Edits `iac/ecs/task_definition.tf` (the `cpu` and `memory` values) and asks the user to run `terraform apply` (does not auto-apply — capacity changes affect prod).

## Voice

> Scaled down to 0.5 vCPU / 1 GB. New task def revision 12. terraform plan shows the change cleanly. Run `cd iac/ecs && terraform apply` when ready. Estimated savings: $8/mo.
