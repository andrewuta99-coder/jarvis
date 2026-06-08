---
name: jarvis-add-files
version: 0.0.1
description: |
  Add file uploads to your Jarvis-managed AWS app: S3 bucket (public-block,
  versioning, lifecycle to IA at 30d, KMS encryption), presigned URL backend
  routes, frontend upload widget, and the IAM policy. Optional virus-scan hook.
  Cost: ~$0 idle. (jarvis)
allowed-tools: [Bash, Read, Write, Edit, AskUserQuestion]
triggers:
  - jarvis add files
  - add file upload
  - let users upload
  - add s3
---

# /jarvis-add-files — file uploads in one command

Adds an S3 bucket with presigned-URL upload pattern. Public-block defaults on. Versioning on. Lifecycle to Infrequent Access at 30 days. The "files" feature that doesn't accidentally make your bucket public.

## Preamble

```bash
[ ! -f .jarvis/profile.json ] && echo "BLOCKED: not a Jarvis project. Run /jarvis-init first." && exit 1
BACKEND=$(jq -r .backend .jarvis/profile.json)
FRONTEND=$(jq -r .frontend .jarvis/profile.json)
echo "BACKEND: $BACKEND | FRONTEND: $FRONTEND"
```

## Cost projection

> About to add: File uploads (S3 bucket + presigned URLs + frontend widget)
> Cost projection:
>   Idle:               +$0/mo
>   100 GB stored:      +$2.30/mo (Standard) / +$1.25/mo (IA after 30d)
>   100k PUT/mo:        +$0.50/mo
>   100k GET/mo:        +$0.04/mo
> Proceed?

## Step 1: Ask once — what's the use case?

This determines which optional defaults ship:

Options:
- A) User-uploaded content (avatars, attachments) — public-read NO, presigned-GET YES (recommended)
- B) Static assets (images, CSS shipped with the app) — CloudFront in front, public-read via OAC
- C) Private documents (PII, legal) — encryption with customer-managed KMS key, no public access ever

## Step 2: Spawn the specialist

Internally this calls the Data specialist with a `files` feature flag (not a separate agent — the Data agent owns S3).

writes_glob:
- `iac/storage/files_bucket.tf`
- `iac/iam/files_policy.tf`
- `backend/files/*.py` (or .ts/.js)
- `frontend/src/files/UploadWidget.{jsx,tsx}` (if frontend in stack)
- `tests/integration/test_files.py`

## Invisible rails

- `block_public_acls = true`, `block_public_policy = true`, `ignore_public_acls = true`, `restrict_public_buckets = true` — all four. Default S3 public-block IS NOT enough; you need this exact combination.
- Versioning on (saves you from "I accidentally deleted production user data")
- Lifecycle rule: transition to S3-IA at 30 days, Glacier at 180 days
- KMS encryption at rest (option C uses customer-managed key)
- Presigned URLs expire in 15 minutes (PUT) / 1 hour (GET)
- Multipart upload supported for files > 5 MB
- CORS rules scoped to the user's ALB / Amplify domain only — not `*`

## Step 3: Test

Run integration test: backend issues a presigned PUT, frontend uploads a 1KB blob, backend issues a presigned GET, file downloads correctly.

## Step 4: Completion

> Files installed.
>   - Bucket: my-saas-12abc-files (public-block ON, versioning ON, KMS encrypted)
>   - Lifecycle: Standard -> IA at 30d -> Glacier at 180d
>   - 4 routes added: /files/presign-upload, /files/presign-download, /files/list, /files/delete
>   - Frontend: <UploadWidget /> component ready to import
> Cost: $0 idle. ~$2-5/mo at 100 GB stored + 100k operations.
