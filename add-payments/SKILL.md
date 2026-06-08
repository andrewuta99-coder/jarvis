---
name: jarvis-add-payments
version: 0.0.1
description: |
  Add Stripe payments: customer + subscription + checkout + webhook handler,
  idempotency table (prevents double-charging on retries), Secrets Manager
  for the webhook signing secret, and the IAM policy. Customer portal wired
  in. (jarvis)
allowed-tools: [Bash, Read, Write, Edit, AskUserQuestion]
triggers:
  - jarvis add payments
  - add stripe
  - accept payments
  - add billing
---

# /jarvis-add-payments — Stripe in one command

The 2026-01-11 double-charge incident from CloudMortgage is permanently solved: an idempotency table guards every credit-charging endpoint. The webhook signing secret is in Secrets Manager from day one (not in env vars).

## Preamble

```bash
[ ! -f .jarvis/profile.json ] && echo "BLOCKED: not a Jarvis project." && exit 1
BACKEND=$(jq -r .backend .jarvis/profile.json)
DOMAIN=$(jq -r '.domain // ""' .jarvis/profile.json)
echo "BACKEND: $BACKEND | DOMAIN: $DOMAIN"
```

## Cost projection

> About to add: Stripe payments (customer + subscription + webhook + idempotency)
> Cost projection:
>   Idle:               +$0/mo
>   Per transaction:    Stripe takes 2.9% + $0.30 (AWS cost is $0)
>   Idempotency table:  +$0/mo (DynamoDB pay-per-request)
> Proceed?

## Step 1: Stripe API keys

Ask the user to paste their Stripe keys. Two modes:

Options:
- A) I have a Stripe account (paste publishable + secret + webhook keys)
- B) I'll set up Stripe later — generate the code, I'll fill in the keys
- C) Use Stripe test mode keys for now (recommended for first install)

If A or C, take the keys via secure input (do NOT echo) and write them to Secrets Manager:

```bash
aws secretsmanager create-secret \
  --name jarvis/{{APP_NAME}}/stripe \
  --secret-string '{"publishable_key":"...","secret_key":"...","webhook_secret":""}'
```

(The webhook signing secret is filled in after Step 3 when we register the webhook.)

## Step 2: Spawn the Payments specialist

writes_glob:
- `iac/dynamodb/billing.tf` — customers + subscriptions
- `iac/dynamodb/idempotency.tf` — request_id -> response cache, 24h TTL
- `iac/secrets/stripe.tf` — Secrets Manager secret reference
- `iac/iam/payments_policy.tf` — scoped to billing + idempotency tables + the secret
- `backend/payments/*.py` — Stripe client, webhook handler, idempotency middleware
- `frontend/src/billing/*` — pricing page, checkout button, customer portal link
- `tests/integration/test_payments.py`

## Step 3: Register webhook

After backend deploys, register the webhook with Stripe (uses the user's Stripe secret key):

```bash
stripe webhook_endpoints create \
  --url "https://{{DOMAIN}}/api/payments/webhook" \
  --enabled-events "checkout.session.completed,customer.subscription.created,customer.subscription.updated,customer.subscription.deleted,invoice.payment_succeeded,invoice.payment_failed"
```

Stripe returns a signing secret. Write it into the Secrets Manager secret:

```bash
aws secretsmanager update-secret --secret-id jarvis/{{APP_NAME}}/stripe \
  --secret-string '{... existing keys ..., "webhook_secret":"whsec_..."}'
```

## Invisible rails

- **Idempotency table**: every credit-charging endpoint checks for existing PENDING/RUNNING executions for the same request_id before charging. The 2026-01-11 double-deduction bug cannot happen.
- **Webhook signature verification**: every webhook request verified with Stripe SDK's constant-time check before any DB write
- **Idempotency-Key header**: passed to Stripe on every create call — Stripe's own retry-safety
- **Secrets in Secrets Manager**: not env vars. Rotation supported.
- **Customer portal pre-configured**: subscription management UI link generated from the API
- **Pricing page**: 3-tier template (free/pro/business) — user can edit
- **Test card preloaded**: `4242 4242 4242 4242` works out of the box in test mode

## Step 4: Test

Run integration test: create a test customer, create a checkout session, simulate webhook (stripe trigger), verify subscription record. If all four pass, payments are wired.

## Step 5: Completion

> Payments installed.
>   - Stripe customer + subscription tables: created
>   - Idempotency table: 24h TTL (prevents double-charges)
>   - Webhook endpoint: https://{{DOMAIN}}/api/payments/webhook (registered with Stripe)
>   - Webhook signing secret: stored in Secrets Manager
>   - Customer portal: GET /api/billing/portal returns the Stripe-hosted URL
>   - Frontend: <PricingTable /> and <CheckoutButton /> ready
> Cost: $0/mo AWS. Stripe fees apply per transaction.
