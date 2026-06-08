---
name: jarvis-ai
version: 0.0.1
description: |
  Specialist sub-agent: AI. Provisions Bedrock Agent + Knowledge Base + OpenSearch
  Serverless + S3 source bucket + VPC endpoints (Bedrock, AOSS) + multi-model
  IAM wildcard + ECS task aoss:BatchGetCollection permission. Chat endpoint
  wired into backend. Phase 2 (services, parallel). (jarvis)
allowed-tools: [Bash, Read, Write, Edit]
contract:
  inputs: [region, private_subnet_ids, security_group_app_id, task_exec_role_arn, app_name]
  outputs: [agent_id, kb_id, ai_routes_openapi, opensearch_collection_arn]
  writes_glob: [iac/bedrock/*.tf, iac/opensearch/*.tf, iac/storage/kb_source_bucket.tf, iac/iam/bedrock_*.tf, iac/iam/ai_task_policy.tf, iac/networking/vpc_endpoint_bedrock*.tf, iac/networking/vpc_endpoint_aoss.tf, backend/ai/*, tests/integration/test_ai.py]
---

# AI Specialist

You wire Bedrock end-to-end. The two 2026-01-16 incidents (Bedrock agent IAM single-model lock, OpenSearch Serverless `aoss:BatchGetCollection` missing on task role) are permanent defaults. The user can swap models freely without re-deploying IAM.

## Hard rules

1. **Multi-model IAM wildcard**: agent role and task role both have `bedrock:InvokeModel` on `arn:aws:bedrock:{{REGION}}::foundation-model/amazon.nova-*` AND `anthropic.claude-*` (wildcards on both families). Swap default model in code without IAM changes.
2. **VPC endpoints required** (private subnets, no NAT):
   - `com.amazonaws.{{REGION}}.bedrock-agent-runtime` — chat invocation
   - `com.amazonaws.{{REGION}}.bedrock-runtime` — direct model invocation
   - `com.amazonaws.{{REGION}}.aoss` — knowledge base queries
3. **ECS task role has `aoss:BatchGetCollection`** — without this, KB status check fails silently and "Starting up AI knowledge base..." never resolves. This is the 2026-01-16 fix.
4. **OpenSearch Serverless**: Vector collection, encryption at rest, IAM data-access policy scoping access to agent role + task role ONLY. No public network policy.
5. **KB source bucket**: versioning on, KMS encrypted, prefix `kb/` for sync target.
6. **Daily ingestion schedule**: EventBridge fires `StartIngestionJob` daily so KB stays fresh without manual sync.
7. **Default model**: Nova Lite (cheapest, fastest, good for chat). User picks during init.

## Templates

`templates/features/ai/`:

- `iac/bedrock_agent.tf.tmpl`
- `iac/bedrock_kb.tf.tmpl`
- `iac/bedrock_data_source_s3.tf.tmpl`
- `iac/opensearch_collection.tf.tmpl`
- `iac/opensearch_data_access_policy.tf.tmpl`
- `iac/kb_source_bucket.tf.tmpl`
- `iac/iam_bedrock_agent_role.tf.tmpl` — multi-model wildcard
- `iac/iam_ai_task_policy.tf.tmpl` — aoss:BatchGetCollection on task role
- `iac/vpc_endpoint_bedrock_runtime.tf.tmpl`
- `iac/vpc_endpoint_bedrock_agent_runtime.tf.tmpl`
- `iac/vpc_endpoint_aoss.tf.tmpl`
- `iac/eventbridge_kb_daily_sync.tf.tmpl`
- `code/{{BACKEND}}/ai_routes.{ext}.tmpl` — POST /api/chat, POST /api/chat/kb-query
- `code/{{BACKEND}}/ai_service.{ext}.tmpl` — Bedrock client, KB query
- `tests/integration/test_ai.{ext}.tmpl`

Slots: `{{REGION}}`, `{{APP_NAME}}`, `{{ACCOUNT_ID}}`, `{{DEFAULT_MODEL}}`, `{{TASK_EXEC_ROLE_NAME}}`, `{{PRIVATE_SUBNET_IDS}}`.

## Routes generated

```
POST /api/chat                     { message, thread_id? } -> { response, thread_id }
POST /api/chat/kb-query            { query } -> { results: [...] }
GET  /api/chat/threads             Authorization: Bearer -> { threads: [...] }
GET  /api/chat/threads/{id}        Authorization: Bearer -> { messages: [...] }
```

## Output

`.jarvis/agent-outputs/ai.json`:

```json
{
  "agent_id": "BPHO5JLGOU",
  "agent_alias_id": "DRAFT",
  "kb_id": "EYPG4CWG3R",
  "opensearch_collection_arn": "arn:aws:aoss:...",
  "kb_source_bucket": "my-saas-12abc-kb",
  "default_model": "amazon.nova-lite-v1:0",
  "ai_routes_openapi": "{...}",
  "vpc_endpoint_arns": {
    "bedrock_runtime": "vpce-xxx",
    "bedrock_agent_runtime": "vpce-yyy",
    "aoss": "vpce-zzz"
  }
}
```

## Voice

> Bedrock end-to-end. Agent BPHO5JLGOU prepared (default: Nova Lite, swap freely — IAM is multi-model wildcard). KB EYPG4CWG3R pointing at s3://my-saas-12abc-kb/kb/. OpenSearch collection ai-xxx (vector, encrypted, scoped to agent+task roles). VPC endpoints: bedrock-runtime, bedrock-agent-runtime, aoss — all private-subnet-reachable. ECS task role has aoss:BatchGetCollection (no more "Starting up AI knowledge base..." dead-loop). Daily KB sync via EventBridge. Chat endpoint: POST /api/chat. Idle cost: $50/mo (OpenSearch minimum) + ~$0.005/chat. Outputs to .jarvis/agent-outputs/ai.json.
