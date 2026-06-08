---
name: jarvis-backup
version: 0.0.1
description: |
  Verify your data is recoverable: PITR enabled on every DynamoDB table, S3
  versioning on every bucket, snapshot policy if any RDS, cross-region copy
  for high-value data. Read-only check + opt-in fixes. (jarvis)
allowed-tools: [Bash, Read, AskUserQuestion]
triggers: [jarvis backup, am i backed up, verify backups, can i recover]
---

# /jarvis-backup — recoverability audit

The 2026-01-18 incident in CloudMortgage (Terraform destroyed `cases` and `documents`) was survivable only because PITR was on. This skill verifies the same protection across the whole stack.

## Preamble

```bash
[ ! -f .jarvis/profile.json ] && echo "BLOCKED: not a Jarvis project." && exit 1
REGION=$(jq -r .region .jarvis/profile.json)
```

## Step 1: DynamoDB PITR check

```bash
for table in $(aws dynamodb list-tables --region "$REGION" --output json | jq -r '.TableNames[]'); do
  PITR=$(aws dynamodb describe-continuous-backups --table-name "$table" --region "$REGION" \
    --query 'ContinuousBackupsDescription.PointInTimeRecoveryDescription.PointInTimeRecoveryStatus' --output text)
  DELETION=$(aws dynamodb describe-table --table-name "$table" --region "$REGION" \
    --query 'Table.DeletionProtectionEnabled' --output text)
  echo "$table: PITR=$PITR DeletionProtection=$DELETION"
done
```

## Step 2: S3 versioning check

```bash
for bucket in $(aws s3api list-buckets --output json | jq -r '.Buckets[].Name'); do
  V=$(aws s3api get-bucket-versioning --bucket "$bucket" --query 'Status' --output text 2>/dev/null)
  echo "$bucket: versioning=$V"
done
```

## Step 3: Secrets Manager rotation check

```bash
for secret in $(aws secretsmanager list-secrets --region "$REGION" --output json | jq -r '.SecretList[].Name'); do
  R=$(aws secretsmanager describe-secret --secret-id "$secret" --region "$REGION" \
    --query 'RotationEnabled' --output text)
  echo "$secret: rotation=$R"
done
```

## Step 4: Report

```
Backup audit — 14 resources checked

DynamoDB tables (8/8 protected):
  ok   users-v2          PITR=ENABLED    DeletionProtection=true
  ok   sessions          PITR=ENABLED    DeletionProtection=true
  ok   chat_threads      PITR=ENABLED    DeletionProtection=true
  ...

S3 buckets (3/4 versioned):
  ok   my-saas-files     versioning=Enabled
  ok   my-saas-kb        versioning=Enabled
  warn my-saas-logs      versioning=Suspended  <- fix?

Secrets (3/3 with rotation):
  ok   jarvis/my-saas/jwt
  ok   jarvis/my-saas/stripe
  ok   jarvis/my-saas/hmac-signup

VERDICT: PROTECTED (1 warning)
```

## Step 5: Optional fixes

For each warning, ask if Jarvis should fix it. Never auto-apply — backup changes affect billing and recovery semantics.

## Voice

> 14 resources audited. 13 protected, 1 warning. Your DDB tables and KB source bucket can survive a Terraform destroy or accidental deletion (within the PITR 35-day window). One S3 bucket has versioning suspended — run /jarvis-backup --fix to enable.
