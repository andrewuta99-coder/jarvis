---
name: jarvis-add-realtime
version: 0.0.1
description: |
  Add WebSocket-based real-time messaging: API Gateway WebSockets, DynamoDB
  connections table, broadcast helper, frontend hook. Idle cost is zero; pay
  per connection-minute. (jarvis)
allowed-tools: [Bash, Read, Write, Edit, AskUserQuestion]
triggers:
  - jarvis add realtime
  - add websockets
  - real-time updates
  - add live
---

# /jarvis-add-realtime — WebSockets in one command

API Gateway WebSockets + DynamoDB connections table is the AWS-native pattern. Cheaper than maintaining a long-lived ECS service for connections. Scales to thousands of concurrent connections without thought.

## Preamble

```bash
[ ! -f .jarvis/profile.json ] && echo "BLOCKED: not a Jarvis project." && exit 1
```

## Cost projection

> About to add: Real-time (API Gateway WebSockets + DynamoDB connections)
> Cost projection:
>   Idle:                          +$0/mo
>   1M connection-minutes/mo:      +$0.25/mo
>   1M messages/mo:                +$1.00/mo
>   Connections table:             $0 idle (DDB pay-per-request)
> Proceed?

## Step 1: Spawn the API specialist with realtime flag

writes_glob:
- `iac/apigateway/websocket.tf`
- `iac/dynamodb/ws_connections.tf` — connection_id PK, TTL on disconnect
- `iac/lambda/ws_*.tf` — $connect, $disconnect, $default handlers
- `iac/iam/realtime_policy.tf`
- `backend/realtime/broadcast.py` — server-side helper to push to all connected clients
- `frontend/src/realtime/useRealtime.{js,ts}` — React hook to subscribe
- `tests/integration/test_realtime.py`

## Invisible rails

- **TTL on connections table** — orphan connections (network drops without a clean disconnect) auto-expire after 1 hour
- **Connect handler validates JWT** — only authenticated users can open WebSockets
- **Per-tenant filtering** — broadcast helper scopes to tenantId so users only see their own org's events
- **Reconnect logic** in frontend hook — exponential backoff, max 30s between retries
- **CloudWatch metric**: active_connections gauge — visible from `/jarvis-doctor`

## Step 2: Test

Open two WebSocket connections from the test suite. Broadcast a message. Verify both receive it. Disconnect one. Broadcast again. Verify only the remaining one receives.

## Step 3: Completion

> Real-time installed.
>   - WebSocket endpoint: wss://{{API_ID}}.execute-api.{{REGION}}.amazonaws.com/prod
>   - Connections table: ws_connections (TTL on, JWT-validated)
>   - 3 Lambda handlers: $connect, $disconnect, $default
>   - Broadcast helper: backend/realtime/broadcast.py
>   - Frontend hook: useRealtime() — subscribe + send in one line
> Cost: $0 idle. ~$1.25 per million messages.
