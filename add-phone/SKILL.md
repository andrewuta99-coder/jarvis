---
name: jarvis-add-phone
version: 0.0.1
description: |
  Add outbound phone calls + AI screening of inbound calls via Amazon Connect.
  Includes one DID phone number, contact flow, queue, agent assignment, and
  Bedrock-powered transcription. (jarvis)
allowed-tools: [Bash, Read, Write, Edit, AskUserQuestion]
triggers:
  - jarvis add phone
  - phone calls
  - add voice
  - add connect
  - ai phone screening
---

# /jarvis-add-phone — phone calls in one command

Amazon Connect is the AWS-native way to do voice. The CloudMortgage AI inbound screening pattern (2026-04-04) is the default for inbound: AI receptionist screens for intent, routes qualified calls.

## Preamble

```bash
[ ! -f .jarvis/profile.json ] && echo "BLOCKED: not a Jarvis project." && exit 1
REGION=$(jq -r .region .jarvis/profile.json)
# Connect is only in certain regions
case "$REGION" in
  us-east-1|us-west-2|eu-west-2|ap-southeast-2|ap-northeast-1|ca-central-1|eu-central-1|af-south-1)
    echo "CONNECT_REGION: ok" ;;
  *)
    echo "BLOCKED: Amazon Connect not available in $REGION. Pick us-east-1 or us-west-2." && exit 1 ;;
esac
```

## Cost projection

> About to add: Amazon Connect (outbound + inbound AI screening)
> Cost projection:
>   Phone number (DID):     +$30/mo
>   Outbound (US toll):     ~$0.013/min (caller leg) + $0.018/min (called leg)
>   Inbound (US toll-free): ~$0.018/min received + AI screening $0.017/30s
>   Connect platform:       $0 idle, $0.018/min active calls
>
> 1000 minutes outbound:  ~$31/mo (number + minutes)
> 1000 minutes inbound:   ~$48/mo (number + minutes + AI)
> Proceed?

## Step 1: Phone number

Connect provisions a number; the user picks an area code:

Options:
- A) US toll-free (recommended for inbound)
- B) Pick a specific area code (e.g., 415, 212, 713)
- C) Skip — set up later, just provision the Connect instance

## Step 2: Spawn the Phone specialist (uses Backend specialist with phone flag)

writes_glob:
- `iac/connect/instance.tf`
- `iac/connect/contact_flow_outbound.tf`
- `iac/connect/contact_flow_inbound_ai.tf` — AI screening flow
- `iac/connect/queue.tf`
- `iac/dynamodb/calls.tf` — call records with transcript pointer
- `iac/iam/connect_policy.tf`
- `iac/networking/vpc_endpoint_connect.tf`     <- invisible rail
- `backend/phone/*.py` — initiate call, end call, transcript fetch
- `lambda/inbound_screening/handler.py` — Bedrock-powered AI screening
- `tests/integration/test_phone.py`

## Invisible rails

- **VPC endpoint for Connect** — outbound call initiation works from private subnets
- **Real-time transcription via Contact Lens** — every call transcribed automatically
- **AI screening Lambda for inbound** — Nova Lite screens caller intent, routes qualified leads, sends "we'll call back" for unqualified — saves agents 60-80% of pickup time
- **Call records in DynamoDB** with TTL of 2 years (compliance default)
- **Outbound rate limit** — per-day cap to prevent runaway dialing (configurable, default 1000/day)

## Step 3: Test

Initiate a test call to the user's own phone via the API. Confirm it rings. Transcript should be retrievable within 60 seconds.

## Step 4: Completion

> Phone installed.
>   - Connect instance: {{INSTANCE_ID}}
>   - Phone number: {{PHONE}}
>   - Contact flows: outbound, inbound-ai-screening
>   - AI screening: Nova Lite (~$0.017 per 30-sec screening)
>   - Outbound API: POST /api/phone/call
>   - Transcript API: GET /api/phone/call/{id}/transcript
> Cost: $30/mo for number + per-minute usage.
