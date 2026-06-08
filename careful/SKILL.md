---
name: jarvis-careful
version: 0.0.1
description: |
  Safety mode. Warns before any destructive AWS or Terraform operation:
  terraform destroy, ECS service delete, DynamoDB delete-table, S3 rm,
  bucket-empty, force-push. User overrides each warning. (jarvis)
allowed-tools: [Bash, Read, AskUserQuestion]
triggers: [jarvis careful, be careful, safety mode, careful mode]
---

# /jarvis-careful — safety guardrails on

Activate the destructive-command guard for AWS + Terraform.

## Activation

```bash
~/.claude/skills/jarvis/bin/jarvis-config set careful_mode true
```

While active, every Bash invocation that matches a destructive pattern triggers an AskUserQuestion before execution.

## Guarded patterns

| Pattern | Why |
|---|---|
| `terraform destroy` | Destroys infra |
| `terraform apply` with `Plan: 0 to add, N to destroy` | Apply with destroys |
| `aws ecs update-service --desired-count 0` | Stops the app |
| `aws ecs delete-service` | Removes the service |
| `aws ecs delete-cluster` | Removes the cluster |
| `aws dynamodb delete-table` | Wipes a table (PITR can recover within 35 days, but the table itself is gone) |
| `aws s3 rm --recursive` | Bulk delete |
| `aws s3api delete-bucket` | Removes a bucket |
| `aws iam delete-role` | Removes a role (breaks anything trusting it) |
| `aws bedrock-agent delete-agent` | Removes the AI agent |
| `git push --force` | Overwrites remote |
| `git reset --hard` (against origin/main) | Local destructive |
| `rm -rf` (against absolute paths) | Filesystem destructive |

## Prompt shape

When a guarded command is detected:

> About to run: {{COMMAND}}
> Why this is destructive: {{REASON}}
> Recoverable? {{YES/NO/PARTIALLY — DDB has PITR, etc.}}
>
> Options:
>   A) Cancel
>   B) Run it (one-time override)
>   C) Run and remember (this exact command for this session)

## Deactivate

```bash
~/.claude/skills/jarvis/bin/jarvis-config set careful_mode false
```

## Companion: /jarvis-freeze

Restricts edits to a single directory. Combine both with /jarvis-guard for maximum safety when debugging prod.
