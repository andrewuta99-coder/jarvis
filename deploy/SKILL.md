---
name: jarvis-deploy
version: 0.0.1
description: |
  Build Docker image, push to ECR, register new ECS task definition, rolling
  deploy to ECS, watch health checks, auto-rollback on failure. Same flow as
  the proven CloudMortgage deploy.sh, but parameterized for any Jarvis project. (jarvis)
allowed-tools: [Bash, Read, Edit, AskUserQuestion]
triggers:
  - jarvis deploy
  - ship it
  - push to prod
  - deploy now
---

# /jarvis-deploy — production deploy in one command

The proven CloudMortgage deploy flow, generalized. Builds for linux/amd64, tags with both `latest` and the git commit hash, drains old tasks gracefully (SIGTERM handlers from /jarvis-add-jobs), monitors the new tasks until healthy.

## Preamble

```bash
[ ! -f .jarvis/profile.json ] && echo "BLOCKED: not a Jarvis project." && exit 1
PROFILE=$(cat .jarvis/profile.json)
APP=$(echo "$PROFILE" | jq -r '.app_name')
REGION=$(echo "$PROFILE" | jq -r .region)
ACCOUNT=$(echo "$PROFILE" | jq -r .account)
echo "APP: $APP | REGION: $REGION | ACCOUNT: $ACCOUNT"

# Git clean check
if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
  echo "UNCOMMITTED: yes"
fi

# Test gate
if [ -f package.json ] && grep -q '"test"' package.json; then
  echo "HAS_TESTS: yes (npm test)"
elif [ -f pytest.ini ] || [ -f pyproject.toml ]; then
  echo "HAS_TESTS: yes (pytest)"
fi
```

## Step 1: Pre-flight

If `UNCOMMITTED: yes`, ask:

> You have uncommitted changes. Deploy them anyway, or commit first?
>   A) Commit first (recommended — gives you a hash to roll back to)
>   B) Deploy uncommitted (will tag image with "dirty-<short-hash>")
>   C) Cancel

If `HAS_TESTS: yes`, run them. If failing:

> Tests are failing. Deploying broken code to prod is rarely the right call.
>   A) Cancel and fix the tests (recommended)
>   B) Force deploy anyway (logs the override for the postmortem)

## Step 2: Build + push

```bash
# Build for linux/amd64 (ECS runs Linux, builders might be ARM Mac)
GIT_COMMIT=$(git rev-parse --short HEAD)
docker build --platform linux/amd64 -t "$APP" .

# Push to ECR
aws ecr get-login-password --region "$REGION" | \
  docker login --username AWS --password-stdin "$ACCOUNT.dkr.ecr.$REGION.amazonaws.com"

docker tag "$APP:latest" "$ACCOUNT.dkr.ecr.$REGION.amazonaws.com/$APP:latest"
docker tag "$APP:latest" "$ACCOUNT.dkr.ecr.$REGION.amazonaws.com/$APP:$GIT_COMMIT"
docker push "$ACCOUNT.dkr.ecr.$REGION.amazonaws.com/$APP:latest"
docker push "$ACCOUNT.dkr.ecr.$REGION.amazonaws.com/$APP:$GIT_COMMIT"
```

## Step 3: Register new task definition

```bash
# Pull current task def, swap image, register new revision
aws ecs describe-task-definition --task-definition "$APP-api" --region "$REGION" \
  --query 'taskDefinition' > /tmp/task-def.json

jq --arg IMG "$ACCOUNT.dkr.ecr.$REGION.amazonaws.com/$APP:$GIT_COMMIT" \
  'del(.taskDefinitionArn, .revision, .status, .requiresAttributes, .compatibilities, .registeredAt, .registeredBy) | .containerDefinitions[0].image = $IMG' \
  /tmp/task-def.json > /tmp/task-def-new.json

NEW_ARN=$(aws ecs register-task-definition \
  --cli-input-json file:///tmp/task-def-new.json \
  --region "$REGION" --query 'taskDefinition.taskDefinitionArn' --output text)
echo "NEW_TASK_DEF: $NEW_ARN"
```

## Step 4: Rolling deploy

```bash
aws ecs update-service \
  --cluster "$APP-cluster" \
  --service "$APP-api-service" \
  --task-definition "$NEW_ARN" \
  --region "$REGION" \
  --force-new-deployment >/dev/null

# Watch deployment
echo "Watching rollout..."
aws ecs wait services-stable \
  --cluster "$APP-cluster" \
  --services "$APP-api-service" \
  --region "$REGION" || ROLLBACK_NEEDED=1
```

## Step 5: Auto-rollback if needed

If rollout didn't stabilize in 10 minutes:

```bash
# Get previous task def
PREV=$(aws ecs describe-services --cluster "$APP-cluster" \
  --services "$APP-api-service" --region "$REGION" \
  --query 'services[0].deployments[?status==`PRIMARY`][taskDefinition]' --output text)

aws ecs update-service --cluster "$APP-cluster" --service "$APP-api-service" \
  --task-definition "$PREV" --region "$REGION" --force-new-deployment >/dev/null
echo "ROLLED_BACK_TO: $PREV"
```

Surface the failure mode (CloudWatch logs from the failed tasks) so the user can diagnose.

## Step 6: Smoke test

```bash
DOMAIN=$(jq -r '.domain // .default_domain' .jarvis/profile.json)
curl -sf "https://$DOMAIN/api/health" >/dev/null && echo "HEALTH: ok" || echo "HEALTH: failed"
```

## Step 7: Completion

> Deployed.
>   - Image:        {{APP}}:{{GIT_COMMIT}}
>   - Task def:     revision {{REV}}
>   - Rollout time: {{SECONDS}}s
>   - Health check: ok
>   - URL:          https://{{DOMAIN}}
>
> Rollback: /jarvis-rollback (one command to the previous revision)

Log to `.jarvis/deploys.jsonl` for audit history.
