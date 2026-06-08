---
name: jarvis-rollback
version: 0.0.1
description: |
  Revert to the previous ECS task definition (the previous deploy). One
  command. Reads .jarvis/deploys.jsonl to find the prior revision. (jarvis)
allowed-tools: [Bash, Read, AskUserQuestion]
triggers: [jarvis rollback, revert deploy, undo deploy]
---

# /jarvis-rollback — one-command revert

Same flow as the proven CloudMortgage rollback. Pull the previous task def from the deploy log, force ECS to use it, wait for stability.

## Preamble

```bash
[ ! -f .jarvis/profile.json ] && echo "BLOCKED: not a Jarvis project." && exit 1
[ ! -f .jarvis/deploys.jsonl ] && echo "BLOCKED: no deploy history (run /jarvis-deploy first)." && exit 1

LAST=$(tail -1 .jarvis/deploys.jsonl | jq -r .task_definition_arn)
PREV=$(tail -2 .jarvis/deploys.jsonl | head -1 | jq -r .task_definition_arn)
echo "CURRENT: $LAST"
echo "PREVIOUS: $PREV"
```

If only one deploy in history, halt with `BLOCKED: nothing to roll back to`.

## Step 1: Confirm

> Rollback to:
>   {{PREV}}
>   ({{PREV_GIT_COMMIT}}, deployed {{PREV_AGO}} ago)
>
> Current:
>   {{LAST}}
>   ({{LAST_GIT_COMMIT}}, deployed {{LAST_AGO}} ago)
>
> Continue?

## Step 2: Apply

```bash
APP=$(jq -r .app_name .jarvis/profile.json)
REGION=$(jq -r .region .jarvis/profile.json)

aws ecs update-service \
  --cluster "$APP-cluster" \
  --service "$APP-api-service" \
  --task-definition "$PREV" \
  --region "$REGION" \
  --force-new-deployment >/dev/null

aws ecs wait services-stable \
  --cluster "$APP-cluster" \
  --services "$APP-api-service" \
  --region "$REGION"
```

## Step 3: Smoke test

```bash
DOMAIN=$(jq -r '.domain // .default_domain' .jarvis/profile.json)
curl -fsS "https://$DOMAIN/api/health" && echo "HEALTH: ok"
```

## Step 4: Log + completion

Append the rollback to `.jarvis/deploys.jsonl`:

```json
{"event":"rollback","from":"{{LAST}}","to":"{{PREV}}","ts":"..."}
```

> Rolled back to {{PREV_GIT_COMMIT}} in {{SECONDS}}s. Health check OK.
> Note: this only rolls back the ECS task definition. If the prior deploy
> required different Terraform state (rare), use `terraform apply` on the
> matching git revision instead.
