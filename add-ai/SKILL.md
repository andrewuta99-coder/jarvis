---
name: jarvis-add-ai
version: 0.0.1
description: |
  Add an AI chatbot / agent powered by AWS Bedrock. Includes Bedrock Agent +
  Knowledge Base + OpenSearch Serverless + S3 source bucket + VPC endpoints
  (Bedrock, AOSS) + multi-model IAM wildcard (so you can switch Nova/Claude
  freely). Chat endpoint wired into your backend. (jarvis)
allowed-tools: [Bash, Read, Write, Edit, AskUserQuestion]
triggers:
  - jarvis add ai
  - add chatbot
  - add bedrock
  - add ai agent
  - add chat
---

# /jarvis-add-ai — Bedrock chatbot in one command

The 2026-01-16 Bedrock-agent IAM lesson is baked in: the agent role has `bedrock:InvokeModel` with a wildcard across Nova (Pro/Lite/Micro) and Claude models so the user can swap models freely without redeploying IAM. The 2026-01-16 OpenSearch Serverless permission gap is also fixed — `aoss:BatchGetCollection` is on the ECS task role from day one.

## Preamble

```bash
[ ! -f .jarvis/profile.json ] && echo "BLOCKED: not a Jarvis project." && exit 1
REGION=$(jq -r .region .jarvis/profile.json)
echo "REGION: $REGION"

# Bedrock model access check
MODELS=$(aws bedrock list-foundation-models --region "$REGION" --output json 2>/dev/null | jq -r '.modelSummaries[] | select(.modelId | startswith("amazon.nova") or startswith("anthropic.claude")) | .modelId' | wc -l | tr -d ' ')
echo "BEDROCK_MODELS_AVAILABLE: $MODELS"
```

## Cost projection

> About to add: Bedrock Agent + Knowledge Base + OpenSearch Serverless
> Cost projection:
>   Idle:               +$50/mo  (OpenSearch Serverless minimum: 2 OCU index + 2 OCU search)
>   1k chats/mo:        +$5/mo   (Nova Lite: ~$0.005/chat)
>   10k chats/mo:       +$50/mo
>   100k chats/mo:      +$500/mo
>
> Note: OpenSearch Serverless has a minimum spend. If you want to skip the KB
> (just chat, no docs), the cost drops to ~$0 idle.
>
> Options:
>   A) Full setup with Knowledge Base (recommended for document-aware chatbot)
>   B) Chat only — no KB (cheaper, just LLM chat)
> Proceed?

## Step 1: Model picker

Ask which model is the default (user can swap later):

Options:
- A) Amazon Nova Lite — fastest, cheapest, good for most chat (recommended)
- B) Amazon Nova Pro — better reasoning, more expensive
- C) Anthropic Claude Haiku — Anthropic-flavored, cheap
- D) Anthropic Claude Sonnet — strongest, expensive

Note: the IAM allows ALL of these. The user picks the default but can change in code without redeploying IAM.

## Step 2: Bedrock model access check

If `BEDROCK_MODELS_AVAILABLE: 0`, the user hasn't enabled model access yet. Tell them:

> Bedrock model access is a one-time per-region toggle. Open this URL and enable Nova + Claude:
> https://console.aws.amazon.com/bedrock/home?region={{REGION}}#/modelaccess
>
> Click "Modify model access" → check Nova Pro/Lite/Micro and all Claude models → Submit.
> Approval is instant. Re-run /jarvis-add-ai when done.

Halt with `NEEDS_CONTEXT`.

## Step 3: Spawn the AI specialist

writes_glob:
- `iac/bedrock/agent.tf` — Bedrock Agent definition
- `iac/bedrock/knowledge_base.tf` — KB pointing at S3 source bucket
- `iac/storage/kb_source_bucket.tf` — versioned, encrypted
- `iac/opensearch/collection.tf` — OpenSearch Serverless vector collection
- `iac/networking/vpc_endpoint_bedrock.tf`        <- invisible rail
- `iac/networking/vpc_endpoint_aoss.tf`           <- invisible rail
- `iac/iam/bedrock_agent_role.tf` — multi-model wildcard
- `iac/iam/ai_task_policy.tf` — aoss:BatchGetCollection on ECS task role
- `backend/ai/*.py` — chat client, agent invoke, KB query
- `tests/integration/test_ai.py`

## Invisible rails

- Multi-model IAM: `bedrock:InvokeModel` on `arn:aws:bedrock:*::foundation-model/amazon.nova-*` AND `anthropic.claude-*` (wildcards). Swap models in code without re-deploying IAM.
- VPC endpoint for `com.amazonaws.{region}.bedrock-agent-runtime` — chat works from private subnets
- VPC endpoint for `com.amazonaws.{region}.aoss` — knowledge-base queries work from private subnets
- ECS task role has `aoss:BatchGetCollection` — without this, the "Starting up AI knowledge base..." loading state never resolves (the 2026-01-16 bug)
- OpenSearch collection: Vector type, encryption at rest, IAM data-access policy scoped to agent role + task role only
- KB source bucket: versioning ON, encryption ON, prefix `kb/` for sync target
- Agent prepared and prepared-version published — KB syncs run on a daily schedule (EventBridge)

## Step 4: Test

Hit `/api/chat` with "hello" — expect a model response in <3s. Hit `/api/chat/kb-test` with a query against a seeded document. Both must pass for the feature to report `DONE`.

## Step 5: Completion

> AI installed.
>   - Bedrock Agent: agent-xxx, prepared version v1
>   - Knowledge Base: kb-xxx, pointing at s3://my-saas-12abc-kb/kb/
>   - OpenSearch collection: ai-xxx (vector, encrypted)
>   - VPC endpoints: bedrock-agent-runtime, aoss (both private-subnet-reachable)
>   - IAM: multi-model wildcard active (swap models freely)
>   - Chat endpoint: POST /api/chat
> Cost: $50/mo idle (OpenSearch minimum) + ~$0.005/chat
