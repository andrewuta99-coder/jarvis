# Pattern: Scale-to-Zero GPU on ECS via EC2 Spot

**Source**: CloudMortgage `iac/ecs-gpu/`. The pattern that makes occasional
GPU workloads (closed-loop ML experiments, batch model inference) cost ~$0
when idle and a few cents/hour when running.

## When to use this

- You need a GPU sometimes — not 24/7.
- Workload is interruption-tolerant (batch processing, has Step Functions
  retry, or a queue with at-least-once delivery).
- You want bills measured in dollars/month, not thousands.

## When NOT to use this

- Latency-sensitive real-time inference. ASG scale-up takes 1-3 minutes.
- You actually need 24/7 GPU. Then reserve capacity is cheaper.
- Your model fits Bedrock — use Bedrock instead (no infrastructure at all).

## How it works

```
┌──────────────────┐
│  Task queued     │  e.g., Step Functions Sync state targeting
│  with capacity   │  the alpamayo-gpu-spot capacity provider
│  provider        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  ECS managed     │  target_capacity = 100, ECS asks ASG
│  scaling sees    │  for desired_count = (tasks_pending / 1)
│  pending task    │  in-this case the ASG goes 0 → 1
└────────┬─────────┘
         │
         ▼
┌──────────────────┐  
│  EC2 Spot        │  g5.2xlarge or g6e.12xlarge spot instance launches.
│  instance        │  user_data installs ECS agent + GPU drivers come
│  launches        │  pre-baked in the AL2023-gpu AMI.
└────────┬─────────┘
         │ 1-3 min
         ▼
┌──────────────────┐
│  Container       │  ECS schedules the GPU-requesting task on the
│  runs            │  new host. Task does its work. Exits.
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  No more tasks   │  ECS managed scaling sees 0 pending tasks.
│  → ASG → 0       │  ASG terminates the instance.
└──────────────────┘
```

**Cost shape**: $0/hr when ASG is at 0, ~$0.45/hr g5.2xlarge spot price
(varies by region/AZ), + ~$0.005/hr per ENI when a task is up.

## Critical implementation notes

### 1. AMI choice — AL2023, NOT AL2

The ECS-optimized GPU AMI defaults to Amazon Linux 2 (glibc 2.26, GCC 7.3).
Modern Python wheels (`numpy`, `torch`) target manylinux_2_28 which requires
glibc 2.28+. Result: `uv sync` fails with:

```
ERROR: Problem encountered: NumPy requires GCC >= 9.3
```

Force AL2023 via SSM parameter:

```hcl
data "aws_ssm_parameter" "ecs_gpu_ami" {
  name = "/aws/service/ecs/optimized-ami/amazon-linux-2023/gpu/recommended/image_id"
}
```

### 2. Cluster capacity-provider association — NOT in Terraform

After the first `terraform apply`, run ONCE:

```bash
aws ecs put-cluster-capacity-providers \
  --cluster <cluster-name> \
  --capacity-providers FARGATE FARGATE_SPOT alpamayo-gpu-spot \
  --default-capacity-provider-strategy capacityProvider=FARGATE_SPOT,weight=1 \
  --region us-east-1
```

This is intentionally outside Terraform so it doesn't step on the
FARGATE/FARGATE_SPOT registrations that aren't Terraform-managed. The
command is idempotent — safe to rerun.

### 3. GPU registration race

When a new EC2 host boots, the ECS agent registers with the cluster
**before** the nvidia drivers report GPU resources. ECS schedulers see
"0 GPU available" and won't schedule the task. Then drivers come online,
the host re-reports — but the task has already been kicked back to PENDING.

Fix: in `user_data`, poll `nvidia-smi` until it succeeds before starting
the ECS agent:

```bash
until nvidia-smi >/dev/null 2>&1; do sleep 2; done
systemctl start ecs
```

### 4. Spot draining

```ini
# /etc/ecs/ecs.config
ECS_ENABLE_SPOT_INSTANCE_DRAINING=true
```

When EC2 sends a Spot interruption notice (2-minute warning), the agent
drains the host — running tasks get SIGTERM and a chance to checkpoint
or exit cleanly. Without this, tasks just die.

## Pairs well with

- `/jarvis-add-pipeline` (Step Functions + S3 inbox) — the typical
  consumer of GPU capacity.
- `/jarvis-add-jobs` (SQS + worker) — simpler queue pattern that can also
  route to the GPU capacity provider.

## Status

- v0.0.1: documented (this page).
- v0.0.3: full `templates/features/gpu/` implementation, `/jarvis-add-gpu`
  skill, integration with the AI Agent starter template.
