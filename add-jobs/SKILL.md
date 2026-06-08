---
name: jarvis-add-jobs
version: 0.0.1
description: |
  Add background job processing. Auto-picks the right pattern: SQS + ECS worker
  for simple async work, Step Functions for multi-step pipelines. SIGTERM
  handlers, DLQ, retry policy, idempotency — all baked in. (jarvis)
allowed-tools: [Bash, Read, Write, Edit, AskUserQuestion]
triggers:
  - jarvis add jobs
  - background job
  - process async
  - add queue
  - add worker
  - add step functions
---

# /jarvis-add-jobs — async work, done right

The ECS task cleanup incident (CloudMortgage 2026-12-22 — 22 orphaned tasks, 44 vCPUs, hit account quota) is permanently solved: every worker handles SIGTERM, has a hard timeout, and exits cleanly. The Step Functions "manifest is single source of truth" pattern (the batches.json lesson) is encoded in the multi-step template.

## Preamble

```bash
[ ! -f .jarvis/profile.json ] && echo "BLOCKED: not a Jarvis project." && exit 1
```

## Step 1: Job shape — auto-pick

Ask which fits:

Options:
- A) Simple async — "do this when a request comes in but don't block the response" (SQS + ECS worker) (recommended for most cases)
- B) Multi-step pipeline — "do X, wait, do Y, branch on result, do Z" (Step Functions + ECS workers)
- C) Scheduled — "run this at 2am every day" (use /jarvis-add-schedule instead)
- D) Long-running — "this job takes > 15 min" (always picks Step Functions + ECS)

## Cost projection

> About to add: Jobs ({{PATTERN}})
> Cost projection (SQS pattern):
>   Idle:               +$0/mo
>   1k jobs/mo:         +$0/mo (SQS free tier)
>   1M jobs/mo:         +$0.40/mo + ECS runtime
>
> Cost projection (Step Functions pattern):
>   Idle:               +$0/mo
>   1k executions/mo:   +$0.025/mo
>   100k transitions/mo: +$2.50/mo + ECS runtime

## Step 2: Spawn the Backend specialist with the jobs flag

writes_glob:
- `iac/sqs/jobs_queue.tf` (if SQS pattern) — DLQ, visibility timeout, redrive policy
- `iac/stepfunctions/main.tf` (if SFN pattern) — state machine + IAM
- `iac/ecs/worker_task.tf` — separate task definition for the worker
- `iac/iam/jobs_policy.tf` — scoped to SQS or SFN + DynamoDB
- `backend/jobs/*.py` — worker, handler registration, SIGTERM handling
- `backend/jobs/example_job.py` — a hello-world job to verify the pipeline
- `tests/integration/test_jobs.py`

## Invisible rails

- **SIGTERM handler** on every worker — graceful shutdown on ECS task stop, prevents orphan tasks
- **SIGALRM hard timeout** — backup timeout (default 1hr) in case Step Functions timeout doesn't fire
- **Proper exit codes**: 0 success, 1 failure, 124 timeout, 130 SIGTERM
- **DLQ on every SQS queue** — failed jobs land somewhere recoverable, not /dev/null
- **Visibility timeout = 6x expected job duration** — prevents duplicate processing
- **Idempotency at the handler level** — job handlers check a dedup key in DynamoDB before processing
- **Manifest as single source of truth** (SFN pattern) — the state machine reads `batches.json` from S3 and that file is the entire context for downstream tasks (the CloudMortgage 2026-01-10 lesson)
- **VPC endpoint for States** (SFN pattern) — Step Functions reachable from private subnets

## Step 3: Test

Submit one example job. Verify it lands in the worker, processes, and updates the database. If SFN, verify the state machine completes with status SUCCEEDED.

## Step 4: Completion

> Jobs installed ({{PATTERN}}).
>   - {{PATTERN_DETAIL}}
>   - Worker task definition: jobs-worker (1 vCPU, 2GB, Fargate Spot)
>   - SIGTERM handler: active (1hr hard timeout, graceful shutdown)
>   - DLQ: jobs-dlq (failed jobs land here)
>   - Submit via: backend/jobs/submit() helper
>   - Example job: backend/jobs/example_job.py (try it!)
> Cost: $0 idle. Pay only for worker minutes.
